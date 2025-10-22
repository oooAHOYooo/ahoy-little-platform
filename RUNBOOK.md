# Incident Response & Operations Runbook

## Emergency Contacts
- **Primary On-Call:** primary@ahoy.example (+1-555-0100)
- **Secondary On-Call:** secondary@ahoy.example (+1-555-0101)
- **Engineering Manager:** manager@ahoy.example (+1-555-0102)
- **CTO:** cto@ahoy.example (+1-555-0103)

## Rollback Procedures

### Render.com Rollback
1. **Access Render Dashboard:** https://dashboard.render.com
2. **Navigate to Service:** Select "ahoy-indie-media" service
3. **Go to Deploys Tab:** Click "Deploys" in left sidebar
4. **Select Previous Deploy:** Click on the last known good deployment
5. **Redeploy:** Click "Redeploy" button
6. **Verify:** Check `/healthz` endpoint returns 200
7. **Monitor:** Watch logs for 5 minutes for stability

### Git Tag Rollback
```bash
# Rollback to previous version
git checkout v0.1.0
git push origin main --force

# Or create hotfix branch
git checkout -b hotfix/rollback-$(date +%Y%m%d)
git revert HEAD
git push origin hotfix/rollback-$(date +%Y%m%d)
```

## Feature Flag Controls

### Disable User Signup
1. **Via Environment Variable:**
   ```bash
   # Set in Render dashboard
   DISABLE_SIGNUP=true
   ```
2. **Via Database (if needed):**
   ```sql
   -- Add maintenance mode flag
   INSERT INTO app_settings (key, value) VALUES ('maintenance_mode', 'true');
   ```
3. **Verify:** Check that `/api/auth/register` returns 503

### Lock Down Media Access
1. **Enable Signed URLs:**
   ```bash
   # Set in Render dashboard
   ENABLE_SIGNED_URLS=true
   SIGNED_URL_EXPIRY=3600
   ```
2. **Restrict Direct Access:**
   ```bash
   # Block direct media access
   BLOCK_DIRECT_MEDIA=true
   ```
3. **Verify:** Check that direct media URLs return 403

### Rate Limiting Controls
1. **Emergency Rate Limiting:**
   ```bash
   # Set aggressive limits
   RATE_LIMIT_DEFAULT=10 per minute
   RATE_LIMIT_AUTH=3 per minute
   ```
2. **Block Specific IPs:**
   ```bash
   # Add to blocked IPs list
   BLOCKED_IPS=192.168.1.100,10.0.0.50
   ```

## Secret Rotation

### Rotate SECRET_KEY
1. **Generate New Key:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. **Update Render Environment:**
   - Go to Render dashboard → Service → Environment
   - Update `SECRET_KEY` value
   - Redeploy service
3. **Invalidate Sessions:**
   ```bash
   # Clear all user sessions
   REDIS_CLI FLUSHDB
   # Or restart service to clear in-memory sessions
   ```

### Rotate Database Credentials
1. **Create New Database User:**
   ```sql
   CREATE USER ahoy_new WITH PASSWORD 'new_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE ahoy_prod TO ahoy_new;
   ```
2. **Update DATABASE_URL:**
   - Update in Render environment variables
   - Test connection with new credentials
   - Redeploy service
3. **Remove Old User:**
   ```sql
   DROP USER ahoy_old;
   ```

## Incident Severity Levels

### Severity 1 (Critical) - 5 min response
- Complete service outage
- Data loss or corruption
- Security breach
- Payment processing failure

### Severity 2 (High) - 30 min response
- Significant feature degradation
- Performance issues affecting >50% users
- Authentication problems
- Database connectivity issues

### Severity 3 (Medium) - 4 hour response
- Minor feature issues
- Cosmetic problems
- Non-critical performance issues
- Documentation updates needed

## Communication Templates

### Initial Alert
```
🚨 INCIDENT ALERT - [SEVERITY] - [TITLE]
Time: [TIMESTAMP]
Service: Ahoy Indie Media
Status: Investigating
Impact: [DESCRIPTION]
On-Call: [ENGINEER_NAME]
```

### Status Update
```
📊 INCIDENT UPDATE - [TITLE]
Time: [TIMESTAMP]
Status: [INVESTIGATING/MITIGATING/RESOLVED]
Progress: [CURRENT_ACTIONS]
ETA: [ESTIMATED_RESOLUTION]
```

### Resolution
```
✅ INCIDENT RESOLVED - [TITLE]
Time: [TIMESTAMP]
Duration: [DOWNTIME]
Root Cause: [BRIEF_DESCRIPTION]
Action Items: [FOLLOW_UP_TASKS]
```

## Post-Incident Process

1. **Immediate (0-1 hour):** Restore service, communicate status
2. **Within 24 hours:** Post-incident review meeting
3. **Within 48 hours:** Root cause analysis document
4. **Within 1 week:** Action items and prevention measures
5. **Within 2 weeks:** Process improvements implementation

## Monitoring & Alerts

### Key Metrics to Watch
- Response time > 2 seconds
- Error rate > 5%
- Database connections > 80%
- Memory usage > 90%
- Disk space < 20% free

### Alert Channels
- **Email:** oncall@ahoy.example
- **Slack:** #incidents channel
- **SMS:** Via PagerDuty integration
- **Phone:** Emergency escalation only
