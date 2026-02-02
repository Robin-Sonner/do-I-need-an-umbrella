pipeline {
    agent any

    environment {
        PYTHON_HOME = 'C:\\Users\\Robin\\AppData\\Local\\Python\\pythoncore-3.14-64'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Hello') {
            steps {
                echo 'Hello World'
            }
        }

        stage('Setup') {
            steps {
                powershell '''
                    & "$env:PYTHON_HOME\\python.exe" --version
                    & "$env:PYTHON_HOME\\python.exe" -m venv venv
                    .\\venv\\Scripts\\Activate.ps1
                    pip install -e .[dev]
                '''
            }
        }
    }

        
    post {
        always {
            step([
                $class: 'GitHubCommitStatusSetter',
                reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/Robin-Sonner/laughing-octo-guide'],
                contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: 'continuous-integration/jenkins'],
                errorHandlers: [[$class: 'ChangingBuildStatusErrorHandler', result: 'UNSTABLE']],
                statusResultSource: [ $class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: message('Build'), state: state()]] ]
            ])
            cleanWs()
        }
        success {
            echo 'Pipeline completed sucessfully'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}

// Helper functions for status messages
@NonCPS
def message(prefix) {
    def result = currentBuild.result ?: 'SUCCESS'
    return "${prefix} ${result.toLowerCase()}"
}

@NonCPS
def state() {
    def result = currentBuild.result ?: 'SUCCESS'
    if (result == 'SUCCESS') {
        return 'SUCCESS'
    } else if (result == 'UNSTABLE') {
        return 'FAILURE'
    } else {
        return 'FAILURE'
    }
}

