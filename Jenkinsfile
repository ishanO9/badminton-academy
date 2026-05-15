pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ishanO9/badminton-academy.git'
            }
        }
        stage('Test') {
            steps {
                echo 'Jenkinsfile is working'
            }
        }
        stage('SonarCloud Analysis') {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    bat "${tool 'SonarScanner'}\\bin\\sonar-scanner.bat"
                }
            }
        }
    }


}