# Recurring Tasks with Cooldown - User Guide

## 📋 Overview

Recurring tasks are household chores that need to be done regularly but not every day. Instead of appearing daily, these tasks appear once, and after completion, they enter a "cooldown period" before reappearing.

**Perfect for tasks like:**
- 🧹 Vacuuming (every 3-5 days)
- 🚗 Car wash (every 7-10 days)  
- 🧼 Deep clean bathroom (every 4-6 days)
- 💧 Water plants (every 2-3 days)
- 🗑️ Take out recycling (every 5-7 days)

---

## 🎯 How It Works

### Task Lifecycle

```
Day 1: Task Appears → Someone Completes It → Cooldown Starts (3-5 days)
Days 2-4: Task Hidden (in cooldown)
Day 5+: Task Reappears → Ready to complete again
```

### Key Features

**1. Daily Appearance Until Completion**
- Task appears in everyone's daily view
- Stays visible until someone completes it
- First-come, first-served basis

**2. Automatic Cooldown**
- After completion, task enters cooldown
- Cooldown is based on the **minimum days** configured
- Task won't reappear during cooldown

**3. Shared Completion**
- When ONE person completes the task, it's marked complete for EVERYONE
- Prevents duplicate work
- Cooldown applies to the entire family

**4. Flexible Window**
- `min_days`: Minimum wait before task can reappear (e.g., 3 days)
- `max_days`: Maximum days allowed between completions (for tracking, future feature)

---

## 🛠️ Creating Recurring Tasks

### Via Admin Panel

1. **Navigate to Admin > Tasks**
2. **Click "Add New Task"**
3. **Fill in the form:**

| Field | Example | Notes |
|-------|---------|-------|
| Task Name | `Vacuum Living Room` | Short, descriptive |
| Description | `Vacuum all carpets and floors` | What needs to be done |
| Base Points | `20` | Point value |
| Assigned To | `🏠 All Family Members` | Who can do it |
| **Schedule Type** | `Recurring (Cooldown)` | ⬅️ Select this! |
| **Minimum Days Between** | `3` | Wait at least 3 days |
| **Maximum Days Between** | `5` | Should be done within 5 days |

4. **Click "Create Task"**

### Via API

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vacuum Living Room",
    "description": "Vacuum all carpets and floors",
    "base_points": 20,
    "assigned_role_id": null,
    "schedule_type": "recurring",
    "default_due_time": "recurring",
    "recurrence_min_days": 3,
    "recurrence_max_days": 5
  }'
