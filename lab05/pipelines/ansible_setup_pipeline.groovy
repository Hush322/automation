pipeline {
    agent { label 'ansible-agent' }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Hush322/automation.git',
                    branch: 'lab05'
            }
        }

        stage('Check Connection') {
            steps {
                dir('lab05/ansible') {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: 'ansible-server-key',
                        keyFileVariable: 'SERVER_KEY')]) {
                        sh 'ansible test_servers -m ping --private-key "$SERVER_KEY"'
                    }
                }
            }
        }

        stage('Run Ansible Playbook') {
            steps {
                dir('lab05/ansible') {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: 'ansible-server-key',
                        keyFileVariable: 'SERVER_KEY')]) {
                        sh 'ansible-playbook setup_test_server.yml --private-key "$SERVER_KEY"'
                    }
                }
            }
        }
    }

    post {
        success { echo 'Serverul de test a fost configurat.' }
        failure { echo 'Configurarea serverului de test a esuat.' }
    }
}
