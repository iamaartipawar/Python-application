pipeline {
    agent any

    environment {
        TARGET_IP   = '32.197.54.30'
        CRED_ID     = 'ec2-target-key'
        TARGET_USER = 'ec2-user'
        APP_DIR     = '/home/ec2-user/python-app'
        PORT        = '5000'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/iamaartipawar/Python-application.git'
            }
        }

        stage('Install System Python') {
            steps {
                sh '''
                    echo "Checking Python3..."

                    if ! command -v python3 >/dev/null 2>&1; then
                        echo "Python3 not found. Installing..."
                        sudo yum install -y python3
                    else
                        echo "Python3 already installed."
                        python3 --version
                    fi
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    echo "Creating virtual environment..."

                    rm -rf .venv
                    python3 -m venv .venv

                    echo "Upgrading pip..."
                    .venv/bin/python -m pip install --upgrade pip

                    echo "Installing application dependencies..."
                    .venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    echo "Testing Flask application..."

                    .venv/bin/python -c "from app import app; client = app.test_client(); response = client.get('/'); print('HTTP Status:', response.status_code); assert response.status_code == 200; print('Flask application test passed successfully.')"
                '''
            }
        }

        stage('Deploy') {
            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${CRED_ID}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    sh '''
                        echo "Connecting to target server: ${TARGET_IP}"

                        echo "Creating application directory..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            ${SSH_USER}@${TARGET_IP} \
                            "mkdir -p ${APP_DIR}"

                        echo "Copying application files..."

                        scp -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            app.py requirements.txt \
                            ${SSH_USER}@${TARGET_IP}:${APP_DIR}/

                        scp -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -r templates static \
                            ${SSH_USER}@${TARGET_IP}:${APP_DIR}/

                        echo "Installing Python3 on target server..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            ${SSH_USER}@${TARGET_IP} \
                            "sudo yum install -y python3"

                        echo "Creating virtual environment..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            ${SSH_USER}@${TARGET_IP} \
                            "cd ${APP_DIR} && \
                             rm -rf .venv && \
                             python3 -m venv .venv"

                        echo "Installing application dependencies on target..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            ${SSH_USER}@${TARGET_IP} \
                            "cd ${APP_DIR} && \
                             .venv/bin/python -m pip install --upgrade pip && \
                             .venv/bin/python -m pip install -r requirements.txt"

                        echo "Stopping old application..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            ${SSH_USER}@${TARGET_IP} \
                            "sudo fuser -k ${PORT}/tcp 2>/dev/null || true"

                        echo "Starting application..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            ${SSH_USER}@${TARGET_IP} \
                            "cd ${APP_DIR} && \
                             nohup .venv/bin/python app.py > app.log 2>&1 < /dev/null &"

                        sleep 5

                        echo "Checking deployed application..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            ${SSH_USER}@${TARGET_IP} \
                            "curl -I http://localhost:${PORT}/"

                        echo "======================================"
                        echo "DEPLOYMENT SUCCESSFUL"
                        echo "======================================"
                    '''
                }
            }
        }
    }
}