```

---

## 📖 Real-World Examples

### Example 1: Weekly Vacuum (3-5 day cooldown)

**Setup:**
- Task: "Vacuum Entire House"
- Base Points: 25
- Assigned To: Teenagers
- Min Days: 3
- Max Days: 5

**Timeline:**
- **Monday**: Tommy sees "Vacuum" in his tasks
- **Monday 3pm**: Tommy completes vacuuming → Gets 25 points × 1.2 multiplier = 30 points
- **Tuesday-Thursday**: Task is hidden (cooldown)
- **Friday**: Task reappears for Tommy and Sarah
- **Friday 6pm**: Sarah completes it → Gets 30 points

### Example 2: Bathroom Deep Clean (4-6 day cooldown)

**Setup:**
- Task: "Deep Clean Main Bathroom"
- Base Points: 30
- Assigned To: All Family Members
- Min Days: 4
- Max Days: 6

**Timeline:**
- **Day 1**: Everyone sees "Deep Clean Bathroom"
- **Day 1, 2pm**: Mom completes it → Gets 30 points
- **Days 2-5**: Task hidden from everyone
- **Day 6**: Task reappears

### Example 3: Car Wash (7-10 day cooldown)

**Setup:**
- Task: "Wash Family Car"
- Base Points: 35
- Assigned To: All Family Members
- Min Days: 7
- Max Days: 10

**Benefits:**
- Car gets washed roughly weekly
- Whoever has time can do it
- No duplicate washing
- Flexible window for scheduling

---

## ⚙️ Technical Details

### Validation Rules

**Required Fields for Recurring Tasks:**
- ✅ Both `recurrence_min_days` and `recurrence_max_days` must be specified
- ✅ `min_days` must be ≤ `max_days`
- ✅ Both values must be between 1-365

**Invalid Examples:**
```json
❌ { "recurrence_min_days": 5, "recurrence_max_days": 3 }  // min > max
❌ { "recurrence_min_days": 3 }  // missing max_days
❌ { "recurrence_min_days": 0, "recurrence_max_days": 5 }  // min < 1
```

### Daily Reset Behavior

When the daily reset runs each day:

1. **Check cooldown status:**
   - Find the most recent completion of the task (by ANY user)
   - Calculate days since completion
   - If `days_since < min_days`: Skip (still in cooldown)
   - If `days_since >= min_days`: Generate new instances

2. **Generate instances:**
   - Create one task instance for each eligible user
   - Set due time to 23:59 (end of day)
   - Mark as PENDING

3. **Prevent duplicates:**
   - Only create instances if no PENDING instance exists for that user/task/day

### Completion Logic

When a user completes a recurring task:

1. **Mark instance as COMPLETED**
2. **Award points** (base_points × role_multiplier)
3. **Create transaction record**
4. **Auto-complete all other pending instances** ⬅️ Key feature!
   - Finds all other PENDING instances of the same task
   - Marks them as COMPLETED (no points awarded)
   - This prevents duplicate work

---

## 🔍 Comparison with Other Schedule Types

| Feature | Daily | Weekly | Recurring |
|---------|-------|--------|-----------|
| Frequency | Every day | Specific weekday | Flexible cooldown |
| Appears when | Daily reset | Matching weekday | After cooldown |
| Completion | Individual | Individual | Shared |
| Use case | Regular chores | Weekly tasks | Periodic tasks |
| Example | Make bed | Mow lawn (Saturdays) | Vacuum (every 3-5 days) |

---

## 📊 Monitoring & Reports

### Future Features (Planned)

**Compliance Tracking:**
- Track if tasks are completed within max_days window
- Generate reports on overdue recurring tasks
- Alert if critical tasks are skipped

**Usage Analytics:**
- Who completes recurring tasks most often
- Average days between completions
- Identify tasks that might need schedule adjustments

**Automatic Scheduling:**
- Suggest optimal cooldown periods based on completion history
- Auto-adjust min/max days for better family workflow

---

## 💡 Best Practices

### Choosing Cooldown Periods

**Too Short (e.g., 1-2 days):**
- ❌ Task appears too frequently
- ❌ Feels like daily task
- ✅ Use daily schedule instead

**Optimal (e.g., 3-7 days):**
- ✅ Clear time between completions
- ✅ Doesn't feel repetitive
- ✅ Good for most household tasks

**Too Long (e.g., 20-30 days):**
- ❌ Easy to forget
- ❌ May become overdue
- ✅ Consider calendar reminders instead

### Task Assignment Tips

**Assign to Everyone (`null` role_id):**
- ✅ Flexible - anyone can do it
- ✅ Great for opportunistic tasks
- ✅ Encourages initiative

**Assign to Specific Role:**
- ✅ Ensures age-appropriate tasks
- ✅ Builds responsibility
- ✅ Clear ownership

### Point Values

**Lower Points (10-20):**
- Quick tasks (5-15 minutes)
- Regular maintenance
- Example: Water plants

**Medium Points (20-35):**
- Standard chores (15-45 minutes)
- Most household tasks
- Example: Vacuum house

**Higher Points (35-50+):**
- Major tasks (45+ minutes)
- Deep cleaning
- Example: Clean entire garage

---

## 🐛 Troubleshooting

### "Task Not Appearing After Cooldown"

**Check:**
1. Has enough time passed? Use date calculation: `(today - last_completion).days >= min_days`
2. Was the task completed recently by someone else?
3. Does a PENDING instance already exist for today?

**Solution:** Check the database or trigger another daily reset

### "Multiple Users Got Points for Same Task"

**This shouldn't happen!** The system auto-completes other instances.

**If it does:**
1. Check the `complete_task_instance` function
2. Verify the recurring task completion logic
3. Review transaction logs

### "Task Appears Every Day"

**Check:**
1. Is `schedule_type` set to "recurring"? (not "daily")
2. Are `recurrence_min_days` and `recurrence_max_days` properly set?
3. Is the cooldown check working?

**Solution:** Verify task configuration in database

---

## 🧪 Testing Recurring Tasks

### Manual Test Scenario

1. **Create test recurring task:**
   - Vacuum Floor, 3-5 day cooldown, 20 points

2. **Day 1:**
   - Trigger daily reset
   - Verify task appears for all eligible users
   - Complete task as one user
   - Verify other users' instances are auto-completed

3. **Day 2:**
   - Trigger daily reset
   - Verify NO new instances created (cooldown active)

4. **Day 4:**
   - Trigger daily reset
   - Verify NEW instances created (cooldown expired)

### Database Queries for Debugging

```sql
-- Check task configuration
SELECT * FROM tasks WHERE schedule_type = 'recurring';

-- Check recent completions
SELECT * FROM task_instances 
WHERE task_id = 1 
  AND status = 'COMPLETED' 
ORDER BY completed_at DESC 
LIMIT 5;

-- Check pending instances
SELECT * FROM task_instances 
WHERE task_id = 1 
  AND status = 'PENDING';
```

---

## 📚 Related Documentation

- [Task Management Guide](./TASK_MANAGEMENT.md)
- [Daily Schedule vs Weekly vs Recurring](./SCHEDULE_TYPES.md)
- [Point Calculation System](./POINTS_SYSTEM.md)
- [BDD Test Scenarios](../tests/features/recurring_tasks.feature)

---

**Last Updated**: 2025-12-06  
**Feature Version**: v1.0  
**Test Coverage**: 7/7 scenarios passing ✅
