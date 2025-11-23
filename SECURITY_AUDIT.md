# 🔒 Security Audit Report - Nepal Entity Service

**Date**: 2025-11-23  
**Version**: 2.0.0  
**Audit Type**: Comprehensive Security Assessment  
**Severity Levels**: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low | ℹ️ Info

---

## Executive Summary

**Overall Risk Level**: 🟠 **HIGH**

The Nepal Entity Service has **8 significant security vulnerabilities** that need immediate attention before production deployment. While the application follows some security best practices (ORM usage, input validation), it lacks critical security features like authentication, rate limiting, and proper CORS configuration.

### Critical Findings
- ❌ No authentication or authorization
- ❌ Unrestricted CORS (`allow_origins=["*"]`)
- ❌ Weak default credentials in examples
- ❌ No rate limiting
- ❌ No HTTPS enforcement

---

## 🔴 CRITICAL Vulnerabilities

### 1. Missing Authentication & Authorization
**Severity**: 🔴 CRITICAL  
**CVSS Score**: 9.1 (Critical)

**Issue:**
- **No authentication system** - Anyone can access all endpoints
- **No authorization** - Anyone can create, update, or delete entities
- **No API keys or tokens** - No way to identify or restrict users

**Impact:**
- Any user can modify or delete all data
- No audit trail of who made changes
- Potential for data manipulation or destruction
- Complete lack of access control

**Location:**
- Entire API (`/api/v1/*`)
- No middleware or dependencies checking auth

**Exploit Scenario:**
```bash
# Anyone can delete all entities
curl -X DELETE http://your-api.com/api/v1/entities/{any-id}

# Anyone can create fake data
curl -X POST http://your-api.com/api/v1/entities/ \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Fake Entity","entity_type":"government"}'
```

**Remediation:**
```python
# Add authentication dependency
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not verify_jwt_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return credentials.credentials

# Apply to endpoints
@router.post("/", dependencies=[Depends(verify_token)])
async def create_entity(...):
    ...
```

**Recommended Solutions:**
1. **Immediate**: Implement JWT authentication
2. **Add**: Role-based access control (RBAC)
3. **Consider**: OAuth2 for third-party access
4. **Implement**: API key system for programmatic access

---

### 2. Unrestricted CORS Configuration
**Severity**: 🔴 CRITICAL  
**CVSS Score**: 7.5 (High)

**Issue:**
```python
# app/core/config.py
CORS_ORIGINS: List[str] = ["*"]  # ⚠️ ALLOWS ALL ORIGINS
```

**Impact:**
- Any website can make requests to your API
- Cross-Site Request Forgery (CSRF) attacks possible
- Data can be stolen from users' browsers
- No protection against malicious frontends

**Location:**
- `app/core/config.py` line 25
- `app/main.py` CORS middleware

**Remediation:**
```python
# app/core/config.py
CORS_ORIGINS: List[str] = [
    "https://yourapp.com",
    "https://www.yourapp.com",
    # Add specific trusted origins only
]

# For development only:
if settings.ENVIRONMENT == "development":
    CORS_ORIGINS.append("http://localhost:3000")
```

**Additional Security:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods
    allow_headers=["Authorization", "Content-Type"],  # Specific headers
    max_age=3600,  # Cache preflight requests
)
```

---

### 3. Weak Default Credentials
**Severity**: 🔴 CRITICAL  
**CVSS Score**: 9.8 (Critical)

**Issue:**
`.env.example` contains default credentials that are commonly used:
```env
POSTGRES_USER=nesuser
POSTGRES_PASSWORD=nespassword  # ⚠️ WEAK PASSWORD
```

**Impact:**
- If users don't change defaults, database is easily compromised
- Default credentials are publicly visible in GitHub
- Brute force attacks will succeed immediately

**Remediation:**
1. **Remove default passwords** from `.env.example`
2. **Add strong password requirements** to documentation
3. **Force password change** on first deployment

```env
# .env.example - UPDATED
POSTGRES_USER=nesuser
POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD_MIN_16_CHARS
# Generate strong password: openssl rand -base64 32
```

**Additional Security:**
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Rotate credentials regularly
- Never commit actual `.env` to Git

---

## 🟠 HIGH Severity Vulnerabilities

### 4. No Rate Limiting
**Severity**: 🟠 HIGH  
**CVSS Score**: 7.5 (High)

**Issue:**
- No protection against brute force attacks
- No protection against DoS/DDoS
- API can be abused with unlimited requests

**Impact:**
- Service can be overwhelmed with requests
- Database can be flooded
- Legitimate users locked out
- High infrastructure costs from abuse

**Remediation:**
```bash
pip install slowapi
```

```python
# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@router.post("/")
@limiter.limit("10/minute")  # 10 requests per minute
async def create_entity(...):
    ...

