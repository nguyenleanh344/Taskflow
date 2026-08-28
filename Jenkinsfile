pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment') {
            steps {
                sh 'pwd'
                sh 'ls -la'
                sh 'git --version'
            }
        }
    }
}