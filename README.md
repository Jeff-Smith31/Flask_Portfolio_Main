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

Manual (local) deploy with SAM:
```bash
# Build (no container needed for pure-Python deps in this repo)
sam build

# Deploy (uses samconfig.toml defaults)
# Provide your SECRET_KEY at deploy time (required). Example:
sam deploy --parameter-overrides SecretKeyParam=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

## CI/CD note on SECRET_KEY
- The GitHub Actions workflow will use the repository secret FLASK_SECRET_KEY if set.
- If FLASK_SECRET_KEY is not set, the workflow will generate a strong random key for that deployment using Python's secrets.token_urlsafe(32).
- Important: When a new random key is generated, previously issued session cookies will become invalid (users will be logged out).

## License
This project is licensed under the Apache 2.0 License. See LICENSE for details.