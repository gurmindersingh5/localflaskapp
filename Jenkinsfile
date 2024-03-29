

pipeline {
    
    agent any

    environment { 
        IMAGE_TAG = "${BUILD_NUMBER}"    
        def dockerImage = 'gurmindersingh5/flask'
        def gitToken = credentials('pat')
    }
    
    stages {
        
        stage('git-checkout') {
          steps {
              echo 'checkout already done, passed'
            // git credentialsId: '',
            // url: 'https://github.com/gurmindersingh5/localflaskapp',
            // branch: 'main'
          }
        }
        
        // stage('pre-build SonarQube Analysis') {
        //      steps {             
        //          script {
        //              def scannerHome = tool 'sonar-scanner';
        //              withSonarQubeEnv() {
        //                  sh "${scannerHome}/bin/sonar-scanner \
        //                      -Dsonar.projectKey='testflask' \
        //                      -Dsonar.sources=./flask_pkg"
        //                      }
        //                  }
        //         }
        // }

        
        stage('Build using docker') {
             steps {             
                     script {
                         sh "DOCKER_BUILDKIT=1 docker build -t ${dockerImage}:ver${BUILD_NUMBER} ."
                         //sh "docker run -d -p 8000:8000 --name ${dockerImage} ${dockerImage}:${BUILD_NUMBER}"
                         //sh 'docker ps'
                     }
                }
        }

         stage('Push the artifacts to docker hub') {
             steps {             
                     script {
                            sh "echo 'pushing the artifacts to repo'"
                            sh "docker push ${dockerImage}:ver${BUILD_NUMBER}"
                     }
                }
        }

        stage('checkout kubernetes manifest SCM') {
             steps {             
                     script {
                        git credentialsId: '',
                        url: 'https://github.com/gurmindersingh5/CICD_kubernetes.git',
                        branch: 'main'
                     }
                }
        }

       stage('update k8s manifest and push to git') {
                            
        steps {

            script { 
                sh '''
                    cd Deploy
                    sed -i "s/ver[^[:space:]]*/ver${BUILD_NUMBER}/g" deploy.yml
                    git add deploy.yml
                    git status
                    git commit -m 'Updated the deploy yml | Jenkins Pipeline'
                    git remote -v
                    echo 'made it to here'
                    git push https://gurmindersingh5:${gitToken}@github.com/gurmindersingh5/CICD_Kubernetes HEAD:main
                '''
                }
            }
        }
    
 
    }
}
        
      
// notes:
// install java, jenkins, docker.io, docker-buildx
// sudo usermod -aG docker jenkins ,(optional: docker ubuntu), systemctl restart docker
// install docker and docker pipeline in jenkins website.
// good to go for pipeline execution
