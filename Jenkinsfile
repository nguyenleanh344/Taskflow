pipeline {
    agent any

    stages {
        stage('Install') {
            steps {
                sh 'python3 -m venv venv'
                sh './venv/bin/pip install -e .[dev]'
            }
        }

        stage('Lint') {
            steps {
                sh './venv/bin/ruff check .'
                sh './venv/bin/ruff format --check .'
            }
        }

        stage('Test') {
            steps {
                sh './venv/bin/pytest -q'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t taskflow-api:latest .'
            }
        }
    }
}