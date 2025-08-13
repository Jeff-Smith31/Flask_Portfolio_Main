# Flask Portfolio

A Flask application for a full‑stack software developer portfolio. Now deployable on AWS Lambda (serverless).

## Features
- Flask app with pages: Home, Work, Services, About, Contact, Résumé
- Modern dark UI with marquee, portfolio grid, and subtle animations
- Links for GitHub, LinkedIn, projects, and PDF résumé
- Serverless-ready via AWS Lambda (awsgi adapter)

## Local Development
1. Create and activate a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Flask:
   ```bash
   set FLASK_APP=app.py  # On macOS/Linux: export FLASK_APP=app.py
   flask run
   ```
   Visit http://127.0.0.1:5000

## AWS Lambda Deployment
This app includes a Lambda handler at `app.lambda_handler` using `awsgi` to translate API Gateway/Lambda events to WSGI.

Option A: Deploy with AWS Console + Function URL
1. Build a deployment package locally (from the project root):
   ```bash
   rm -rf build && mkdir -p build
   pip install --platform manylinux2014_x86_64 --only-binary=:all: --target build -r requirements.txt
   cp -R app.py wsgi.py templates static assets build/
   (cd build && zip -r ../package.zip .)
   ```
2. In AWS Lambda, create a Python 3.12 function.
3. Upload `package.zip` to the function (Code > Upload from > .zip file).
4. Set the Handler to: `app.lambda_handler`.
5. Configure a Function URL (Auth: NONE) or attach an HTTP API Gateway.
6. Test by opening the Function URL; static assets are served under `/static/...` and `/assets/...`.

Option B: Deploy with AWS SAM/Serverless Framework (recommended for CI/CD)
- This repo includes a ready-to-use AWS SAM template (template.yaml) and a GitHub Actions workflow (.github/workflows/deploy-sam.yml).
- Runtime: Python 3.12; Handler: app.lambda_handler; CodeUri points to project root to include templates, static, and assets.

Manual (local) deploy with SAM:
```bash
# Build (no container needed for pure-Python deps in this repo)
sam build

# Deploy (uses samconfig.toml defaults)
# Provide your SECRET_KEY at deploy time (required). Example:
sam deploy --parameter-overrides SecretKeyParam=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```
## License
This project is licensed under the Apache 2.0 License. See LICENSE for details.


## CI/CD note on SECRET_KEY
- The GitHub Actions workflow will use the repository secret FLASK_SECRET_KEY if set.
- If FLASK_SECRET_KEY is not set, the workflow will generate a strong random key for that deployment using Python's secrets.token_urlsafe(32).
- Important: When a new random key is generated, previously issued session cookies will become invalid (users will be logged out). To avoid unexpected session rotation, set a stable FLASK_SECRET_KEY in your repository secrets.
