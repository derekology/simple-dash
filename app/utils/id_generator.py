import hashlib
import re
from datetime import datetime


def normalize_datetime(date_str: str) -> str:
    """
    Normalize various datetime formats to a consistent string for hashing.
    Tries to parse common formats and returns a normalized string.
    """
    if not date_str:
        return ""
    
    # Common MailChimp formats: 
    # "Mon, Apr 26, 2021 12:25" 
    # "Sat, May 1, 2021 10:15"
    # "6/9/2018 21:30" (M/D/YYYY H:MM)
    # "Jun 09, 2018 09:30 pm" (with am/pm)
    # "2018-06-09 21:30" (ISO-like)
    # Common MailerLite formats: "2021-04-26 12:25:00"
    
    # Try to parse various formats
    formats = [
        "%a, %b %d, %Y %H:%M",    # Mon, Apr 26, 2021 12:25
        "%Y-%m-%d %H:%M:%S",       # 2021-04-26 12:25:00
        "%Y-%m-%d %H:%M",          # 2021-04-26 12:25 (already normalized)
        "%m/%d/%Y %H:%M",          # 6/9/2018 21:30
        "%m/%d/%y %H:%M",          # 6/9/18 21:30
        "%-m/%-d/%Y %H:%M",        # 6/9/2018 21:30 (no padding)
        "%-m/%-d/%y %H:%M",        # 6/9/18 21:30 (no padding)
        "%d/%m/%Y %H:%M",          # 09/06/2018 21:30
        "%b %d, %Y %I:%M %p",      # Jun 09, 2018 09:30 pm
    ]
    
    # Clean up the string first
    clean_str = re.sub(r'\s+', ' ', date_str.strip())
    
    for fmt in formats:
        try:
            dt = datetime.strptime(clean_str, fmt)
            # Return ISO format for consistency: YYYY-MM-DD HH:MM
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    
    # If parsing fails, just clean and return the string
    return clean_str


def generate_unique_id(title: str = "", subject: str = "", sent_at: str = "", platform: str = "") -> str:
    """
    Generate a consistent unique ID based on campaign title, subject, and send date/time.
    
    Args:
        title: Campaign title/name
        subject: Campaign subject line
        sent_at: Send date/time string
        platform: Optional platform name for additional uniqueness
    
    Returns:
        A short hash-based unique ID (first 12 chars of SHA256)
    """
    if not title and not subject and not sent_at:
        # Fallback if all are empty
        return hashlib.sha256(f"{platform}_unknown".encode()).hexdigest()[:12]
    
    # Normalize the datetime
    normalized_date = normalize_datetime(sent_at)
    
    # Clean title and subject
    clean_title = re.sub(r'[^\w\s-]', '', title or "").strip()
    clean_title = re.sub(r'\s+', '_', clean_title)
    
    clean_subject = re.sub(r'[^\w\s-]', '', subject or "").strip()
    clean_subject = re.sub(r'\s+', '_', clean_subject)
    
    # Create composite string with all components
    composite = f"{clean_title}_{clean_subject}_{normalized_date}_{platform}".lower()
    
    # Generate hash
    hash_value = hashlib.sha256(composite.encode()).hexdigest()[:12]
    
    return hash_value


def generate_readable_id(title: str = "", subject: str = "", sent_at: str = "", platform: str = "") -> str:
    """
    Generate a more readable unique ID with title/subject prefix + hash.
    
    Args:
        title: Campaign title/name
        subject: Campaign subject line
        sent_at: Send date/time string
        platform: Optional platform name
    
    Returns:
        A readable ID like "my_campaign_a1b2c3d4e5f6"
    """
    # Use title if available, otherwise subject
    name = title or subject or "untitled"
    
    # Clean name to create prefix (max 30 chars)
    clean_name = re.sub(r'[^\w\s-]', '', name).strip()
    clean_name = re.sub(r'\s+', '_', clean_name).lower()
    prefix = clean_name[:30]
    
    # Generate hash for uniqueness
    hash_part = generate_unique_id(title, subject, sent_at, platform)
    
    return f"{prefix}_{hash_part}"
