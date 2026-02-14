# Security Hardening for Simple Dash

This document outlines the security measures implemented in Simple Dash, especially for production deployment behind Cloudflare.

## Implemented Security Measures

### 1. Rate Limiting

**What it does:**

- Limits API requests to prevent abuse and DoS attacks
- Works with Cloudflare proxy by reading `CF-Connecting-IP` header

**Configuration:**

- `/parse` endpoint: **10 requests per minute per IP**
- Automatically returns `429 Too Many Requests` when exceeded

**To adjust rate limits:**
Edit `app/main.py` and change the decorator:

```python
@limiter.limit("10/minute")  # Change to "20/minute" or "5/minute" etc.
```

### 2. Cloudflare IP Detection

**How it works:**

- Reads real client IP from Cloudflare headers (`CF-Connecting-IP`)
- Falls back to `X-Forwarded-For` if Cloudflare header is missing
- Prevents rate limit bypass by spoofing IPs

### 3. File Upload Limits

**Protections:**

- Maximum file size: 10MB per file (configurable)
- Maximum files per upload: 12 files
- Maximum total upload size: 120MB (10MB × 12 files)
- Only CSV files accepted
- Total size validation before processing

### 4. CORS Restrictions

**Production mode:**

- Only allows requests from your domain
- Restricts HTTP methods to GET and POST only

**To configure:**
Edit `app/main.py` and update:

```python
allowed_origins = ["*"] if DEV else [
    "https://yourdomain.com",      # Replace with your domain
    "https://www.yourdomain.com"
]
```

### 5. API Documentation Disabled

**Security through obscurity:**

- `/docs` endpoint disabled
- `/redoc` endpoint disabled
- `/openapi.json` endpoint disabled

This prevents attackers from easily discovering API structure.

### 6. Memory Protection

- Files are read and validated before processing
- Total upload size checked to prevent memory exhaustion
- File contents stored temporarily, not streamed

---

## Additional Cloudflare Protections (Recommended)

### Enable These in Cloudflare Dashboard:

1. **SSL/TLS Mode:**
   - Set to "Full (strict)" or "Full"

2. **WAF (Web Application Firewall):**
   - Enable Cloudflare Managed Ruleset
   - Consider enabling "OWASP Core Ruleset"

3. **Bot Fight Mode:**
   - Enable to block known bad bots
   - Free tier includes basic bot protection

4. **Challenge Passage:**
   - Set to 30 minutes or 1 hour
   - Reduces repeat challenges for legitimate users

5. **Security Level:**
   - Set to "Medium" or "High"
   - Challenges suspicious requests

6. **DDoS Protection:**
   - Automatically enabled by Cloudflare
   - No configuration needed

7. **Rate Limiting (Cloudflare):**
   - Additional layer on top of application rate limiting
   - Example rule: Max 30 requests per minute to `/parse`

8. **Browser Integrity Check:**
   - Enable to block requests without valid browser signatures

---

## Environment Variables

Set these in your production environment:

```bash
# Disable development mode
DEV=false

# File limits (optional, defaults shown)
MAX_FILE_SIZE=10485760  # 10MB in bytes
MAX_FILES=12
```

---

## Testing Rate Limiting

Test that rate limiting works:

```bash
# Make 11 requests quickly (should see 429 on 11th)
for i in {1..101}; do
  curl -X GET https://simplepixel.wooprojects.com/p/b8b6fe0e-465d-4698-a80a-3a384e2d5cd9.gif \
    -w "\nResponse code: %{http_code}\n"
done
```

---

## Monitoring Recommendations

1. **Set up alerts for:**
   - High rate of 429 errors (possible attack)
   - High rate of 413 errors (large file attacks)
   - Unusual traffic spikes

2. **Monitor Cloudflare Analytics:**
   - Check for unusual traffic patterns
   - Review blocked requests
   - Monitor bandwidth usage

3. **Application logs:**
   - Log all rate limit violations
   - Log file validation failures
   - Monitor error rates

---

## Incident Response

**If under attack:**

1. **Immediate:**
   - Enable "I'm Under Attack Mode" in Cloudflare (Security > Settings)
   - Reduce rate limits temporarily (e.g., `"5/minute"`)

2. **Investigate:**
   - Check Cloudflare firewall events
   - Review application logs
   - Identify attack patterns

3. **Block:**
   - Create Cloudflare firewall rules to block malicious IPs
   - Block specific countries if needed (Security > WAF > Tools)

4. **Long-term:**
   - Adjust rate limits based on legitimate usage patterns
   - Consider implementing user accounts with higher limits

---

## Additional Hardening (Optional)

### 1. Add Request Signing

For API clients, implement HMAC request signing:

```python
# Requires shared secret between client and server
# Prevents replay attacks and unauthorized access
```

### 2. Implement Caching

Cache parsed results to reduce server load:

```python
# Use Redis or similar for temporary caching
# Cache key: hash of file contents
```

### 3. Add Logging

Log security events:

```python
import logging

logger = logging.getLogger(__name__)

# Log rate limit violations
# Log suspicious file uploads
# Log parsing errors
```

### 4. Health Check Monitoring

Set up monitoring for `/health` endpoint:

- Use UptimeRobot, Pingdom, or similar
- Alert if endpoint returns non-200 status
- Alert if response time exceeds threshold

---

## Summary

✅ **Already protected against:**

- DoS attacks (rate limiting)
- Large file attacks (size limits)
- Memory exhaustion (total size validation)
- IP spoofing (Cloudflare header detection)
- CORS attacks (origin restrictions in production)

⚠️ **You should configure:**

1. Update CORS allowed origins with your domain
2. Enable Cloudflare WAF and security features
3. Set up monitoring and alerts
4. Set `DEV=false` in production

🔒 **Consider for future:**

- User authentication for higher rate limits
- Request signing for API clients
- Result caching to reduce server load
- Comprehensive logging and monitoring
