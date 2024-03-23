

pipeline {
    
    agent any

    environment {
        IMAGE_TAG = "${BUILD_NUMBER}"    
        def dockerImage = 'gurmindersingh5/flask'
    }
    stages {

        stage('git-checkout') {
          steps {
              echo 'checkout already done, passed'
            // git credentialsId: '4c20f28a-13c3-4fd4-b676-bf1848df738b',
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
                         sh "DOCKER_BUILDKIT=1 docker build -t ${dockerImage}:${BUILD_NUMBER} ."
                         //sh "docker run -d -p 8000:8000 --name ${dockerImage} ${dockerImage}:${BUILD_NUMBER}"
                         //sh 'docker ps'
                     }
                }
        }

         stage('Push the artifacts to docker hub') {
             steps {             
                     script {
                            sh "echo 'pushing the artifacts to repo'"
                            sh "docker push ${dockerImage}:${BUILD_NUMBER}"
                     }
                }
        }

        stage('checkout kubernetes manifest SCM') {
             steps {             
                     script {
                        git credentialsId: '4c20f28a-13c3-4fd4-b676-bf1848df738b',
                        url: 'https://github.com/gurmindersingh5/CICD_kubernetes.git',
                        branch: 'main'
                     }
                }
        }
        
         stage('update k8s manifest and push to git') {
             steps {             
                     script {
                        withCredentials([gitUsernamePassword(credentialsId: 'gitsecret', gitToolName: 'Default')]) {
                            sh '''
                                cd Deploy
                                sed -i "s/v[^[:space:]]*/${BUILD_NUMBER}/g" deploy.yml
                                git add deploy.yml
                                git commit -m 'Updated the deploy yml | Jenkins Pipeline'
                                git remote -v
                                git config --global user.email "gurminder.barca@gmail.com"
                                git config --global user.name "gurmindersingh5"
                                git push https://github.com/gurmindersingh5/CICD_kubernetes.git HEAD:main
                            '''
                        }
                    }
                }
        }

        
    }
}

        
//         

//         stage('build python app continer') {
            
//             steps {             
//                 sh '''
//                     echo 'trying to run docker on agenet machine'
//                     '''
//                     //docker run hello-world
                 

//             }
//         }

        
//     }
// }


// // pipeline {
// //     agent any


// //     stages {
// //         stage ('git checkout') {
// //             steps {
// //                 echo 'Checking out the git repo' 
// //                 // git branch: 'main', url: 'https://github.com/gurmindersingh5/localflaskapp.git'
// //             }
// //         }
        
// //         stage('pre-build test') {
            
// //             environment {
// //                 SONAR_HOST_URL = "http://3.99.154.7:9000"
// //                 SONAR_TOKEN = credentials('jenkins-integration') 
// //                 SONAR_PROJECT_KEY = 'testflask' 
// //                 }
// //             steps {
// //                 sh 'python3 --version'
// //                 // withSonarQubeEnv('My SonarQube Server', envOnly: true) {
// //                 //   // This expands the evironment variables SONAR_CONFIG_NAME, SONAR_HOST_URL, SONAR_AUTH_TOKEN that can be used by any script.
// //                 //   println "${env.SONAR_HOST_URL}"
// //                 //   }
// //                 sh('sonar-scanner -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.sources=. -Dsonar.host.url=${SONAR_HOST_URL} -Dsonar.login=${SONAR_TOKEN}')
// //             }
// //         }
// //     }

// // }
//notes:
// install java, jenkins, docker.io, docker-buildx
// sudo usermod -aG docker jenkins ,(optional: docker ubuntu), systemctl restart docker
// install docker and docker pipeline in jenkins website.
// good to go for pipeline execution
