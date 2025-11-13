from flask import Flask, request, jsonify
from flask_cors import CORS   # ✅ Enables CORS for Wix frontend
import re
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # ✅ Allow requests from Wix and other domains

# Load intents (editable JSON file)
with open('intents.json', 'r', encoding='utf-8') as f:
    INTENTS = json.load(f)

def match_intent(text):
    text_l = text.lower().strip()
    # Try regex patterns first
    for intent in INTENTS['intents']:
        for pattern in intent.get('patterns', []):
            if re.search(pattern, text_l):
                return intent
    # Fallback: keyword scoring
    best, best_score = None, 0
    words = set(re.findall(r'\w+', text_l))
    for intent in INTENTS['intents']:
        kws = set(intent.get('keywords', []))
        score = len(words & kws)
        if score > best_score:
            best_score = score
            best = intent
    return best if best_score >= 1 else None


@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ok", "message": "Strato Lending Chatbot API is live."})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    text = data.get('message', '').strip()
    if not text:
        return jsonify({'reply': "Please enter a message."}), 400

    intent = match_intent(text)
    if intent:
        response_text = intent.get('responses', ["Sorry, I don't have an answer right now."])[0]
        handoff = intent.get('handoff', False)
        payload = {
            'reply': response_text,
            'intent': intent.get('name') or intent.get('tag'),
            'handoff': handoff,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        if handoff:
            payload['handoff_options'] = {
                'phone': '+1 (646) 450-3088',
                'email': 'info@stratolending.com',
                'open_form': True
            }
        return jsonify(payload)
    else:
        return jsonify({
            'reply': "Sorry — I didn't quite get that. Would you like to talk to a live agent or submit a quick form?",
            'intent': 'fallback',
            'handoff': True,
            'handoff_options': {
                'phone': '+1 (646) 450-3088',
                'email': 'info@stratolending.com',
                'open_form': True
            }
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
