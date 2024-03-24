

pipeline {
    
    agent any

    environment { 
        IMAGE_TAG = "${BUILD_NUMBER}"    
        def dockerImage = 'gurmindersingh5/flask'
           //USER_CREDENTIALS = credentials('pat')
    }
    
    stages {


        // stage('Print Credentials') {
        //     steps {
        //            // echo "Credentials: ${USER_CREDENTIALS}"
        //             echo "Username: ${USERNAME}"
        //             echo "Password: ${PASSWORD}"
        //         }
        //     }

        
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
                 def gitToken = credentials('pat')

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


        
        //  stage('update k8s manifest and push to git') {
        //      steps {             
        //         script {
        //             withCredentials([gitUsernamePassword(credentialsId: 'pat', gitToolName: 'git-tool')]) {
        //                 sh '''
        //                         cd Deploy
        //                         sed -i "s/ver[^[:space:]]*/ver${BUILD_NUMBER}/g" deploy.yml
        //                         git add deploy.yml
        //                         git status
        //                         git commit -m 'Updated the deploy yml | Jenkins Pipeline'
        //                         git remote -v
        //                         echo 'made it to here'
        //                         git push https://github.com/gurmindersingh5/CICD_Kubernetes HEAD:main

        //                     '''    
                        
        //             }
        //             }
        //         }
        // }

        
    }
}

        

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
