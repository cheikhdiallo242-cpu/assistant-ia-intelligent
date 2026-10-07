from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>Assistant IA intelligent</h1>
    <p>Bienvenue dans notre application.</p>
    <p>Le système est en construction. 🤖</p>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
