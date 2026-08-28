pipeline {
    agent any

    stages {
        stage('Install') {
            steps {
                sh 'python3 -m venv venv'
                sh "./venv/bin/pip install -e '.[dev]'"
            }
        }

        stage('Lint') {
            steps {
                sh './venv/bin/ruff check .'
                sh './venv/bin/ruff format --check .'
            }
        }

        stage('Unit Test') {
            steps {
                sh './venv/bin/pytest -q tests --ignore=tests/integration --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml'
            }
        }

        stage('Check Docker') {
            steps {
                sh 'docker version'
                sh 'docker compose version'
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set +x
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USERNAME" \
                            --password-stdin
                    '''
                }
            }
        }

        stage('Integration Test') {
            steps {
                sh 'docker compose -p taskflow-ci -f docker-compose.ci.yml up --build --abort-on-container-exit --exit-code-from test test'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t taskflow-api:${BUILD_NUMBER} -t taskflow-api:latest .'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set +x
                        IMAGE="$DOCKERHUB_USERNAME/taskflow-api"
                        echo "$DOCKERHUB_TOKEN" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                        docker tag "taskflow-api:$BUILD_NUMBER" "$IMAGE:$BUILD_NUMBER"
                        docker tag taskflow-api:latest "$IMAGE:latest"
                        docker push "$IMAGE:$BUILD_NUMBER"
                        docker push "$IMAGE:latest"
                        docker logout
                    '''
                }
            }
        }

    }

    post {
        always {
            archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
            sh 'docker compose -p taskflow-ci -f docker-compose.ci.yml down -v --remove-orphans || true'
            sh 'docker logout || true'
        }
    }
}
