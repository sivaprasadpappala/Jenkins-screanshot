
pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Prepare Environment') {
            steps {
                sh '''
                    set -e

                    mkdir -p artifacts reports

                    python3 -m venv .venv

                    .venv/bin/pip install --upgrade pip
                    .venv/bin/pip install pytest -r requirements-screenshot.txt
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                script {
                    int testStatus = sh(
                        returnStatus: true,
                        script: '''#!/bin/bash
                            set -o pipefail

                            .venv/bin/python -m pytest \
                                -v \
                                --color=no \
                                --junitxml=reports/pytest-results.xml \
                                py_test/tests/ 2>&1 | tee artifacts/pytest-output.log
                        '''
                    )

                    env.PYTEST_STATUS = testStatus.toString()
                }
            }
        }

        stage('Capture Kubernetes Nodes') {
            steps {
                script {
                    int kubectlStatus = sh(
                        returnStatus: true,
                        script: '''#!/bin/bash
                            set -o pipefail

                            export KUBECONFIG=/var/lib/jenkins/.kube/config

                            {
                                echo "$ kubectl get nodes -o wide"
                                /var/lib/rancher/rke2/bin/kubectl get nodes -o wide
                            } 2>&1 | tee artifacts/kubectl-nodes-output.log
                        '''
                    )

                    env.KUBECTL_STATUS = kubectlStatus.toString()
                }
            }
        }

        stage('Generate Screenshots') {
            steps {
                sh '''
                    .venv/bin/python scripts/create_terminal_screenshot.py \
                        --input artifacts/pytest-output.log \
                        --output artifacts/pytest-screenshot.png

                    .venv/bin/python scripts/create_terminal_screenshot.py \
                        --input artifacts/kubectl-nodes-output.log \
                        --output artifacts/kubectl-nodes-screenshot.png
                '''
            }
        }

        stage('Validate Execution Results') {
            steps {
                script {
                    if (env.PYTEST_STATUS != '0') {
                        error("Pytest execution failed. Exit code: ${env.PYTEST_STATUS}")
                    }

                    if (env.KUBECTL_STATUS != '0') {
                        error("Kubectl command failed. Exit code: ${env.KUBECTL_STATUS}")
                    }

                    echo 'Pytest and Kubernetes node checks completed successfully.'
                }
            }
        }
    }

    post {
        always {
            echo 'Publishing execution artifacts...'

            junit(
                testResults: 'reports/pytest-results.xml',
                allowEmptyResults: true
            )

            archiveArtifacts(
                artifacts: 'artifacts/**, reports/**',
                allowEmptyArchive: true
            )
        }
    }
}
