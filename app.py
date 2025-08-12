from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os


# --- Resume PDF parsing helpers ---

def extract_experience_from_pdf(pdf_path: str):
    """Attempt to extract the 'Experience' section from a resume PDF.
    Returns a list of blocks. Each block is a dict: { 'header': str, 'lines': [str, ...] }.
    Parsing is best‑effort and tolerant to unknown formats.
    """
    try:
        from PyPDF2 import PdfReader
    except Exception:
        return []

    if not os.path.exists(pdf_path):
        return []

    # 1) Extract raw text
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return []

    if not text:
        return []

    # Normalize whitespace
    raw = "\n".join(line.strip() for line in text.splitlines())

    # 2) Find Experience section boundaries
    lower = raw.lower()
    start_idx = lower.find("experience")
    if start_idx == -1:
        # Try alternate headings
        for key in ["professional experience", "work experience"]:
            start_idx = lower.find(key)
            if start_idx != -1:
                break
    if start_idx == -1:
        return []

    # Candidates for next section headers to stop at
    stops = [
        "education", "skills", "projects", "certifications", "publications", "awards", "summary", "profile",
    ]
    end_idx = len(raw)
    for s in stops:
        i = lower.find(s, start_idx + 10)
        if i != -1:
            end_idx = min(end_idx, i)
    section = raw[start_idx:end_idx].strip()

    # Remove the heading line itself if present
    lines = [ln for ln in section.splitlines() if ln]
    if lines and lines[0].lower().startswith("experience"):
        lines = lines[1:]

    # 3) Split into blocks separated by blank lines or obvious role separators
    # Reconstruct with explicit blank lines to detect breaks
    # Here, we make a simple heuristic: treat lines that look like role headers as new blocks
    blocks = []
    current = []
    def flush():
        nonlocal current
        if current:
            header = current[0]
            rest = current[1:]
            blocks.append({"header": header, "lines": rest})
            current = []

    for ln in lines:
        # Heuristic: a header often contains a dash or an en dash between Title and Company or has dates in parentheses
        if current and (" — " in ln or " - " in ln or "(" in ln and ")" in ln):
            # Potentially a new header line; if previous current is small, flush before starting anew
            # Safer approach: start a new block if current already has a header and at least one detail line
            flush()
        current.append(ln)
    flush()

    # Filter out very small noise blocks
    cleaned = []
    for b in blocks:
        if b["header"] and any(ch.isalpha() for ch in b["header"]):
            cleaned.append(b)
    return cleaned


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_change_me')

    # Preload resume experience at startup (prioritize curated data from user input)
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

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/services')
    def services():
        return render_template('services.html')

    @app.route('/work')
    def work():
        # Dummy portfolio items
        items = [
            {
                'title': 'Real‑time Chat Application',
                'tags': ['Flask', 'WebSocket', 'Redis'],
                'image': 'https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop',
                'link': '#'
            },
            {
                'title': 'Data Dashboard',
                'tags': ['Plotly', 'Pandas', 'Application Programming Interfaces'],
                'image': 'https://images.unsplash.com/photo-1551281044-8d8e372c61f7?q=80&w=1200&auto=format&fit=crop',
                'link': '#'
            },
            {
                'title': 'Electronic Commerce Backend',
                'tags': ['Flask', 'Stripe', 'PostgreSQL'],
                'image': 'https://images.unsplash.com/photo-1519337265831-281ec6cc8514?q=80&w=1200&auto=format&fit=crop',
                'link': '#'
            },
            {
                'title': 'Machine Learning Inference API',
                'tags': ['FastAPI', 'Scikit‑Learn', 'Docker'],
                'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop',
                'link': '#'
            },
        ]
        return render_template('work.html', items=items)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            # For demo purposes, just flash a message.
            flash(f'Thanks {name}! Your message has been received. I will get back to {email} soon.', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html')

    @app.route('/resume')
    def resume():
        experience = app.config.get('RESUME_EXPERIENCE') or []
        return render_template('resume.html', experience=experience)

    @app.route('/assets/<path:filename>')
    def assets(filename):
        # Serve files from the assets directory (e.g., JEFFREY_SMITH.pdf)
        return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

    return app


# For flask run
app = create_app()
