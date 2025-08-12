# Flask Portfolio

A Dockerized Flask application for a full‑stack software developer portfolio.

## Features
- Flask app with pages: Home, Work, Services, About, Contact, Résumé
- Modern dark UI with marquee, portfolio grid, and subtle animations
- Links for GitHub, LinkedIn, projects, and PDF résumé
- Dockerfile and docker-compose for containerized deployment

## Local Development
1. Create and activate a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Flask:
   ```bash
   set FLASK_APP=app.py
   flask run
   ```
   Visit http://127.0.0.1:5000

## Docker
Build and run with Docker:
```bash
# Build image
docker build -t flask-portfolio .

# Run container
docker run -p 8000:8000 --env SECRET_KEY=not_gonna_happen flask-portfolio
```
Or using docker-compose:
```bash
docker compose up --build
```
Visit http://localhost:8000

## License
This project is licensed under the Apache 2.0 License. See LICENSE for details.
