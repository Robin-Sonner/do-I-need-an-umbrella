pipeline {
    agent any

    // PATH Variables are a bit finicky in windows. Disregard PATH and pick python from here
    environment {
        PYTHON_HOME = 'C:\\Users\\Robin\\AppData\\Local\\Python\\pythoncore-3.14-64'
    }

    stages {

        // Releases are triggered when the commit message contains "release vX.Y.Z""
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
                        echo "Building Release ${env.GIT_TAG}"
                    } else {
                        env.IS_RELEASE = 'false'
                        env.GIT_TAG = ''
                        echo "Building regular commit (no release)"
                    }
                }
            }
        }

        // Optional: If a release is built, automatically create a Tag
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

        // Build the package with dev + gui dependencies (gui dependencies being needed for releases)
        stage('Setup') {
            steps {
                powershell """
                    & "\$env:PYTHON_HOME\\python.exe" --version
                    & "\$env:PYTHON_HOME\\python.exe" -m venv venv
                    .\\venv\\Scripts\\Activate.ps1
                    pip install -e .[dev,gui]
                """
            }
        }

        // Lint the project
        // E501 is long lines. In the cases were black allows long lines I don't care if flake doesn't like them
        stage('Linting') {
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    flake8 . --extend-ignore=E501 --exclude=.\\venv
                """
            }
        }

        // Check for adherence to import sorting and black formatting
        // pyproject.toml configures isort to respect black formatting
        stage('Format Check') {
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    black --check .
                    isort --check-only .
                """
            }
        }

        // Run all Unittests
        stage('Test') {
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    python -m unittest discover -s tests -p "*_test.py" -v
                """
            }
        }

        // Check if the documentation can be built without warnings 
        // (-W causes failure on warning)
        stage('Document') {
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    cd .\\docs
                    .\\make.bat html -W
                """
            }
        }

        // Optional: Build a .exe file
        stage('Build Release') {
            when {
                expression { env.IS_RELEASE == 'true' }
            }
            steps {
                powershell """
                    .\\venv\\Scripts\\Activate.ps1
                    pyinstaller --onefile app\\main.py --name dinau
                """
            }
        }

        // Optional: Build and publish the dinau package to TestPyPI
        stage('Publish to TestPyPI') {
            when {
                expression { env.IS_RELEASE == 'true' }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'TestPyPIToken', variable: 'TESTPYPI_TOKEN')
                    ]) {
                        powershell """
                            .\\venv\\Scripts\\Activate.ps1
                            # Build the package (creates dist/ folder with wheel and sdist)
                            python -m build
                            python -m twine upload --repository testpypi dist/*.whl dist/*.tar.gz --username __token__ --password \$env:TESTPYPI_TOKEN --verbose
                        """
                    }
                }
            }
        }

        // Optional: Publish the .exe file
        stage('Publish Release') {
            when {
                expression { env.IS_RELEASE == 'true' }
            }
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'JenkinsGitHubToken', variable: 'GH_TOKEN')
                    ]) {
                        powershell '''
                            $ErrorActionPreference = "Stop"

                            $tagName   = $env:GIT_TAG
                            $repoOwner = "freiburg-missing-semester-course"
                            $repoName  = "project-Robin-Sonner"
                            $token     = $env:GH_TOKEN

                            Write-Host "Creating release for tag: $tagName"

                            $releaseData = @{
                                tag_name   = $tagName
                                name       = $tagName
                                body       = "Release $tagName"
                                draft      = $false
                                prerelease = $false
                            } | ConvertTo-Json

                            $headers = @{
                                Authorization = "token $token"
                                Accept        = "application/vnd.github.v3+json"
                            }

                            $releaseResponse = Invoke-RestMethod `
                                -Uri "https://api.github.com/repos/$repoOwner/$repoName/releases" `
                                -Method Post `
                                -Headers $headers `
                                -Body $releaseData `
                                -ContentType "application/json"

                            Write-Host "Release created: $($releaseResponse.html_url)"

                            # Extract upload URL and remove the {?name,label} template part
                            $uploadUrl = $releaseResponse.upload_url -replace '\\{.*\\}', ''
                            $assetPath = "dist\\dinau.exe"
                            $assetName = "dinau-$tagName.exe"

                            Write-Host "Upload URL: $uploadUrl"
                            Write-Host "Asset path: $assetPath"

                            if (-Not (Test-Path $assetPath)) {
                                throw "Asset file not found: $assetPath"
                            }

                            $uploadHeaders = @{
                                Authorization = "token $token"
                                "Content-Type" = "application/octet-stream"
                            }

                            Write-Host "Uploading asset: $assetName"
                            Invoke-RestMethod `
                                -Uri "$uploadUrl`?name=$assetName" `
                                -Method Post `
                                -Headers $uploadHeaders `
                                -InFile $assetPath
                            
                            Write-Host "Asset uploaded successfully"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            // Update the Commit Check State
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
            // Cleanup
            cleanWs()
        }
    }
}
