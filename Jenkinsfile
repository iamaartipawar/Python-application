pipeline {

    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        TARGET_IP = '3.90.146.164'
        CRED_ID   = 'ec2-target-key'
        APP_DIR   = '/home/ec2-user/python-static-site'
    }

    stages {

        // ============================================================
        // 1. CHECKOUT APPLICATION CODE
        // ============================================================
        stage('Checkout') {
            steps {
                echo 'Cloning Python application...'

                git branch: 'main',
                    url: 'https://github.com/iamaartipawar/Python-application'
            }
        }

        // ============================================================
        // 2. INSTALL PYTHON AND PIP ON JENKINS SERVER
        // ============================================================
        stage('Install Python') {
            steps {
                sh '''
                    echo "Installing Python and pip..."

                    sudo yum install -y python3 python3-pip

                    echo "Python version:"
                    python3 --version

                    echo "Pip version:"
                    python3 -m pip --version
                '''
            }
        }

        // ============================================================
        // 3. CREATE VIRTUAL ENVIRONMENT ON JENKINS
        // ============================================================
        stage('Create Virtual Environment') {
            steps {
                sh '''
                    echo "Creating Python virtual environment..."

                    rm -rf venv

                    python3 -m venv venv

                    echo "Virtual environment Python:"
                    ./venv/bin/python --version

                    echo "Virtual environment pip:"
                    ./venv/bin/python -m pip --version
                '''
            }
        }

        // ============================================================
        // 4. INSTALL APPLICATION DEPENDENCIES ON JENKINS
        // ============================================================
        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "Installing Python dependencies..."

                    ./venv/bin/python -m pip install --upgrade pip

                    ./venv/bin/python -m pip install -r requirements.txt

                    echo "Dependencies installed successfully."
                '''
            }
        }

        // ============================================================
        // 5. BUILD / VALIDATE APPLICATION
        // ============================================================
        stage('Build / Validate') {
            steps {
                sh '''
                    echo "Validating Python application..."

                    ./venv/bin/python -m py_compile app.py

                    echo "Python application validation successful."
                '''
            }
        }

        // ============================================================
        // 6. COPY APPLICATION TO TARGET SERVER
        // ============================================================
        stage('Deploy to Target Server') {
            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${CRED_ID}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    sh '''
                        echo "Creating application directory on target server..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            "$SSH_USER@$TARGET_IP" \
                            "mkdir -p '$APP_DIR'"

                        echo "Copying application files..."

                        scp -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -r app.py requirements.txt templates static \
                            "$SSH_USER@$TARGET_IP:$APP_DIR/"

                        echo "Application copied successfully."
                    '''
                }
            }
        }

        // ============================================================
        // 7. SETUP PYTHON APPLICATION ON TARGET SERVER
        // ============================================================
        stage('Setup Application on Target') {
            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${CRED_ID}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    sh '''
                        echo "Setting up Python application on target server..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            "$SSH_USER@$TARGET_IP" "

                            echo 'Installing Python...'

                            sudo yum install -y python3

                            cd '$APP_DIR'

                            echo 'Removing old virtual environment...'

                            rm -rf venv

                            echo 'Creating new virtual environment...'

                            python3 -m venv venv

                            echo 'Installing Python dependencies...'

                            ./venv/bin/python -m pip install --upgrade pip

                            ./venv/bin/python -m pip install -r requirements.txt

                            echo 'Python dependencies installed successfully.'
                        "
                    '''
                }
            }
        }

        // ============================================================
        // 8. START APPLICATION WITH GUNICORN
        // ============================================================
        stage('Start Application') {
            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${CRED_ID}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    sh '''
                        echo "Starting Python application..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            "$SSH_USER@$TARGET_IP" "

                            cd '$APP_DIR'

                            echo 'Checking existing Gunicorn process...'

                            if [ -f gunicorn.pid ]; then

                                OLD_PID=\\$(cat gunicorn.pid)

                                if kill -0 \\$OLD_PID 2>/dev/null; then
                                    echo 'Stopping existing Gunicorn process...'

                                    kill \\$OLD_PID

                                    sleep 3
                                else
                                    echo 'Old Gunicorn process is not running.'
                                fi

                                rm -f gunicorn.pid

                            else
                                echo 'No existing Gunicorn PID file found.'
                            fi

                            echo 'Starting Gunicorn...'

                            nohup ./venv/bin/gunicorn \
                                --bind 0.0.0.0:5000 \
                                --workers 2 \
                                --pid gunicorn.pid \
                                app:app \
                                > app.log 2>&1 < /dev/null &

                            sleep 3

                            echo 'Checking Gunicorn process...'

                            if [ -f gunicorn.pid ]; then

                                NEW_PID=\\$(cat gunicorn.pid)

                                if kill -0 \\$NEW_PID 2>/dev/null; then
                                    echo 'Gunicorn started successfully.'
                                    echo "Gunicorn PID: \\$NEW_PID"
                                else
                                    echo 'ERROR: Gunicorn failed to start.'
                                    cat app.log
                                    exit 1
                                fi

                            else
                                echo 'ERROR: Gunicorn PID file was not created.'
                                cat app.log
                                exit 1
                            fi

                            echo 'Checking port 5000...'

                            if ss -lnt | grep -q ':5000'; then
                                echo 'Port 5000 is listening.'
                            else
                                echo 'ERROR: Port 5000 is not listening.'
                                cat app.log
                                exit 1
                            fi

                            echo 'Application log:'

                            tail -20 app.log || true

                            echo 'Application started successfully.'
                        "
                    '''
                }
            }
        }

        // ============================================================
        // 9. VERIFY APPLICATION
        // ============================================================
        stage('Verify Application') {
            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${CRED_ID}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    sh '''
                        echo "Verifying application..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            "$SSH_USER@$TARGET_IP" "

                            echo 'Testing health endpoint...'

                            curl -f http://localhost:5000/health

                            echo ''

                            echo 'Application is running successfully.'
                        "
                    '''
                }
            }
        }
    }

    // ================================================================
    // POST ACTIONS
    // ================================================================
    post {

        success {
            echo 'Python application deployed successfully!'
        }

        failure {
            echo 'Python application deployment failed.'
        }

        always {
            echo 'Jenkins pipeline execution completed.'
        }
    }
}
