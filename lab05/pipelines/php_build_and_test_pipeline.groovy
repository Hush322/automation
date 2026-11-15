pipeline {
    agent { label 'php-agent' }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Hush322/php-price-calculator.git',
                    branch: 'main'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'composer install --no-interaction --prefer-dist'
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    mkdir -p build
                    ./vendor/bin/phpunit --testdox --log-junit build/junit.xml
                '''
            }
        }
    }

    post {
        always {
            // Raportarea rezultatelor testelor
            junit allowEmptyResults: true, testResults: 'build/junit.xml'
        }
        success {
            echo 'Build si teste finalizate cu succes.'
        }
        failure {
            echo 'Build-ul sau testele au esuat.'
        }
    }
}
