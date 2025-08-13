import os


def extract_experience_from_pdf(pdf_path: str):
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
        if current and (" — " in ln or " - " in ln or ("(" in ln and ")" in ln)):
            flush()
        current.append(ln)
    flush()

    # Filter out very small noise blocks
    cleaned = []
    for b in blocks:
        if b["header"] and any(ch.isalpha() for ch in b["header"]):
            cleaned.append(b)
    return cleaned
