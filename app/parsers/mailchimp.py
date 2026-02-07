import csv
from io import StringIO
from datetime import datetime


def parse_mailchimp(text: str):
    """Parse MailChimp CSV campaign report."""
    reader = csv.DictReader(StringIO(text))
    campaigns = []
    
    for row in reader:
        try:
            # Parse send date
            sent_at = row.get('Send Date', '')
            
            # Parse delivered (Successful Deliveries)
            delivered = int(row.get('Successful Deliveries', 0))
            
            # Parse open rate
            open_rate_str = row.get('Open Rate', '0%').strip('%')
            open_rate = float(open_rate_str) / 100 if open_rate_str else 0
            
            # Parse unique opens
            opens = int(row.get('Unique Opens', 0))
            
            # Parse click rate
            click_rate_str = row.get('Click Rate', '0%').strip('%')
            click_rate = float(click_rate_str) / 100 if click_rate_str else 0
            
            # Parse unique clicks
            clicks = int(row.get('Unique Clicks', 0))
            
            # Parse bounces
            hard_bounces = int(row.get('Hard Bounces', 0))
            soft_bounces = int(row.get('Soft Bounces', 0))
            
            # Parse unsubscribes
            unsubscribes = int(row.get('Unsubscribes', 0))
            
            # Parse spam complaints
            spam_complaints = int(row.get('Abuse Complaints', 0))
            
            # Calculate rates
            hard_bounce_rate = hard_bounces / delivered if delivered > 0 else 0
            soft_bounce_rate = soft_bounces / delivered if delivered > 0 else 0
            unsubscribe_rate = unsubscribes / delivered if delivered > 0 else 0
            
            # Calculate CTOR
            ctor = clicks / opens if opens > 0 else 0
            
            campaign = {
                "platform": "mailchimp",
                "subject": row.get('Subject', ''),
                "email_title": row.get('Title', ''),
                "unique_id": row.get('Unique Id', ''),
                "sent_at": sent_at,
                "delivered": delivered,
                "opens": opens,
                "open_rate": open_rate,
                "clicks": clicks,
                "click_rate": click_rate,
                "ctor": ctor,
                "unsubscribes": unsubscribes,
                "unsubscribe_rate": unsubscribe_rate,
                "spam_complaints": spam_complaints,
                "hard_bounces": hard_bounces,
                "hard_bounce_rate": hard_bounce_rate,
                "soft_bounces": soft_bounces,
                "soft_bounce_rate": soft_bounce_rate,
            }
            
            campaigns.append(campaign)
            
        except (ValueError, KeyError) as e:
            # Skip rows that can't be parsed
            continue
    
    return {
        "campaigns": campaigns
    }
