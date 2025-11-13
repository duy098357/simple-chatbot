# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow Wix frontend to access this backend

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").lower()

    # --- Simple response logic (you can replace this with OpenAI or GPT call) ---
    if "hello" in user_message:
        bot_reply = "Hi there! How can I help you today?"
    elif "help" in user_message:
        bot_reply = "Sure! What do you need help with?"
    elif "bye" in user_message:
        bot_reply = "Goodbye! Have a great day!"
    else:
        bot_reply = "I'm just a simple bot for now. Please try 'hello' or 'help'."
    
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
