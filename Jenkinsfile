pipeline {
    agent any

    tools {
        jdk 'JDK17'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/ishanO9/badminton-academy.git'
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

        stage('OWASP Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '''
                    --scan .
                    --format HTML
                    --out reports
                ''',
                odcInstallation: 'OWASP-DC'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t badminton_academy .'
            }
        }

        
        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"

                    bat "docker tag badminton_academy %DOCKER_USER%/badminton_academy:latest"

                    bat "docker push %DOCKER_USER%/badminton_academy:latest"
                }
            }
        }
        

        /*stage('Deploy Container') {
            steps {
                bat 'docker stop badminton_app || ver > nul'
                bat 'docker rm badminton_app || ver > nul'
                bat 'docker run -d --name badminton_app -p 5000:5000 badminton_academy'
            }
        }*/

    }
}