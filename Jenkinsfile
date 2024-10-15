pipeline {
    agent any

    environment {
        WORKSPACE = pwd()
        SQLDB_URL="sqlite+aiosqlite:///./test-data/test-sqlalchemy.db"
        SECRET_KEY = "Fkhlt19/j2p73aOdZ2aPR6NBulnyfSmlMpJpom5nVzA"
    }

    stages {
        stage('Code') {
            steps {
                git branch: 'main', url: 'https://github.com/chayodom-khruesuk/Co-table-application.git'
            }
        }

        stage('Test') {
            agent {
                docker {
                    image 'python:3.11.9'
                    reuseNode true
                    args '-u root'
                }
            }
            steps {

                sh "pip install poetry"
                sh "poetry install" 

                sh "poetry run pytest -v"
            }
        }

    }
}