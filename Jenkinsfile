pipeline {
    agent any

    environment {
        PYTHON_HOME = 'C:\\Users\\Robin\\AppData\\Local\\Python\\pythoncore-3.14-64'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // Get the commit message
                    def commitMessage = powershell(
                        returnStdout: true,
                        script: 'git log -1 --pretty=%B'
                    ).trim()

                    // Check if commit message contains "release vX.Y.Z"
                    def releasePattern = ~/release\s+(v\d+\.\d+\.\d+)/
                    def matcher = commitMessage =~ releasePattern

                    if (matcher.find()) {
                        env.IS_RELEASE = 'true'
                        env.GIT_TAG = matcher.group(1)
                        echo "Buidling Release ${env.GIT_TAG}"
                    } else {
                        env.IS_RELEASE = 'false'
                        env.GIT_TAG = ''
                        echo "Building regular commit (no release)"
                    }
                }
            }
        }

        stage('Create Tag') {
            when {
                expression { env.IS_RELEASE == 'true' }
            }
            steps {
                script {
                    def tagName = env.GIT_TAG
                    withCredentials([
                        string(credentialsId: 'JenkinsGitHubToken', variable: 'GH_TOKEN')
                    ]) {
                        powershell """
                            git config --local credential.helper "!f() { echo username=x-access-token; echo password=%GH_TOKEN%; }; f"
                            git tag ${tagName}
                            git push origin ${tagName}
                        """
                    }
                }
            }
        }

        stage('Setup') {
            steps {
                powershell """
                    & "\$env:PYTHON_HOME\\python.exe" --version
                    & "\$env:PYTHON_HOME\\python.exe" -m venv venv
                    .\\venv\\Scripts\\Activate.ps1
                    pip install -e .[dev]
                """
            }
        }

        stage('Linting') {
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    flake8 . --extend-ignore=E501 --exclude=.\\venv
                """
            }
        }

        stage('Format Check') {
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    black --check .
                    isort --check-only .
                """
            }
        }

        stage('Unit Tests') {
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    python -m unittest discover -s tests -p "*_test.py" -v
                """
            }
        }

        stage('Build Release') {
            when {
                expression { env.IS_RELEASE == 'true' }
            }
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    pip install pyinstaller
                    pyinstaller --onefile app\\main.py --name dinau
                """
            }
        }

        stage('Create GitHub Release') {
            when {
                expression { env.IS_RELEASE == 'true' }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'JenkinsGitHubToken', variable: 'GH_TOKEN')
                    ]) {
                        powershell """
                            \$ErrorActionPreference = "Stop"

                            \$tagName   = "\$env:GIT_TAG"
                            \$repoOwner = "Robin-Sonner"
                            \$repoName  = "freiburg-missing-semester-course/project-Robin-Sonner"
                            \$token     = "\$env:GH_TOKEN"

                            Write-Host "Creating release for tag: \$tagName"

                            \$releaseData = @{
                                tag_name   = \$tagName
                                name       = \$tagName
                                body       = "Release \$tagName"
                                draft      = \$false
                                prerelease = \$false
                            } | ConvertTo-Json

                            \$headers = @{
                                Authorization = "token \$token"
                                Accept        = "application/vnd.github.v3+json"
                            }

                            \$release = Invoke-RestMethod `
                                -Uri "https://api.github.com/repos/\$repoOwner/\$repoName/releases" `
                                -Method Post `
                                -Headers \$headers `
                                -Body \$releaseData `
                                -ContentType "application/json"

                            Write-Host "Release created: \$($release.html_url)"

                            \$uploadUrl = \$release.upload_url.Split('{')[0]
                            \$assetPath = "dist\\dinau.exe"
                            \$assetName = "dinau-\$tagName.exe"

                            \$uploadHeaders = @{
                                Authorization = "token \$token"
                                "Content-Type" = "application/octet-stream"
                            }

                            Invoke-RestMethod `
                                -Uri "\$uploadUrl?name=\$assetName" `
                                -Method Post `
                                -Headers \$uploadHeaders `
                                -InFile \$assetPath
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def result = currentBuild.result ?: 'SUCCESS'
                def state = (result == 'SUCCESS') ? 'success' :
                            (result == 'UNSTABLE') ? 'failure' : 'error'

                withCredentials([
                    string(credentialsId: 'JenkinsGitHubToken', variable: 'GH_TOKEN')
                ]) {
                    def commitSha = powershell(
                        returnStdout: true,
                        script: 'git rev-parse HEAD'
                    ).trim()

                    def repo = 'freiburg-missing-semester-course/project-Robin-Sonner'

                    powershell """
                        \$headers = @{
                            Authorization = "token ${GH_TOKEN}"
                            Accept        = "application/vnd.github.v3+json"
                        }

                        \$body = @{
                            state       = "${state}"
                            context     = "continuous-integration/jenkins"
                            description = "Build ${result}"
                            target_url = "${env.BUILD_URL}"
                        } | ConvertTo-Json

                        Invoke-RestMethod `
                            -Uri "https://api.github.com/repos/${repo}/statuses/${commitSha}" `
                            -Method Post `
                            -Headers \$headers `
                            -Body \$body `
                            -ContentType "application/json"
                    """
                }
            }
            cleanWs()
        }
    }
}

