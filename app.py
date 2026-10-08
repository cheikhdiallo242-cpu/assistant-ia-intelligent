import os

from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types


app = Flask(__name__)


# ==========================================================
# CONNEXION À GEMINI
# ==========================================================

api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=30000
    )
) if api_key else None


# ==========================================================
# PAGE PRINCIPALE
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================================
# QUESTION À L'ASSISTANT
# ==========================================================

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
            model="gemini-3.8-flash",
            contents=question
        )

        return jsonify({
            "answer": response.text
        })

    except Exception as error:

        print("Erreur Gemini :", error)

        return jsonify({
            "error": (
                "Le service d'intelligence artificielle "
                "est temporairement indisponible. "
                "Réessaie dans quelques instants."
            )
        }), 503


# ==========================================================
# DÉMARRAGE LOCAL
# ==========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
