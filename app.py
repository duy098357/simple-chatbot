from flask import Flask, request, jsonify
import re
import json
from datetime import datetime

app = Flask(__name__)

# Load intents (editable JSON file - see intents.json below)
with open('intents.json', 'r', encoding='utf-8') as f:
    INTENTS = json.load(f)

def match_intent(text):
    text_l = text.lower().strip()
    # Try exact intent patterns (ordered)
    for intent in INTENTS['intents']:
        for pattern in intent.get('patterns', []):
            if re.search(pattern, text_l):
                return intent
    # fallback: keyword scoring
    best = None
    best_score = 0
    words = set(re.findall(r'\w+', text_l))
    for intent in INTENTS['intents']:
        kws = set(intent.get('keywords', []))
        score = len(words & kws)
        if score > best_score:
            best_score = score
            best = intent
    if best_score >= 1:
        return best
    return None

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    text = data.get('message', '')
    session_id = data.get('session_id') or 'anon'
    intent = match_intent(text)
    if intent:
        # If the intent needs data (like rates) we can expand here
        response_text = intent.get('responses', ["Sorry, I don't have an answer right now."])[0]
        # if this intent requests handoff, provide handoff options
        handoff = intent.get('handoff', False)
        payload = {
            'reply': response_text,
            'intent': intent.get('name'),
            'handoff': handoff,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        # If handoff true, include contact data
        if handoff:
            payload['handoff_options'] = {
                'phone': '+1 (646) 450-3088',
                'email': 'info@stratolending.com',
                'open_form': True
            }
        return jsonify(payload)
    else:
        # fallback answer + offer handoff
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
