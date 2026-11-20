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

                            .venv/bin/python -m pytest \\
                                -v \\
                                --color=no \\
                                --junitxml=reports/pytest-results.xml \\
                                py_test/tests/ 2>&1 | tee artifacts/pytest-output.log
                        '''
                    )

                    // Save the test status for the final pipeline result.
                    env.PYTEST_STATUS = testStatus.toString()
                }
            }
        }

        stage('Generate Screenshot') {
            steps {
                sh '''
                    .venv/bin/python scripts/create_terminal_screenshot.py \
                        --input artifacts/pytest-output.log \
                        --output artifacts/pytest-screenshot.png
                '''
            }
        }

        stage('Validate Test Result') {
            steps {
                script {
                    if (env.PYTEST_STATUS != '0') {
                        error("Pytest execution failed. Exit code: ${env.PYTEST_STATUS}")
                    }

                    echo 'All pytest tests passed.'
                }
            }
        }
    }

    post {
        always {
            echo 'Publishing test execution artifacts...'

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