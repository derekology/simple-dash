from app.parsers.mailerlite_classic import parse_mailerlite_classic

def detect_and_parse(text: str):
    if 'Campaign report' in text and 'Campaign results' in text:
        return parse_mailerlite_classic(text)

    raise ValueError("Unsupported or unrecognized report format")
