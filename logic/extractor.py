import json


def extract_intents_logic(raw, filter_text):
    intents_data = {}
    intent_count = 0
    phrase_count = 0

    if not raw:
        return {}, 0, 0

    data = json.loads(raw)

    if isinstance(data, dict):
        data = [data]

    for item in data:

        # Dialogflow-style
        if isinstance(item, dict) and "trainingPhrases" in item:
            phrases = []

            for phrase in item.get("trainingPhrases", []):
                parts = phrase.get("parts", [])
                text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()

                if text and (not filter_text or filter_text in text.lower()):
                    phrases.append(text)
                    phrase_count += 1

            if phrases:
                name = item.get("displayName") or item.get("name") or phrases[0][:30]
                intents_data[name] = phrases
                intent_count += 1

        # generic
        elif isinstance(item, dict):
            for intent in item.get("intents", []):
                name = intent.get("name") or intent.get("intent")
                phrases = []

                for ex in intent.get("examples", []):
                    if isinstance(ex, str) and (not filter_text or filter_text in ex.lower()):
                        phrases.append(ex)
                        phrase_count += 1

                if phrases:
                    intents_data[name] = phrases
                    intent_count += 1

    return intents_data, intent_count, phrase_count