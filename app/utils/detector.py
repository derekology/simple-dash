from app.parsers.mailerlite_classic import parse_mailerlite_classic
from app.parsers.mailchimp_ab import parse_mailchimp_ab
from app.parsers.mailchimp import parse_mailchimp
from app.parsers.mailchimp_aggregated import parse_mailchimp_aggregated

def detect_and_parse(text: str):
    """Detect the platform and parse accordingly"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # MailChimp A/B Test Campaign
    if any("Campaign Report" in line for line in lines[:5]) and \
       any("Combination" in line and "Stats" in line for line in lines[:20]):
        return parse_mailchimp_ab(text)
    
    # MailChimp Single Campaign
    if any("Email Campaign Report" in line for line in lines[:5]) and \
       any("Overall Stats" in line for line in lines[:20]):
        return parse_mailchimp(text)
    
    # MailChimp Aggregated Reports
    if 'Unique Id' in text and 'Send Date' in text and 'Open Rate' in text:
        return parse_mailchimp_aggregated(text)
    
    # MailerLite Classic
    if 'Campaign report' in text and 'Campaign results' in text:
        return parse_mailerlite_classic(text)

    raise ValueError("Unsupported or unrecognized report format")
