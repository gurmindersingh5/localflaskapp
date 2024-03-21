pipeline {
    agent {
        docker { image 'pyimage' }
    }
    
    stages {
        stage('SCM') {
            steps {
                checkout scm
            }
        }
        stage('git-checkout') {
          steps {
            git credentialsId: '4c20f28a-13c3-4fd4-b676-bf1848df738b',
            url: 'https://github.com/gurmindersingh5/localflaskapp',
            branch: 'main'
          }
        }
        
        // stage('SonarQube Analysis') {
            
        //     steps {             
        //         script {
        //             def scannerHome = tool 'sonar-scanner';
        //             withSonarQubeEnv() {
        //                 sh "${scannerHome}/bin/sonar-scanner \
        //                     -Dsonar.projectKey='testflask' \
        //                     -Dsonar.sources=./flask_pkg"
        //                     }
        //                 }
        //             }
        //         }

        stage('build python app continer') {
            
            steps {             
                sh '''
                    echo 'trying to run docker on agenet machine'
                    '''
                    //docker run hello-world
                 

            }
        }

        
    }
}


// pipeline {
//     agent any


//     stages {
//         stage ('git checkout') {
//             steps {
//                 echo 'Checking out the git repo' 
//                 // git branch: 'main', url: 'https://github.com/gurmindersingh5/localflaskapp.git'
//             }
//         }
        
//         stage('pre-build test') {
            
//             environment {
//                 SONAR_HOST_URL = "http://3.99.154.7:9000"
//                 SONAR_TOKEN = credentials('jenkins-integration') 
//                 SONAR_PROJECT_KEY = 'testflask' 
//                 }
//             steps {
//                 sh 'python3 --version'
//                 // withSonarQubeEnv('My SonarQube Server', envOnly: true) {
//                 //   // This expands the evironment variables SONAR_CONFIG_NAME, SONAR_HOST_URL, SONAR_AUTH_TOKEN that can be used by any script.
//                 //   println "${env.SONAR_HOST_URL}"
//                 //   }
//                 sh('sonar-scanner -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.sources=. -Dsonar.host.url=${SONAR_HOST_URL} -Dsonar.login=${SONAR_TOKEN}')
//             }
//         }
//     }

// }
