import pdfplumber
import pytesseract
from PIL import Image
import re
from datetime import datetime
import os


# If Windows, set path like this:
#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_file(file_path):

    text = ""

    if file_path.lower().endswith(".pdf"):

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    return text.upper()


def validate_iso_certificate(file_path):

    text = extract_text_from_file(file_path)

    if "ISO 9001" not in text:
        return False, None, None, "Invalid"

    cert_pattern = r"(CERT|CERTIFICATE)[\s\-:]?\d+"
    if not re.search(cert_pattern, text):
        return False, None, None, "Invalid"

    date_pattern = r"\d{2}/\d{2}/\d{4}"
    dates = re.findall(date_pattern, text)

    if not dates:
        return False, None, None, "Invalid"

    expiry_str = dates[-1]

    try:
        expiry_date = datetime.strptime(expiry_str, "%d/%m/%Y")
    except:
        return False, None, None, "Invalid"

    today = datetime.today()
    days_left = (expiry_date - today).days

    if days_left < 0:
        status = "Red"
    elif days_left <= 90:
        status = "Amber"
    else:
        status = "Green"

    return True, expiry_str, days_left, status
