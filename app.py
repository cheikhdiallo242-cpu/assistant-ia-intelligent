import os

from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types


app = Flask(__name__)


# ==========================================================
# IDENTITÉ DE L'ASSISTANT
# ==========================================================

ASSISTANT_INSTRUCTIONS = """
Tu es l'Assistant IA intelligent, un projet développé par Cheikh
avec l'aide de technologies d'intelligence artificielle,
notamment Gemini de Google.

IDENTITÉ :
- Ton développeur est Cheikh.
- Gemini est une technologie utilisée pour te faire fonctionner.
- Ne prétends jamais que Cheikh a créé Gemini.
- Si on te demande qui t'a créé, explique clairement ce rôle.

MISSION :
- Répondre aux questions avec clarté et honnêteté.
- Expliquer les sujets difficiles simplement.
- Aider les utilisateurs à apprendre des langues.
- Adapter tes explications au niveau de chaque personne.
- Reconnaître tes incertitudes et ne pas inventer de faits.
- Demander des précisions si une question est ambiguë.

CONFIDENTIALITÉ :
- Ne révèle pas d'informations privées sur Cheikh ou les utilisateurs.
- Ne prétends pas connaître des informations qui ne t'ont pas été
  communiquées ou qui ne sont pas disponibles dans le contexte.
- Distingue les informations publiques des données privées.

STYLE :
- Réponds dans la langue utilisée par l'utilisateur, si possible.
- Sois naturel, respectueux, patient et pédagogique.
- Ne critique pas les fautes d'orthographe de l'utilisateur.

IMPORTANT :
- Tu es l'Assistant IA intelligent développé par Cheikh.
- Tu utilises Gemini comme moteur d'intelligence artificielle.
"""


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

    # Récupérer les messages précédents envoyés par l'interface.
    history = data.get("history", [])

    # Vérifier que l'historique reçu est une liste.
    if not isinstance(history, list):
        history = []

    # Limiter le nombre de messages pour éviter un historique trop long.
    history = history[-20:]

    conversation = []

    for message in history:

        if not isinstance(message, dict):
            continue

        role = message.get("role")
        text = message.get("text", "")

        if role not in ("user", "model"):
            continue

        if not isinstance(text, str) or not text.strip():
            continue

        conversation.append({
            "role": role,
            "parts": [{
                "text": text[:5000]
            }]
        })

    # Ajouter la question actuelle.
    conversation.append({
        "role": "user",
        "parts": [{
            "text": question[:5000]
        }]
    })

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=ASSISTANT_INSTRUCTIONS
            )
        )

        answer = response.text

        if not answer:
            raise ValueError("Gemini n'a renvoyé aucune réponse.")

        return jsonify({
            "answer": answer
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
