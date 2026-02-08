# 📖 Family Chore App - User Guide

Welcome to the Family Chore App! This guide will help you set up your family, manage chores, and start earning rewards.

---

## 🚀 Getting Started

### 1. Accessing the App
Open your web browser and navigate to the address where the app is hosted (e.g., `http://localhost:5173` or your NAS IP).

### 2. Logging In
You will see the **Login Screen**.
- **Admin**: Enter `Admin` as the nickname and `1234` as the PIN (default credentials).
- **Family Members**: Enter your assigned Nickname and PIN.

---

## 👨‍👩‍👧‍👦 For Parents (Admin)

As an Admin, you are responsible for setting up the system.

### 1. Adding Family Members
Go to **"Users"** (or "Benutzer") in the sidebar.
1. Click **"+ Add New User"**.
2. Enter a **Nickname** (e.g., "Tommy").
3. Set a **4-digit PIN** (e.g., "0000").
4. Assign a **Role**:
   - **Parent**: Can manage tasks (if authorized).
   - **Teenager / Child**: Gets point multipliers (e.g., 1.2x or 1.5x points).
5. Click **"Create User"**.

### 2. Setting Up Chores
Go to **"Tasks"** (or "Aufgaben").
1. Click **"+ Add New Task"**.
2. Fill in the details:
   - **Name**: e.g., "Empty Dishwasher".
   - **Base Points**: How much is this worth? (e.g., 10).
   - **Schedule Type**:
     - **Daily**: Appears every day (e.g., "Make Bed").
     - **Weekly**: Appears on a specific day (e.g., "Mow Lawn" on Saturdays).
     - **Recurring**: Appears periodically (e.g., "Vacuum" every 3-5 days).
3. **Assign To**: Choose specific people or "All Family Members".
4. Click **"Create Task"**.

### 3. Import & Export Tasks
Use **Export** and **Import** to manage tasks in bulk:

**📤 Export Tasks**
1. Go to **"Tasks"** and click **"Export"**.
2. A JSON file downloads with all your tasks.
3. Use this for backups or as a template for AI-generated tasks.

**📥 Import Tasks**
1. Click **"Import"** to open the import modal.
2. Paste JSON or click **"Upload File"** to load a JSON file.
3. Review the preview showing tasks to be created.
4. Check **"Skip duplicates"** to avoid creating tasks that already exist.
5. Click **"Import"** to create the tasks.

**💡 Tip:** Export your tasks, then ask ChatGPT: *"Create 5 meal prep tasks following this format..."* and paste the JSON. Import the AI's response to quickly add new tasks!

### 4. Creating Rewards
Go to **"Rewards"** (or "Belohnungen").
1. Click **"+ Add New Reward"**.
2. Enter details:
   - **Name**: e.g., "Ice Cream", "Extra Screen Time".
   - **Cost**: Points required (e.g., 50).
   - **Tier**: Bronze/Silver/Gold (affects badge color).
3. Click **"Create Reward"**.

### 5. System Settings
Go to **"Settings"** (or "Einstellungen").
- **Language**: Change the language for the whole family or just for your session (English or German).

---

## 🧒 For Kids (Users)

Your goal is to complete tasks, earn points, and get rewards!

### 1. Checking Your Tasks
Go to **"Dashboard"** or **"Tasks"**.
- You will see **"My Daily Tasks"**.
- These are the chores you need to do **today**.

### 2. Completing a Task
1. Do the chore in real life (e.g., make your bed).
2. Go to the app and find the task card.
3. Click **"Mark Complete"** (or the checkmark button).
4. 🎉 **Success!** You instantly get points added to your score.

### 3. Setting a Goal
Go to **"Rewards"**.
1. Browse the rewards your parents created.
2. Find one you really want.
3. Click **"Set as Goal"**.
4. This reward will now appear on your Dashboard with a progress bar showing how close you are!

### 4. Redeeming Rewards
Go to the **Dashboard** and switch to the **"Redeem"** tab.
1. Browse rewards you can afford.
2. Click **"Redeem"** on a reward you want.
3. Confirm the redemption to instantly deduct points and notify your parents!

##### 🎁 Split Redemption
You can pool points with siblings or parents to buy a big reward together!
1. Click **"Redeem"** on a reward.
2. In the popup, use the **Split Evenly** button or adjust each person's contribution manually.
3. Once the total matches the cost, click **"Redeem"** to share the cost!

---

## 💡 Concepts Explained

### 📅 Schedule Types
- **Daily**: Resets every night. If you miss it, it’s gone.
- **Weekly**: Only appears on the chosen day.
- **Recurring**: These have a "Cooldown". If you do it today, it disappears for a few days (e.g., 3 days) before appearing again. First person to do it gets the points!

### 🏆 Roles & Multipliers
Different roles can earn points differently to make it fair.
- **Child**: Might get **1.5x points** (harder for them!).
- **Teenager**: Might get **1.2x points**.
- **Admin**: Usually 1.0x.

### 🔄 Daily Reset
The system refreshes every night at midnight.
- Completed tasks are cleared.
- New Daily tasks serve up.
- Recurring tasks check if their cooldown is over.

---

## ❓ FAQ

**Q: I completed a task by mistake. Can I undo it?**
A: Currently, task completion is final for the day. Ask an Admin to adjust your points if needed.

**Q: Why can't I see a Recurring Task?**
A: Someone else might have done it recently, so it's in "Cooldown". Wait a few days!

**Q: How do I change the language to German?**
A: Go to the **Settings** page and select "Deutsch". You can set it as your personal preference or the family default.

---
*Generated for ChoreSpec v1.0*
