import re
from app.utils.id_generator import generate_unique_id

def parse_kv(line: str):
    """Parse key-value pair from CSV format like '"Title:","Personal Styling (Amy 02)"'"""
    parts = [p.strip().strip('"') for p in line.split('","') if p.strip()]
    if len(parts) >= 2:
        key = parts[0].strip(':').strip()
        value = parts[1].strip()
        return key, value
    return None, None


def extract_number_and_percent(value: str):
    """Extract number and percentage from strings like '1 (100.0%)'"""
    if not value:
        return None, None
    
    # Extract main number
    num_match = re.search(r'([\d,]+)', value)
    num = int(num_match.group(1).replace(',', '')) if num_match else None
    
    # Extract percentage
    pct_match = re.search(r'\(([\d.]+)%\)', value)
    pct = float(pct_match.group(1)) / 100 if pct_match else None
    
    return num, pct


def sanitize_title(subject: str) -> str:
    """Remove special characters from subject line to create a clean title."""
    if not subject:
        return "Untitled"
    cleaned = re.sub(r'[^\w\s\-.,!?]', '', subject)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else "Untitled"


def parse_mailchimp(text: str):
    """Parse MailChimp individual single campaign report"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    data = {
        "platform": "mailchimp",
        "subject": None,
        "email_title": None,
        "unique_id": None,
        "sent_at": None,
        "delivered": None,
        "opens": None,
        "open_rate": None,
        "clicks": None,
        "click_rate": None,
        "unsubscribes": None,
        "unsubscribe_rate": None,
        "spam_complaints": None,
        "bounces": None,
        "bounce_rate": None,
        "hard_bounces": None,
        "hard_bounce_rate": None,
        "soft_bounces": None,
        "soft_bounce_rate": None,
        "ctor": None,
    }
    
    campaign_title = None
    
    for line in lines:
        # Stop parsing at "Clicks by URL" section
        if line.startswith('"Clicks by URL"') or line.startswith('"URL"'):
            break
            
        key, val = parse_kv(line)
        
        if not key:
            continue
        
        if key == "Title":
            campaign_title = val
            data["unique_id"] = val
        elif key == "Subject Line":
            data["subject"] = val
        elif key == "Delivery Date/Time":
            data["sent_at"] = val
        elif key == "Successful Deliveries":
            data["delivered"] = int(val.replace(',', ''))
        elif key == "Recipients Who Opened":
            num, pct = extract_number_and_percent(val)
            data["opens"] = num
            data["open_rate"] = pct
        elif key == "Recipients Who Clicked":
            num, pct = extract_number_and_percent(val)
            data["clicks"] = num
            data["click_rate"] = pct
        elif key == "Total Unsubs":
            data["unsubscribes"] = int(val.replace(',', '')) if val != "0" else 0
        elif key == "Total Abuse Complaints":
            data["spam_complaints"] = int(val.replace(',', '')) if val != "0" else 0
        elif key == "Bounces":
            num, pct = extract_number_and_percent(val)
            data["bounces"] = num
            data["bounce_rate"] = pct
    
    # Calculate CTOR if we have data
    if data["opens"] and data["clicks"] and data["opens"] > 0:
        data["ctor"] = data["clicks"] / data["opens"]
    
    # Calculate unsubscribe rate if we have delivered count
    if data["delivered"] and data["unsubscribes"] is not None and data["delivered"] > 0:
        data["unsubscribe_rate"] = data["unsubscribes"] / data["delivered"]
    
    # Set email title
    title = sanitize_title(data.get("title", ""))
    data["email_title"] = title
    
    # Generate unique ID based on title, subject, and send date
    data["unique_id"] = generate_unique_id(
        title=title,
        subject=data.get("subject", ""),
        sent_at=data.get("sent_at", ""),
        platform="mailchimp"
    )
    
    return {
        "campaigns": [data]
    }
