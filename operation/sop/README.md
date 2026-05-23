# SOP — GPTFlow Standard Operating Procedures

## SOP-01: Daily Operations

### Morning Check (09:00 WIB)
1. Check Grafana dashboard — all green?
2. Check pending approvals queue — any stuck?
3. Check scheduled posts for today — all queued correctly?
4. Check overnight alerts — any unresolved?
5. Verify Instagram token health

### Evening Check (18:00 WIB)
1. Verify all scheduled posts for today were published
2. Check error logs for anomalies
3. Review AI generation success rate

## SOP-02: New Instagram Account Onboarding

1. Admin navigates to Settings → Accounts → Connect
2. Complete Facebook OAuth flow
3. Select Instagram Business Account
4. Verify permissions granted (publish, insights)
5. Test: generate sample content → schedule → verify
6. Assign account to relevant users

## SOP-03: Content Production Workflow

```
1. Creator: Open AI Generator
2. Creator: Input topic, audience, tone, type
3. Creator: Generate → Review → Edit if needed
4. Creator: Submit for Approval
5. Manager: Review in Approval Queue
6. Manager: Approve (or Reject with notes)
7. Creator: Schedule approved content
8. System: Auto-post at scheduled time
9. System: Fetch analytics after 24h
10. AI: Generate recommendations weekly
```

## SOP-04: Handling Failed Posts

1. System sends alert (Slack + email)
2. On-call checks error in logs
3. Common fixes:
   - Token expired → refresh token (RB-04)
   - Rate limit → wait and retry
   - Invalid media → check image URL accessibility
   - API error → check Instagram status page
4. Re-queue post after fix
5. Document if recurring issue

## SOP-05: Monthly Review

1. Review analytics dashboard (engagement trends)
2. Review AI recommendation accuracy
3. Review prompt performance (A/B test results)
4. Update knowledge base / prompt templates if needed
5. Review and rotate secrets if due
6. Update dependencies (security patches)
7. Capacity planning review

## SOP-06: User Management

### Add New User
1. Admin → Users → Invite
2. Enter email, assign role (creator/manager)
3. Assign to Instagram account(s)
4. User receives invite email → sets password
5. User completes onboarding tour

### Remove User
1. Admin → Users → Deactivate
2. Revoke all sessions
3. Reassign pending content to another user
4. Archive (don't delete) for audit trail

## SOP-07: Emergency Procedures

| Situation | Action |
|-----------|--------|
| System completely down | Follow RB-01, escalate if not resolved in 15 min |
| Data breach suspected | Revoke all tokens, enable maintenance mode, notify team |
| OpenAI API down | System auto-degrades, notify users "generation unavailable" |
| Instagram API down | Pause scheduler, queue posts, resume when API recovers |
| Database corruption | Stop writes, restore from backup (RB-06) |

## SOP-08: Release Process

1. Feature branch → PR → Code review → Merge to develop
2. Auto-deploy to staging
3. QA verification on staging (1-2 days)
4. Merge develop → main
5. Auto-deploy to production (with approval gate)
6. Monitor for 30 min post-deploy
7. If issues: rollback (RB-07)
