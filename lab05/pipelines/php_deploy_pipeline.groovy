pipeline {
    agent { label 'ansible-agent' }

    stages {
        stage('Checkout PHP Project') {
            steps {
                dir('php-app') {
                    git url: 'https://github.com/Hush322/php-price-calculator.git',
                        branch: 'main'
                }
            }
        }

        stage('Checkout Ansible Playbooks') {
            steps {
                dir('automation') {
                    git url: 'https://github.com/Hush322/automation.git',
                        branch: 'lab05'
                }
            }
        }

        stage('Deploy to Test Server') {
            steps {
                dir('automation/lab05/ansible') {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: 'ansible-server-key',
                        keyFileVariable: 'SERVER_KEY')]) {
                        sh '''
                            ansible-playbook deploy_php.yml \
                              --private-key "$SERVER_KEY" \
                              -e project_dir="$WORKSPACE/php-app"
                        '''
                    }
                }
            }
        }
    }

    post {
        success { echo 'Aplicatia este disponibila la http://localhost:8081' }
        failure { echo 'Deploy-ul a esuat.' }
    }
}
