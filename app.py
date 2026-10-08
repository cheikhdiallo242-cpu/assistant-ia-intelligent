import os

from flask import Flask, render_template, request, jsonify
from google import genai


app = Flask(__name__)


# Connexion à Gemini
# La clé sera fournie par la variable d'environnement GEMINI_API_KEY.
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "error": "Écris une question."
        }), 400

    if client is None:
        return jsonify({
            "error": "La clé Gemini n'est pas encore configurée."
        }), 500

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        return jsonify({
            "answer": response.text
        })

    except Exception as error:
        print("Erreur Gemini :", error)

        return jsonify({
            "error": "Une erreur est survenue pendant la réponse de l'assistant."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
