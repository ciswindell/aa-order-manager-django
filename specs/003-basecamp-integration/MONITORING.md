# Basecamp Integration: Monitoring & Alerting

## Overview

This document outlines monitoring and alerting considerations for the Basecamp OAuth integration to ensure production reliability and meet success criteria (SC-003: 95% token refresh success rate).

## Key Metrics to Monitor

### 1. Token Refresh Success Rate (Critical - SC-003)

**Metric**: `basecamp_token_refresh_success_rate`  
**Target**: ≥95%  
**Calculation**: `(successful_refreshes / total_refresh_attempts) * 100`

**Alert Conditions**:
- **WARNING**: Success rate drops below 95% over 1-hour window
- **CRITICAL**: Success rate drops below 90% over 1-hour window
- **CRITICAL**: 5+ consecutive refresh failures for any user

**Log Patterns to Track**:
```
Basecamp token refresh successful | user_id=%s | account_id=%s
Basecamp token refresh failed | user_id=%s | error=%s
```

**Recommended Actions**:
- Check Basecamp API status
- Verify OAuth credentials are valid
- Review error logs for patterns (rate limiting, network issues)
- Consider increasing exponential backoff delays

### 2. OAuth Flow Completion Rate

**Metric**: `basecamp_oauth_completion_rate`  
**Target**: ≥90% (SC-006: 90% first-time success)  
**Calculation**: `(successful_connections / initiated_connections) * 100`

**Alert Conditions**:
- **WARNING**: Completion rate drops below 90% over 24-hour window
- **CRITICAL**: No successful OAuth completions in past hour during business hours

**Log Patterns to Track**:
```
Basecamp OAuth connect initiated | user_id=%s
Basecamp OAuth connection successful | user_id=%s | account_id=%s
Basecamp OAuth callback exception | user_id=%s | error=%s
```

**Common Failure Reasons**:
- State parameter mismatch (CSRF)
- Session expiration
- Invalid OAuth credentials
- User cancellation

### 3. OAuth Flow Duration (SC-001)

**Metric**: `basecamp_oauth_flow_duration_seconds`  
**Target**: <120 seconds (2 minutes)  
**Measurement**: Time from connect initiation to callback completion

**Alert Conditions**:
- **WARNING**: P95 duration exceeds 120 seconds
- **CRITICAL**: P95 duration exceeds 180 seconds

**Optimization Opportunities**:
- Reduce token exchange timeout
- Optimize database writes
- Cache OAuth credentials lookup

### 4. Status Check Response Time (SC-002)

**Metric**: `basecamp_status_check_duration_ms`  
**Target**: <1000ms (1 second)  
**Measurement**: Time to return status from `/api/integrations/basecamp/status/`

**Alert Conditions**:
- **WARNING**: P95 response time exceeds 1 second
- **CRITICAL**: P95 response time exceeds 2 seconds

**Log Patterns to Track**:
```
Integration status check | provider=basecamp | duration_ms=%d
```

**Optimization**:
- Verify status caching is working (ttl_seconds=600)
- Check database query performance
- Monitor cache hit rate

### 5. API Rate Limiting

**Metric**: `basecamp_rate_limit_hits`  
**Target**: 0 (ideally) or <5% of requests  

**Alert Conditions**:
- **WARNING**: Rate limit (HTTP 429) encountered
- **CRITICAL**: 10+ rate limit hits in 1-hour window

**Log Patterns to Track**:
```
Basecamp rate limit hit (429) | attempt=%d/%d | retry_after=%s
Basecamp API request failed after %d attempts | error=%s
```

**Recommended Actions**:
- Review exponential backoff implementation
- Consider request throttling
- Check for excessive API calls in application logic

### 6. Error Rate by Type

**Metrics**:
- `basecamp_oauth_errors_by_type{error_type}`
- `basecamp_auth_errors_by_type{error_type}`

**Common Error Types**:
- `invalid_state`: CSRF validation failures
- `token_exchange_failed`: OAuth code exchange failures
- `session_expired`: Session timeout during OAuth
- `account_already_connected`: Duplicate connection attempts
- `authorization_failed`: User denied access

**Alert Conditions**:
- **WARNING**: Any error type exceeds 10% of requests for that operation
- **CRITICAL**: Any error type exceeds 25% of requests

### 7. Account Health

**Metrics**:
- `basecamp_connected_accounts_total`: Total active connections
- `basecamp_expired_accounts_total`: Accounts with expired tokens
- `basecamp_disconnection_rate`: Accounts disconnected per day

**Alert Conditions**:
- **WARNING**: >5% of accounts have expired tokens
- **CRITICAL**: >10% of accounts have expired tokens
- **WARNING**: Disconnection rate spike (>3x average)

## Logging Strategy (FR-016)

### Required Log Fields

All Basecamp authentication events must include:

```json
{
  "timestamp": "2025-10-27T12:00:00Z",
  "level": "INFO|WARNING|ERROR",
  "event": "basecamp_oauth_connect|basecamp_token_refresh|...",
  "user_id": 123,
  "account_id": "888888",
  "status": "success|failure",
  "duration_ms": 250,
  "error": "optional_error_message",
  "metadata": {
    "attempt": 1,
    "max_retries": 3,
    "http_status": 200
  }
}
```

