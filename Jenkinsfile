pipeline {
    agent any

    environment {
        PATH              = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
        APP_NAME          = 'movie-recommender'
        DOCKER_REGISTRY   = 'docker.io'
        DOCKER_IMAGE      = "${DOCKER_REGISTRY}/your-dockerhub-user/${APP_NAME}"
        DOCKER_TAG        = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        DOCKER_CREDS_ID   = 'dockerhub-credentials'   // Jenkins Credential ID for Docker Registry
        ANSIBLE_CREDS_ID  = 'ansible-ssh-key'         // Jenkins Credential ID for Ansible deployment SSH key
    }

    parameters {
        choice(name: 'DEPLOY_ENV', choices: ['staging', 'production'], description: 'Deployment Environment')
        string(name: 'DOCKER_USER', defaultValue: 'your-dockerhub-user', description: 'Docker Hub Username / Organization')
        booleanParam(name: 'PUSH_IMAGE', defaultValue: false, description: 'Push image to Docker registry? (Requires dockerhub-credentials)')
        booleanParam(name: 'RUN_DEPLOY', defaultValue: false, description: 'Trigger Ansible deployment stage after build?')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo "Checking out CineMatch AI source code..."
                checkout scm
            }
        }

        stage('Lint & Unit Tests') {
            steps {
                echo "Setting up Python virtual environment and running test suite..."
                sh '''
                    python3 -m venv .ci_venv
                    . .ci_venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    mkdir -p reports
                    pytest -v tests/ --junitxml=reports/test-results.xml
                '''
            }
            post {
                always {
                    junit testResults: 'reports/test-results.xml', allowEmptyResults: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker container image..."
                sh '''
                    IMAGE="${DOCKER_REGISTRY}/${params.DOCKER_USER}/${APP_NAME}"
                    docker build -t ${APP_NAME}:latest -t ${IMAGE}:${DOCKER_TAG} -t ${IMAGE}:latest .
                '''
            }
        }

        stage('Push Docker Image') {
            when {
                expression { return params.PUSH_IMAGE }
            }
            steps {
                echo "Authenticating and pushing image to registry..."
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDS_ID}", usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_PASS')]) {
                    sh '''
                        IMAGE="${DOCKER_REGISTRY}/${params.DOCKER_USER}/${APP_NAME}"
                        echo "$REGISTRY_PASS" | docker login ${DOCKER_REGISTRY} -u "$REGISTRY_USER" --password-stdin
                        docker push ${IMAGE}:${DOCKER_TAG}
                        docker push ${IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy via Ansible') {
            when {
                expression { return params.RUN_DEPLOY }
            }
            steps {
                echo "Triggering Ansible CD Deployment to [${params.DEPLOY_ENV}]..."
                withCredentials([sshUserPrivateKey(credentialsId: "${ANSIBLE_CREDS_ID}", keyFileVariable: 'ANSIBLE_KEY', usernameVariable: 'ANSIBLE_USER')]) {
                    sh '''
                        IMAGE="${DOCKER_REGISTRY}/${params.DOCKER_USER}/${APP_NAME}"
                        ansible-playbook -i ansible/inventory.ini ansible/deploy.yml \
                            -u $ANSIBLE_USER \
                            --private-key $ANSIBLE_KEY \
                            -e "target_env=${params.DEPLOY_ENV}" \
                            -e "docker_image=${IMAGE}" \
                            -e "docker_tag=${DOCKER_TAG}" \
                            -e "container_port=5001" \
                            -e "host_port=5001"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline finished successfully! CineMatch AI is live on ${params.DEPLOY_ENV}."
        }
        failure {
            echo "❌ Pipeline failed! Please inspect stage logs above."
        }
        cleanup {
            sh '''
                rm -rf .ci_venv reports
                docker image prune -f || true
            '''
        }
    }
}
