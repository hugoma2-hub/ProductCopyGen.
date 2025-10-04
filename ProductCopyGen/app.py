import random
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from flask_cors import CORS
import os
import csv

app = Flask(__name__)
CORS(app)

EMAIL_FILE = "emails.txt"
HISTORIAL_FILE = "history.txt"
ADMIN_PASSWORD = "qdB10C0LP6R6"  

# Crear archivos si no existen
for file in [EMAIL_FILE, HISTORIAL_FILE]:
    if not os.path.exists(file):
        open(file, "w", encoding="utf-8").close()

# Función para generar descripción según categoría
def generar_descripcion(product, category):
    ejemplos = [
        f"✨ {product}: Diseñado para quienes buscan calidad y confort en su día a día.",
        f"🚀 {product}: Ideal para destacar entre la competencia y atraer más clientes.",
        f"💡 {product}: Una mezcla perfecta de estilo moderno y practicidad.",
        f"🔥 {product}: Hecho para quienes no se conforman con lo común."
    ]

    # Puedes agregar ejemplos según categoría
    if category == "Moda":
        ejemplos += [
            f"👗 {product}: Estilo y elegancia que todos notarán.",
            f"🥿 {product}: Comodidad y tendencia en un solo producto."
        ]
    elif category == "Tecnología":
        ejemplos += [
            f"💻 {product}: Innovación y rendimiento en cada detalle.",
            f"📱 {product}: Conectividad y potencia para tu día a día."
        ]
    elif category == "Hogar":
        ejemplos += [
            f"🏠 {product}: Práctico y elegante para tu hogar.",
            f"🛋️ {product}: Funcionalidad y estilo combinados."
        ]
    elif category == "Deporte":
        ejemplos += [
            f"🏃 {product}: Rendimiento y comodidad para tus entrenamientos.",
            f"⚽ {product}: Diseñado para superar tus límites."
        ]

    return random.choice(ejemplos)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    product = data.get("product", "Producto")
    category = data.get("category", "General")

    text = generar_descripcion(product, category)

    # Guardar en historial
    with open(HISTORIAL_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

    # Retornar usos restantes (para JS)
    usos = int(data.get("usos", 3)) - 1
    return jsonify({"text": text, "usos": usos})

@app.route("/history", methods=["GET"])
def history():
    with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return jsonify({"history": lines[-3:]})  # Solo últimas 3 descripciones

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json
    email = data.get("email")
    if email and "@" in email:
        with open(EMAIL_FILE, "a", encoding="utf-8") as f:
            f.write(email + "\n")
        return jsonify({"status": "ok", "message": "Email guardado con éxito"})
    return jsonify({"status": "error", "message": "Correo inválido"}), 400

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            return redirect(url_for("dashboard"))
        else:
            return render_template("admin_login.html", error="Contraseña incorrecta")
    return render_template("admin_login.html", error=None)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    with open(EMAIL_FILE, "r", encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip()]
    with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
        history = [line.strip() for line in f if line.strip()]
    return render_template("admin_dashboard.html", emails=emails, history=history)

@app.route("/reset_usos", methods=["POST"])
def reset_usos():
    # Esta opción solo desde admin
    return jsonify({"status": "ok", "message": "Usos reseteados en cliente JS"}), 200

@app.route("/clear_emails", methods=["POST"])
def clear_emails():
    open(EMAIL_FILE, "w", encoding="utf-8").close()
    return jsonify({"status": "ok", "message": "Emails borrados"})

@app.route("/download_emails", methods=["GET"])
def download_emails():
    csv_file = "emails.csv"
    with open(EMAIL_FILE, "r", encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip()]
    with open(csv_file, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["Email"])
        for e in emails:
            writer.writerow([e])
    return send_file(csv_file, as_attachment=True)

@app.route("/clear_history", methods=["POST"])
def clear_history():
    # Mantener 3 últimos ejemplos
    with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    last_three = lines[-3:]
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        for l in last_three:
            f.write(l + "\n")
    return jsonify({"status": "ok", "message": "Historial limpio, se mantienen últimos 3 ejemplos"})

if __name__ == "__main__":
    app.run(debug=True)
