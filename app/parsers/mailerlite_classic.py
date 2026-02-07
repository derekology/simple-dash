import re

def parse_kv(line: str):
    parts = [p.strip().strip('"') for p in line.split(",") if p.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


def extract_number_and_percent(value: str):
    if not value:
        return None, None
    
    num_match = re.search(r"([\d,]+)", value)
    pct_match = re.search(r"\(([\d.]+)%\)", value)

    num = int(num_match.group(1).replace(",", "")) if num_match else None
    pct = float(pct_match.group(1)) / 100 if pct_match else None

    return num, pct


def sanitize_title(subject: str) -> str:
    """Remove special characters from subject line to create a clean title."""
    if not subject:
        return "Untitled"
    cleaned = re.sub(r'[^\w\s\-.,!?]', '', subject)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else "Untitled"


def parse_mailerlite_classic(text: str):
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    section = None

    data = {
        "platform": "mailerlite_classic",
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
        "hard_bounces": None,
        "hard_bounce_rate": None,
        "soft_bounces": None,
        "soft_bounce_rate": None,
    }

    for line in lines:
        if line == 'Campaign report':
            section = "campaign_report"
            continue
        elif line == '"Campaign results"':
            section = "campaign_results"
            continue
        elif line == '"Bad statistics"':
            section = "bad_statistics"
            continue
        elif line == '"Links activity"':
            section = "links_activity"
            continue

        if section == "campaign_report":
            key, val = parse_kv(line)
            if key == "Subject:":
                data["subject"] = val
            elif key == "Sent":
                data["sent_at"] = val

        elif section == "campaign_results":
            key, val = parse_kv(line)
            if key == "Total emails sent:":
                data["delivered"] = int(val.replace(",", ""))
            elif key == "Opened:":
                num, pct = extract_number_and_percent(val)
                data["opens"] = num
                data["open_rate"] = pct
            elif key == "Clicked:":
                num, pct = extract_number_and_percent(val)
                data["clicks"] = num
                data["click_rate"] = pct

        elif section == "bad_statistics":
            key, val = parse_kv(line)
            num, pct = extract_number_and_percent(val)
            if key == "Unsubscribed:":
                data["unsubscribes"] = num
                data["unsubscribe_rate"] = pct
            elif key == "Spam complaints:":
                data["spam_complaints"] = num
            elif key == "Hard bounce:":
                data["hard_bounces"] = num
                data["hard_bounce_rate"] = pct
            elif key == "Soft bounce:":
                data["soft_bounces"] = num
                data["soft_bounce_rate"] = pct

    if data["opens"] and data["clicks"]:
        data["ctor"] = data["clicks"] / data["opens"]
    else:
        data["ctor"] = None

    data["email_title"] = sanitize_title(data["subject"])

    return {
        "campaign": data
    }
