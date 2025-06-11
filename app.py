from flask import Flask, request, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import uuid
import os

app = Flask(__name__, static_folder="static")
os.makedirs("static", exist_ok=True)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, y, data.get("title", "Form"))
    y -= 40

    form = c.acroForm
    for field in data['fields']:
        label = field['label']
        field_type = field['type']
        options = field.get('options', [])
        multiline = field.get('multiline', False)

        c.setFont("Helvetica", 12)
        c.drawString(50, y, label + ":")

        if field_type == "text":
            form.textfield(
                name=label,
                tooltip=label,
                x=150,
                y=y - 4,
                width=300,
                height=20 if not multiline else 60,
                borderStyle='underlined',
                fieldFlags=4096 if multiline else 0,
                multiline=multiline
            )
            y -= 40 if not multiline else 80

        elif field_type == "checkbox":
            for opt in options:
                c.drawString(150, y, opt)
                form.checkbox(name=f"{label}_{opt}", tooltip=opt, x=120, y=y, buttonStyle='check')
                y -= 25

        elif field_type == "radio":
            form.radio(
                name=label,
                tooltip=label,
                value=options[0],
                options=[(opt, 120 + i * 60, y) for i, opt in enumerate(options)]
            )
            y -= 30

        elif field_type == "dropdown":
            form.choice(
                name=label,
                tooltip=label,
                options=options,
                value=options[0],
                x=150,
                y=y,
                width=200,
                height=20,
                combo=True
            )
            y -= 40

        elif field_type == "listbox":
            form.choice(
                name=label,
                tooltip=label,
                options=options,
                value=options[0],
                x=150,
                y=y,
                width=200,
                height=60,
                combo=False
            )
            y -= 80

    c.save()
    buffer.seek(0)
    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join("static", filename)
    with open(filepath, 'wb') as f:
        f.write(buffer.read())

    return jsonify({"url": f"https://<RENDER_URL>/static/{filename}"})
