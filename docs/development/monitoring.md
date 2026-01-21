# Monitoring & Incident Response

## Alert Rules

### Sentry Error Rate Alert
- **Rule:** Error rate > 10 errors/minute for 5 consecutive minutes
- **Severity:** Critical
- **Notification:** Email to on-call engineer
- **Escalation:** If no acknowledgment in 15 minutes, page backup engineer

### Uptime Monitoring
- **Service:** UptimeRobot or BetterStack
- **Endpoint:** `https://ahoy-indie-media.onrender.com/healthz`
- **Frequency:** Every 60 seconds
- **Timeout:** 30 seconds
- **Alert:** If 3 consecutive failures, send notification

## On-Call Rotation

### Primary (Week 1-2)
- **Email:** primary@ahoy.example
- **Phone:** +1-555-0100
- **Slack:** @primary-oncall

### Secondary (Week 3-4)  
- **Email:** secondary@ahoy.example
- **Phone:** +1-555-0101
- **Slack:** @secondary-oncall

## Escalation Steps

1. **Level 1 (0-15 min):** Primary on-call engineer
2. **Level 2 (15-30 min):** Secondary + Engineering Manager
3. **Level 3 (30+ min):** CTO + Full engineering team

## Incident Response

### Severity 1 (Critical)
- **Definition:** Complete service outage, data loss, security breach
- **Response Time:** 5 minutes
- **Communication:** Immediate Slack alert + SMS

### Severity 2 (High)
- **Definition:** Significant feature degradation, performance issues
- **Response Time:** 30 minutes
- **Communication:** Slack alert within 15 minutes

### Severity 3 (Medium)
- **Definition:** Minor feature issues, cosmetic problems
- **Response Time:** 4 hours
- **Communication:** Slack alert within 1 hour

## Post-Incident Process

1. **Immediate:** Restore service
2. **Within 24h:** Post-incident review meeting
3. **Within 48h:** Root cause analysis document
4. **Within 1 week:** Action items and prevention measures

## Monitoring Tools

- **Application:** Sentry (error tracking)
- **Uptime:** UptimeRobot (external monitoring)
- **Logs:** Render logs + structured logging
- **Metrics:** Custom health endpoints
- **Alerts:** Email + Slack integration
