pipeline {
    agent any

    tools {
        jdk 'JDK17'
    }

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
        stage('OWASP Dependency Check')  {
            steps {
                dependencyCheck additionalArguments: '''
                    --scan .
                    --format HTML
                    --out reports
                ''', odcInstallation: 'OWASP-DC'
            }
        }
    }


}