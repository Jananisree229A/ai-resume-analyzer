from flask import Flask, render_template, request
import os
import re
from PyPDF2 import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    # =========================
    # FILE UPLOAD
    # =========================

    if "resume" not in request.files:
        return "No file uploaded"

    file = request.files["resume"]

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # =========================
    # PDF TEXT EXTRACTION
    # =========================

    reader = PdfReader(filepath)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    # =========================
    # NAME EXTRACTION
    # =========================

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    name = "Not Found"

    blacklist = [
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "objective",
        "summary"
    ]

    for line in lines[:15]:

        if (
            len(line.split()) >= 2
            and len(line.split()) <= 4
            and "@" not in line
            and not any(char.isdigit() for char in line)
            and line.lower() not in blacklist
        ):
            name = line
            break

    # =========================
    # EMAIL EXTRACTION
    # =========================

    email_match = re.findall(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    email = email_match[0] if email_match else "Not Found"

    # =========================
    # PHONE EXTRACTION
    # =========================

    phone_match = re.findall(
        r'(?:\+91[-\s]?)?[6-9]\d{9}',
        text
    )

    phone = phone_match[0] if phone_match else "Not Found"

    # =========================
    # SKILLS DATABASE
    # =========================

    skills_list = [
        "Python",
        "Java",
        "C",
        "C++",
        "HTML",
        "CSS",
        "JavaScript",
        "SQL",
        "Flask",
        "Django",
        "Machine Learning",
        "Data Science",
        "Git",
        "React",
        "Node.js",
        "MongoDB",
        "Bootstrap",
        "AWS",
        "Docker",
        "Linux",
        "Power BI",
        "Excel"
    ]

    found_skills = []
    missing_skills = []

    for skill in skills_list:

        if skill.lower() in text.lower():
            found_skills.append(skill)

        else:
            missing_skills.append(skill)

    # =========================
    # ATS SCORE
    # =========================

    ats_score = min(len(found_skills) * 8, 100)

    # =========================
    # STRENGTHS
    # =========================

    strengths = []

    if len(found_skills) >= 5:
        strengths.append("Good technical skill coverage")

    if "project" in text.lower():
        strengths.append("Projects section detected")

    if "internship" in text.lower():
        strengths.append("Internship experience detected")

    if email != "Not Found":
        strengths.append("Professional contact information available")

    if not strengths:
        strengths.append("Resume has room for improvement")

    # =========================
    # SUGGESTIONS
    # =========================

    suggestions = []

    if ats_score < 80:
        suggestions.append("Add more relevant technical skills.")

    if "project" not in text.lower():
        suggestions.append("Add project experience section.")

    if (
        "certificate" not in text.lower()
        and "certification" not in text.lower()
    ):
        suggestions.append("Add certifications.")

    if "internship" not in text.lower():
        suggestions.append("Add internship or work experience.")

    if len(found_skills) < 5:
        suggestions.append("Include more tools and technologies.")

    if len(suggestions) == 0:
        suggestions.append("Excellent Resume! Keep it up.")

    # =========================
    # RENDER RESULT PAGE
    # =========================

    return render_template(
        "result.html",
        name=name,
        email=email,
        phone=phone,
        found_skills=found_skills,
        missing_skills=missing_skills,
        strengths=strengths,
        ats_score=ats_score,
        suggestions=suggestions,
        text=text
    )


if __name__ == "__main__":
    app.run(debug=True)