@router.get("/")
@limiter.limit("100/minute")  # Higher limit for reads
async def list_entities(...):
    ...
```

---

### 5. No HTTPS Enforcement
**Severity**: 🟠 HIGH  
**CVSS Score**: 7.4 (High)

**Issue:**
- No redirect from HTTP to HTTPS
- No HSTS headers
- Data transmitted in plain text

**Impact:**
- Credentials sent in clear text
- Man-in-the-middle (MITM) attacks
- Session hijacking
- Data interception

**Remediation:**
```python
# app/main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Force HTTPS in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourapp.com", "www.yourapp.com"]
    )

# Add security headers
from fastapi.middleware.cors import CORSMiddleware

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

### 6. Information Disclosure in Error Messages
**Severity**: 🟠 HIGH  
**CVSS Score**: 6.5 (Medium)

**Issue:**
Current error handling may expose sensitive information:
- Database connection strings in errors
- Stack traces in production
- Internal paths revealed

**Example:**
```python
# Current (vulnerable)
raise DatabaseError(f"Failed to create entity: {str(e)}")
# May expose: "Failed to create entity: connection to server at postgres:5432 failed"
```

**Impact:**
- Attackers learn about internal architecture
- Database info exposed
- Helps attackers plan attacks

**Remediation:**
```python
# app/core/exceptions.py
class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database operation failed", internal_detail: str = None):
        # Log internal details
        if internal_detail and settings.ENVIRONMENT != "production":
            logger.error(f"Database error: {internal_detail}")
        
        # Return generic message in production
        if settings.ENVIRONMENT == "production":
            super().__init__(status_code=500, detail="An internal error occurred")
        else:
            super().__init__(status_code=500, detail=detail)

# Usage
try:
    # database operation
except Exception as e:
    logger.error(f"Database error: {str(e)}", exc_info=True)
    raise DatabaseError(
        detail="Failed to create entity",
        internal_detail=str(e)
    )
```

---

## 🟡 MEDIUM Severity Vulnerabilities

### 7. Missing Input Sanitization
**Severity**: 🟡 MEDIUM  
**CVSS Score**: 5.3 (Medium)

**Issue:**
- No HTML/Script sanitization in text fields
- Potential for stored XSS in `description` and `metadata` fields
- No length limits on text fields

**Impact:**
- Stored XSS attacks possible
- Malicious scripts stored in database
- Frontend vulnerabilities if data rendered as HTML

**Current Code:**
```python
# No sanitization
description: Optional[str] = None  # Can contain <script> tags
```

**Remediation:**
```python
from html import escape
from pydantic import validator

class EntityBase(BaseModel):
    description: Optional[str] = Field(None, max_length=5000)
    
    @validator('description')
    def sanitize_description(cls, v):
        if v:
            # Remove or escape HTML
            return escape(v)
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        # Ensure metadata values are safe
        if v:
            for key, value in v.items():
                if isinstance(value, str):
                    v[key] = escape(value)
        return v
```

---

### 8. Exposed Database Port
**Severity**: 🟡 MEDIUM  
**CVSS Score**: 5.9 (Medium)

**Issue:**
```yaml
# docker-compose.yml
postgres:
  ports:
    - "${POSTGRES_PORT:-5432}:5432"  # ⚠️ EXPOSED TO HOST
```

**Impact:**
- PostgreSQL accessible from host machine
- Potential for direct database attacks
- Bypasses application security
- Not necessary for production

**Remediation:**
```yaml
# Remove port mapping in production
postgres:
  # ports:  # COMMENTED OUT - only API should access DB
  #   - "5432:5432"
  networks:
    - nes-network  # Internal network only
```

