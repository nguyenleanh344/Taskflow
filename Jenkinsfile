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
                sh './venv/bin/pytest -q tests --ignore=tests/integration'
            }
        }

        stage('Integration Test') {
            steps {
                sh 'docker compose -p taskflow-ci -f docker-compose.ci.yml up --build --abort-on-container-exit --exit-code-from test test'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t taskflow-api:latest .'
            }
        }

    }

    post {
        always {
            sh 'docker compose -p taskflow-ci -f docker-compose.ci.yml down -v --remove-orphans || true'
        }
    }
}
