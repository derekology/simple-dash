from app.parsers.mailerlite_classic import parse_mailerlite_classic
from app.parsers.mailchimp import parse_mailchimp

def detect_and_parse(text: str):
    # Check for MailChimp format
    if 'Unique Id' in text and 'Send Date' in text and 'Open Rate' in text:
        return parse_mailchimp(text)
    
    # Check for MailerLite Classic format
    if 'Campaign report' in text and 'Campaign results' in text:
        return parse_mailerlite_classic(text)

    raise ValueError("Unsupported or unrecognized report format")
