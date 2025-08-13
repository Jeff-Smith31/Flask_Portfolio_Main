from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import base64, mimetypes
from werkzeug.utils import safe_join

from resume_parser import extract_experience_from_pdf


def create_app():
    app = Flask(__name__)
    secret_from_env = os.environ.get('SECRET_KEY')
    running_in_lambda = bool(os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    if secret_from_env:
        app.config['SECRET_KEY'] = secret_from_env
    else:
        if running_in_lambda:
            raise RuntimeError("SECRET_KEY is not set. Configure a strong SECRET_KEY in the Lambda environment or via SAM parameter SecretKeyParam.")
        else:
            try:
                import secrets
                generated = secrets.token_urlsafe(32)
            except Exception:
                generated = os.urandom(32).hex()
            app.config['SECRET_KEY'] = generated

    # Contact email configuration
    app.config['CONTACT_RECIPIENT'] = os.environ.get('CONTACT_RECIPIENT')
    # If CONTACT_SENDER not provided, default to recipient (valid when SES verifies that address)
    app.config['CONTACT_SENDER'] = os.environ.get('CONTACT_SENDER') or app.config['CONTACT_RECIPIENT']

    # Preload resume experience at startup
    provided = [
        {
            "header": "Software Developer — Amazon (Apr 2023 – Mar 2025)",
            "lines": [
                "Contributed to developing scalable React applications integrated with Python and Java microservices on Amazon Web Services (Lambda, Elastic Container Service), improving operational tool performance and user experience.",
                "Designed and maintained back end application programming interfaces and serverless workflows using Amazon Web Services services, including API Gateway, DynamoDB, Amazon Aurora, and Amazon Simple Storage Service, ensuring high availability and low latency performance.",
                "Oversaw database architecture and optimization across Structured Query Language and NoSQL systems, increasing query performance and supporting real-time data analytics for business-critical tools."
            ]
        },
        {
            "header": "Business Analyst — Amazon (Jan 2022 – Apr 2023)",
            "lines": [
                "Developed and deployed React applications with Python and Java back ends on Amazon Web Services (Lambda, Elastic Container Service, Amazon Simple Storage Service), streamlining internal tools for shift planning and workforce tracking.",
                "Restructured DynamoDB and Amazon Aurora schemas, enhancing data accessibility and reducing load times for key business intelligence dashboards.",
                "Migrated legacy reporting systems to a serverless framework, lowering infrastructure overhead and improving long-term maintainability."
            ]
        },
        {
            "header": "Program Developer — Amazon (Jun 2021 – Jan 2022)",
            "lines": [
                "Developed custom data tools using Django and Python, enabling warehouse managers to track and identify backlogs and rectify impediments, improving workflow.",
                "Created interactive React dashboards for real-time operational metrics, enhancing data-driven decision-making across management teams.",
                "Built serverless web applications with Amazon Web Services Lambda and API Gateway, streamlining reporting processes and reducing manual dependencies.",
                "Automated performance data extraction and reporting with Amazon Redshift and DynamoDB, improving the speed and accuracy of daily reports.",
                "Collaborated with warehouse operations to refine data analytics tools using Python and Amazon Web Services services, leading to quicker issue identification and resolution."
            ]
        },
        {
            "header": "Data Analyst — Amazon (Aug 2020 – Jun 2021)",
            "lines": [
                "Analyzed warehouse datasets using Structured Query Language and Amazon Redshift to identify inventory gaps, improving forecast accuracy and enabling better supply chain planning.",
                "Automated data aggregation workflows with Python, reducing manual reporting time and enhancing operational efficiency across multiple business units.",
                "Developed audit-support dashboards for Sarbanes–Oxley Act compliance, streamlining documentation processes and ensuring control accuracy.",
                "Improved real-time inventory tracking accuracy by diagnosing inefficiencies in data input systems and enhancing data flow across platforms.",
                "Built Structured Query Language-based operational tools for fulfillment leads, ensuring faster identification and resolution of stock discrepancies while maintaining data integrity."
            ]
        }
    ]

    if provided:
        app.config['RESUME_EXPERIENCE'] = provided
    else:
        pdf_path = os.path.join(os.path.dirname(__file__), 'assets', 'JEFFREY_SMITH.pdf')
        app.config['RESUME_EXPERIENCE'] = extract_experience_from_pdf(pdf_path)

    # Shared portfolio items
    portfolio_items = [
        {
            'title': 'Wedding Photography Website',
            'tags': ['React', 'Vite', 'Tailwind'],
            'image': 'pictures/wedding_photography_card.jpg',
            'link': 'https://github.com/Jeff-Smith31/WeddingPhotographySite'
        },
        {
            'title': 'Data Dashboard Application',
            'tags': ['Python', 'Tkinter', 'Pandas', 'Application Programming Interfaces'],
            'image': 'pictures/data_dashboard_card.jpg',
            #Photo by Luke Chesser on Unsplash
            'link': 'https://github.com/Jeff-Smith31/Dashboard_App'
        },
        {
            'title': 'Deep Learning Model for Digit Recognition',
            'tags': ['Python', 'tensorflow'],
            'image': 'pictures/deep_learning_card.jpg',
            #Photo by Pietro Jeng on Unsplash
            'link': 'https://github.com/Jeff-Smith31/Deep_Learning'
        },
        {
            'title': 'Database with RESTful API',
            'tags': ['FastAPI', 'OAuth2', 'SQLAlchemy'],
            'image': 'pictures/API_card.jpg',
            #Photo by Riku Lu on Unsplash
            'link': 'https://github.com/Jeff-Smith31/API_Python'
        },
    ]

    @app.route('/')
    def index():
        # Show a subset of items on the home page
        return render_template('index.html', items=portfolio_items[:4])

    @app.route('/services')
    def services():
        return render_template('services.html')

    @app.route('/work')
    def work():
        return render_template('work.html', items=portfolio_items)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/certifications')
    def certifications():
        return render_template('certifications.html')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = (request.form.get('name') or '').strip()
            email_addr = (request.form.get('email') or '').strip()
            message = (request.form.get('message') or '').strip()

            if not name or not email_addr or not message:
                flash('Please fill out all fields.', 'error')
                return redirect(url_for('contact'))

            recipient = app.config.get('CONTACT_RECIPIENT')
            sender = app.config.get('CONTACT_SENDER')

            if not recipient or not sender:
                # In local/dev without env vars, avoid crashing and inform via flash
                flash('Message received locally. Email delivery is not configured. Set CONTACT_RECIPIENT/CONTACT_SENDER to enable email.', 'error')
                return redirect(url_for('contact'))

            subject = f"New contact form submission from {name}"
            body_text = (
                f"You received a new message via the portfolio contact form.\n\n"
                f"Name: {name}\n"
                f"Email: {email_addr}\n\n"
                f"Message:\n{message}\n"
            )

            # Try to send via AWS SES
            try:
                import boto3  # type: ignore
                import os as _os
                region = _os.environ.get('AWS_REGION') or _os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
                ses = boto3.client('ses', region_name=region)
                ses.send_email(
                    Source=sender,
                    Destination={'ToAddresses': [recipient]},
                    Message={
                        'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                        'Body': {'Text': {'Data': body_text, 'Charset': 'UTF-8'}}
                    },
                    ReplyToAddresses=[email_addr] if email_addr else []
                )
                flash(f'Thanks {name}! Your message has been sent. I will get back to {email_addr} soon.', 'success')
            except Exception as e:
                # Do not expose sensitive details; optionally log if you have logging
                flash('Sorry, there was an issue sending your message. Please try again later.', 'error')
            return redirect(url_for('contact'))
        return render_template('contact.html')

    @app.route('/resume')
    def resume():
        experience = app.config.get('RESUME_EXPERIENCE') or []
        return render_template('resume.html', experience=experience)

    @app.route('/assets/<path:filename>')
    def assets(filename):
        # Serve files from the assets directory
        return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

    # Helper: build data URI for assets to avoid binary issues through awsgi
    def asset_data_uri(path: str) -> str:
        try:
            # Resolve and ensure the path stays within assets directory
            assets_dir = os.path.join(app.root_path, 'assets')
            full_path = safe_join(assets_dir, path)
            if not full_path or not os.path.exists(full_path):
                return ''
            mime, _ = mimetypes.guess_type(full_path)
            mime = mime or 'application/octet-stream'
            with open(full_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('ascii')
            return f'data:{mime};base64,{b64}'
        except Exception:
            return ''

    # Expose helper to Jinja templates
    app.jinja_env.globals['asset_data_uri'] = asset_data_uri

    return app


# For flask run
app = create_app()

# AWS Lambda handler (via awsgi)
try:
    import awsgi  # type: ignore
    from urllib.parse import parse_qs

    def _normalize_event_for_awsgi(evt: dict) -> dict:

        try:
            if isinstance(evt, dict) and 'httpMethod' not in evt:
                rc = evt.get('requestContext') or {}
                http = rc.get('http') or {}
                method = http.get('method')
                if method:
                    new_evt = dict(evt)
                    new_evt['httpMethod'] = method
                    # Path
                    path = evt.get('rawPath') or http.get('path') or evt.get('path') or '/'
                    new_evt['path'] = path
                    # Query string
                    if 'queryStringParameters' not in new_evt:
                        raw_qs = evt.get('rawQueryString') or ''
                        if raw_qs:
                            qs_map = {k: v[0] if isinstance(v, list) else v for k, v in parse_qs(raw_qs, keep_blank_values=True).items()}
                        else:
                            qs_map = None
                        new_evt['queryStringParameters'] = qs_map
                    # Headers fallback
                    if 'headers' not in new_evt or new_evt['headers'] is None:
                        new_evt['headers'] = {}
                    # Body passthrough, ensure isBase64Encoded present
                    if 'isBase64Encoded' not in new_evt:
                        new_evt['isBase64Encoded'] = bool(evt.get('isBase64Encoded', False))
                    return new_evt
        except Exception:
            # If normalization fails, fall back to original event
            return evt
        return evt

    def lambda_handler(event, context):
        event = _normalize_event_for_awsgi(event)
        return awsgi.response(app, event, context)
except Exception:
    # awsgi not available in local/dev environments
    pass
