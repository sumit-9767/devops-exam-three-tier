pipeline{
    agent any
    environment {
        SCANNER_HOME = tool 'sonar-scanner'
    }
    stages{
        stage('Checkout'){
            steps{
                git branch:'main', url:'https://github.com/sumit-9767/devops-exam-three-tier.git'
            }
        }
        stage('Sonarqube Ananlysis'){
             steps{
                    withSonarQubeEnv('sonar') {
                        sh '''
                            $SCANNER_HOME/bin/sonar-scanner \
                            -Dsonar.projectName=Devops-exam \
                            -Dsonar.projectKey=Devops-exam
                        '''
                        
                    }
             }
         }
        stage('Docker compose Verify'){
            steps{
                sh 'docker-compose --version'
            }
        }
        // stage('BUILD Images'){
        //     steps{
                
        //     }
        // }
        // stage('Trivy'){
        //     steps{
                
        //     }
        // }
        // stage('Push Images'){
        //     steps{
                
        //     }
        //}
    }
}
