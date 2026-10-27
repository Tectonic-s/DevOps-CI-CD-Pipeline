pipeline {
    agent any

    environment {
        PATH              = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
        APP_NAME          = 'movie-recommender'
        DOCKER_REGISTRY   = 'docker.io'
        DOCKER_TAG        = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        DOCKER_CREDS_ID   = 'dockerhub-credentials'
        ANSIBLE_CREDS_ID  = 'ansible-ssh-key'
    }

    parameters {
        choice(name: 'DEPLOY_ENV', choices: ['local', 'staging', 'production'], description: 'Deployment Target Environment')
        string(name: 'DOCKER_USER', defaultValue: 'your-dockerhub-user', description: 'Docker Hub Username / Organization')
        booleanParam(name: 'PUSH_IMAGE', defaultValue: false, description: 'Push image to Docker registry? (Requires dockerhub-credentials)')
        booleanParam(name: 'RUN_ANSIBLE', defaultValue: false, description: 'Trigger Ansible deployment to remote staging/production?')
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
                echo "Running automated test suite with pytest..."
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
                    docker build -t ${APP_NAME}:latest -t ${APP_NAME}:${DOCKER_TAG} .
                '''
            }
        }

        stage('Deploy Local Container & Healthcheck') {
            when {
                expression { return !params.RUN_ANSIBLE }
            }
            steps {
                echo "Deploying container locally and running health probe..."
                sh '''
                    docker stop cinematch_app >/dev/null 2>&1 || true
                    docker rm cinematch_app >/dev/null 2>&1 || true
                    docker run -d --name cinematch_app -p 5001:5001 ${APP_NAME}:latest
                    sleep 4
                    curl -f http://127.0.0.1:5001/health
                    echo ""
                    echo "=========================================================="
                    echo "🎉 CineMatch AI is LIVE and Healthy on http://localhost:5001"
                    echo "=========================================================="
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
                        FULL_IMAGE="${DOCKER_REGISTRY}/${params.DOCKER_USER}/${APP_NAME}"
                        docker tag ${APP_NAME}:latest ${FULL_IMAGE}:latest
                        docker tag ${APP_NAME}:${DOCKER_TAG} ${FULL_IMAGE}:${DOCKER_TAG}
                        echo "$REGISTRY_PASS" | docker login ${DOCKER_REGISTRY} -u "$REGISTRY_USER" --password-stdin
                        docker push ${FULL_IMAGE}:${DOCKER_TAG}
                        docker push ${FULL_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy via Ansible') {
            when {
                expression { return params.RUN_ANSIBLE }
            }
            steps {
                echo "Triggering Ansible CD Deployment to [${params.DEPLOY_ENV}]..."
                withCredentials([sshUserPrivateKey(credentialsId: "${ANSIBLE_CREDS_ID}", keyFileVariable: 'ANSIBLE_KEY', usernameVariable: 'ANSIBLE_USER')]) {
                    sh '''
                        FULL_IMAGE="${DOCKER_REGISTRY}/${params.DOCKER_USER}/${APP_NAME}"
                        ansible-playbook -i ansible/inventory.ini ansible/deploy.yml \
                            -u $ANSIBLE_USER \
                            --private-key $ANSIBLE_KEY \
                            -e "target_env=${params.DEPLOY_ENV}" \
                            -e "docker_image=${FULL_IMAGE}" \
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
            echo "🎉 Pipeline finished successfully! CineMatch AI is live on http://localhost:5001"
        }
        failure {
            echo "❌ Pipeline failed! Please inspect stage logs above."
        }
        cleanup {
            sh '''
                rm -rf .ci_venv reports
            '''
        }
    }
}