For debugging, use:
```bash
# Access via docker exec instead
docker-compose exec postgres psql -U nesuser -d nepal_entity_db
```

---

## 🟢 LOW Severity / Best Practices

### 9. Missing Security Headers
**Severity**: 🟢 LOW

**Missing Headers:**
- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Content-Security-Policy`
- `Permissions-Policy`

**Remediation:** See HTTPS Enforcement section above.

---

### 10. Docker Security Improvements
**Severity**: 🟢 LOW

**Issues:**
- Running as root user in container
- No read-only root filesystem
- Privileged ports exposed

**Remediation:**
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8195

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8195"]
```

---

### 11. Dependency Vulnerabilities
**Severity**: ℹ️ INFO

**Recommendation:**
Run regular security scans:

```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check --file requirements.txt

# Or use snyk
snyk test
```

---

## ✅ Security Features Already Implemented

### Good Practices Found:
1. ✅ **SQL Injection Protection** - Using SQLAlchemy ORM
2. ✅ **Input Validation** - Pydantic schemas validation
3. ✅ **Environment Variables** - Secrets not hardcoded
4. ✅ **Parameterized Queries** - ORM handles this
5. ✅ **Type Safety** - Pydantic type checking
6. ✅ **Error Handling** - Custom exceptions (recently added)
7. ✅ **`.env` in `.gitignore`** - Secrets not committed

---

## 📋 Priority Action Plan

### Immediate (Before Production):
1. 🔴 **Implement Authentication** - JWT or OAuth2
2. 🔴 **Fix CORS Configuration** - Whitelist specific origins
3. 🔴 **Change Default Credentials** - Strong passwords required
4. 🟠 **Add Rate Limiting** - Protect against abuse
5. 🟠 **Enable HTTPS** - TLS/SSL certificates

### Short Term (1-2 weeks):
6. 🟠 **Add Security Headers** - HSTS, CSP, etc.
7. 🟡 **Input Sanitization** - XSS protection
8. 🟡 **Remove DB Port Exposure** - Internal network only
9. 🟢 **Docker Hardening** - Non-root user

### Ongoing:
10. 📊 **Regular Security Audits** - Monthly reviews
11. 🔍 **Dependency Scanning** - Automated with CI/CD
12. 📝 **Security Monitoring** - Log analysis
13. 🔄 **Penetration Testing** - Before major releases

---

## 🛡️ Recommended Security Stack

```python
# requirements.txt additions
slowapi==0.1.9  # Rate limiting
python-jose[cryptography]==3.3.0  # JWT tokens
passlib[bcrypt]==1.7.4  # Password hashing
python-multipart==0.0.9  # Form data (already included)
bleach==6.1.0  # HTML sanitization
```

---

## 📊 Risk Matrix

| Vulnerability | Severity | Likelihood | Risk Level | Priority |
|--------------|----------|------------|------------|----------|
| No Authentication | Critical | High | **CRITICAL** | P0 |
| Open CORS | Critical | High | **CRITICAL** | P0 |
| Weak Credentials | Critical | Medium | **HIGH** | P0 |
| No Rate Limiting | High | High | **HIGH** | P1 |
| No HTTPS | High | Medium | **HIGH** | P1 |
| Info Disclosure | Medium | Medium | **MEDIUM** | P2 |
| Missing Sanitization | Medium | Low | **MEDIUM** | P2 |
| Exposed DB Port | Medium | Low | **LOW** | P3 |

---

## 🎯 Compliance Considerations

If this API handles sensitive data, consider:
- **GDPR** compliance (if handling EU data)
- **Data encryption** at rest and in transit
- **Audit logging** for all data access
- **Data retention** policies
- **Right to deletion** implementation

---

## 📞 Next Steps

1. **Review** this report with your team
2. **Prioritize** fixes based on deployment timeline
3. **Implement** P0 items before any public deployment
4. **Test** security measures thoroughly
5. **Monitor** for security events post-deployment

---

**Report Generated**: 2025-11-23  
**Audited By**: AI Security Analyst  
**Next Review**: When implementing fixes

⚠️ **WARNING**: Do NOT deploy to production without addressing CRITICAL vulnerabilities!