### Log Levels

- **INFO**: Successful operations (connect, disconnect, refresh, status check)
- **WARNING**: Retryable failures, rate limiting, account already connected
- **ERROR**: Fatal errors requiring investigation (OAuth failures, token exchange errors)

### Log Retention

- **INFO logs**: 30 days
- **WARNING logs**: 60 days
- **ERROR logs**: 90 days

## Alerting Channels

### Priority Levels

1. **CRITICAL** → PagerDuty/On-call + Slack #alerts
2. **WARNING** → Slack #monitoring
3. **INFO** → Dashboard only

### Alert Escalation

1. **CRITICAL alert**: Immediate notification
2. **No acknowledgment in 15 min**: Escalate to secondary on-call
3. **Issue persists 1 hour**: Escalate to engineering lead

## Dashboards

### Primary Dashboard: Basecamp Integration Health

**Panels**:
1. Token Refresh Success Rate (line chart, 24h)
2. OAuth Flow Completion Rate (line chart, 24h)
3. Active Connections (gauge)
4. Expired Accounts (gauge)
5. Error Rate by Type (stacked area chart, 24h)
6. API Response Times P50/P95/P99 (line chart, 24h)
7. Rate Limit Hits (bar chart, 7d)

### Secondary Dashboard: OAuth Flow Details

**Panels**:
1. OAuth Flow Duration Distribution (histogram)
2. Connection Success/Failure by Hour (heatmap)
3. Recent Failed Connections (table with error messages)
4. State Validation Failures (counter)
5. Session Expiration Rate (line chart)

## Production Readiness Checklist

- [ ] Logging integrated with centralized log aggregation (e.g., ELK, Datadog)
- [ ] Metrics exported to monitoring system (e.g., Prometheus, Datadog)
- [ ] Dashboards created in monitoring tool
- [ ] Alerts configured with appropriate thresholds
- [ ] On-call rotation includes Basecamp integration knowledge
- [ ] Runbook created for common failure scenarios
- [ ] Health check endpoint includes Basecamp status
- [ ] Status page updated to include Basecamp integration

## Runbook: Common Issues

### Issue 1: Token Refresh Failure Spike

**Symptoms**: Sudden increase in token refresh failures

**Investigation**:
1. Check Basecamp API status: https://status.basecamp.com
2. Review error logs for common error messages
3. Verify OAuth credentials are valid
4. Check network connectivity to Basecamp API

**Resolution**:
- If Basecamp API down: Wait for recovery, users can re-authenticate
- If credentials invalid: Rotate OAuth credentials
- If network issues: Check firewall/proxy configuration

### Issue 2: OAuth Flow Failures

**Symptoms**: Users unable to connect Basecamp accounts

**Investigation**:
1. Check recent failed callback logs
2. Verify OAuth redirect URI matches registered value
3. Check session middleware configuration
4. Test OAuth flow manually

**Resolution**:
- Update redirect URI if changed
- Verify session configuration (cookies, secure flag)
- Clear affected user sessions if state mismatch

### Issue 3: Status Check Timeout

**Symptoms**: Slow status endpoint responses

**Investigation**:
1. Check database query performance
2. Verify status cache is working
3. Review database connection pool

**Resolution**:
- Add database indexes if missing
- Increase cache TTL if appropriate
- Scale database connections if needed

## Audit Trail

All Basecamp authentication events are logged with metadata for compliance and troubleshooting (FR-016):

- User ID
- Timestamp (ISO 8601, UTC)
- Action (connect, disconnect, refresh, status)
- Status (success/failure)
- Account ID (if applicable)
- Error details (if failure)

**Audit log query examples**:
```sql
-- Recent token refresh failures
SELECT timestamp, user_id, account_id, error
FROM auth_events
WHERE event = 'basecamp_token_refresh' AND status = 'failure'
ORDER BY timestamp DESC
LIMIT 50;

-- Connection success rate by day
SELECT DATE(timestamp) as date,
       COUNT(*) as total,
       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
       ROUND(100.0 * SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM auth_events
WHERE event = 'basecamp_oauth_connect'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## Performance Targets Summary

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Token Refresh Success Rate | ≥95% | <95% (WARNING), <90% (CRITICAL) |
| OAuth Completion Rate | ≥90% | <90% (WARNING), <85% (CRITICAL) |
| OAuth Flow Duration (P95) | <120s | >120s (WARNING), >180s (CRITICAL) |
| Status Check Time (P95) | <1s | >1s (WARNING), >2s (CRITICAL) |
| Rate Limit Hits | 0 | >0 (WARNING), >10/hour (CRITICAL) |
| Expired Accounts | <5% | >5% (WARNING), >10% (CRITICAL) |

## Review Schedule

- **Daily**: Review error logs and alert trends
- **Weekly**: Check metric trends and dashboard health
- **Monthly**: Review alert thresholds and adjust if needed
- **Quarterly**: Full monitoring system audit and improvement planning

