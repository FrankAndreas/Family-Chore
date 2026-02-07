---
description: Trigger a manual daily reset or cron job
---

Use this workflow to manually trigger the daily reset logic (e.g., for testing or if a cron job failed).

---
**💡 Quota Recommendation**: Use **Gemini 3 Flash** for this workflow. This is a simple administrative task.
---

// turbo
1. **Trigger Backend Daily Reset**
```bash
curl -X POST http://localhost:8000/daily-reset/
```

2. **Verify Reset Status**
Check the backend logs or query the system settings to see the last reset date.
```bash
# Example check if the reset setting was updated
# (Note: This depends on having a terminal-friendly DB client or API endpoint)
curl -s http://localhost:8000/settings/language/default
```
