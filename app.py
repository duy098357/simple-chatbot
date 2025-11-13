from flask import Flask, request, jsonify
import re
import json
from datetime import datetime
from flask_cors import CORS  # Allow frontend to talk to backend from another origin

app = Flask(__name__)
CORS(app)  # Enable CORS for local dev & browser clients

# --- Load intents from JSON ---
with open('intents.json', 'r', encoding='utf-8') as f:
    INTENTS = json.load(f)

def match_intent(text):
    text_l = text.lower().strip()
    # Pattern match first
    for intent in INTENTS['intents']:
        for pattern in intent.get('patterns', []):
            if pattern.lower() in text_l:
                return intent
    # Fallback: keyword scoring
    best, best_score = None, 0
    words = set(re.findall(r'\w+', text_l))
    for intent in INTENTS['intents']:
        kws = set(intent.get('patterns', [])) | set(intent.get('keywords', [])) if 'keywords' in intent else set()
        score = len(words & kws)
        if score > best_score:
            best_score = score
            best = intent
    return best

# --- Health check for browser ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "StratoBridge Chatbot backend running."})

# --- Chat endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    user_text = data.get("message", "").strip()

    if not user_text:
        return jsonify({"reply": "Please enter a message."}), 400

    intent = match_intent(user_text)
    if intent:
        reply = intent.get("responses", ["Sorry, I don’t have an answer for that."])[0]
        return jsonify({
            "reply": reply,
            "intent": intent.get("tag"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    else:
        return jsonify({
            "reply": "Sorry — I didn’t quite get that. Would you like to talk to a live agent or submit a quick form?",
            "intent": "fallback",
            "handoff": True
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
