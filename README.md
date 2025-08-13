# Flask Portfolio

A Flask application for a full‑stack software developer portfolio. Now deployable on AWS Lambda (serverless).

## Features
- Flask app with pages: Home, Work, Services, About, Contact, Résumé
- Modern dark UI with marquee, portfolio grid, and subtle animations
- Links for GitHub, LinkedIn, projects, and PDF résumé
- Serverless-ready via AWS Lambda (awsgi adapter)
- Contact form sends email via Amazon SES (with logging and helpful diagnostics)

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
# Provide your SECRET_KEY and contact parameters at deploy time. Example:
sam deploy \
  --parameter-overrides \
    SecretKeyParam=$(python -c "import secrets; print(secrets.token_urlsafe(32))") \
    ContactRecipientParam=you@example.com \
    ContactSenderParam=you@example.com
```

## CI/CD note on SECRET_KEY
- The GitHub Actions workflow will use the repository secret FLASK_SECRET_KEY if set.
- If FLASK_SECRET_KEY is not set, the workflow will generate a strong random key for that deployment using Python's secrets.token_urlsafe(32).
- Important: When a new random key is generated, previously issued session cookies will become invalid (users will be logged out).

## License
This project is licensed under the Apache 2.0 License. See LICENSE for details.
# Flask Portfolio

## SES deliverability tips (reduce spam)
- Use a sender address on your domain (e.g., contact@jeffrey-smith-dev.com) for CONTACT_SENDER. Avoid gmail.com senders when using SES.
- In Amazon SES: verify your domain and enable DKIM. Consider setting up Custom MAIL FROM for bounce alignment.
- If you configured Custom MAIL FROM, set ReturnPathParam (e.g., bounce@jeffrey-smith-dev.com) so Return-Path aligns with your domain.
- If SES is in sandbox, verify the recipient or request production access.
- If your SES identities are in a different AWS region than the Lambda, set SesRegionParam.
- Check CloudWatch Logs for "SES send_email success" or errors to diagnose issues.

## CI/CD note on SECRET_KEY
- The GitHub Actions workflow will use the repository secret FLASK_SECRET_KEY if set.
- If FLASK_SECRET_KEY is not set, the workflow will generate a strong random key for that deployment using Python's secrets.token_urlsafe(32).
- Important: When a new random key is generated, previously issued session cookies will become invalid (users will be logged out).

## License
This project is licensed under the Apache 2.0 License. See LICENSE for details.
