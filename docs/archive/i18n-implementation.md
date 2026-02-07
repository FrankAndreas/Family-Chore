# Internationalization (i18n) Implementation - Status

**Started**: 2025-12-28 20:35 CET  
**Goal**: German translation + configurable language (family-wide + per-user override)

---

## ✅ Completed

### 1. **i18n Infrastructure Setup**
- ✅ Installed `i18next`, `react-i18next`, `i18next-browser-languagedetector`
- ✅ Created i18n configuration (`/frontend/src/i18n.ts`)
- ✅ Language detection from localStorage or browser
- ✅ Fallback to English

### 2. **Translation Files Created**
- ✅ `/frontend/src/locales/en.json` - Complete English translations
- ✅ `/frontend/src/locales/de.json` - Complete German translations

**Coverage**: All UI strings translated for:
- Common elements (buttons, labels)
- Login page
- Navigation
- Dashboard
- Tasks (creation, editing, completion)
- Rewards
- Users
- Roles
- Settings
- Weekdays

### 3. **Database Schema Updates**
- ✅ Added `SystemSettings` model for family-wide settings
- ✅ Added `preferred_language` field to `User` model
- ✅ Updated Pydantic schemas:
  - `SystemSettings` schema
  - `UserLanguageUpdate` schema
  - Added `preferred_language` to `User` schema

---

## 🚧 Remaining Work

### 4. **Database Migration** ⚠️ REQUIRED NEXT
**What**: Create tables and add new columns
**How**:
```bash
cd /home/andreas/work/family-chore
./venv/bin/python backend/init_db.py
```

Or manually:
```sql
-- Create system_settings table
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY,
    key VARCHAR NOT NULL UNIQUE,
    value VARCHAR NOT NULL,
    description TEXT
);

-- Add preferred_language column to users table  
ALTER TABLE users ADD COLUMN preferred_language VARCHAR;

-- Set default language for family
INSERT INTO system_settings (key, value, description) 
VALUES ('default_language', 'de', 'Family default language (en or de)');
```

### 5. **Backend API Endpoints**
Need to add:
```python
# In backend/main.py:

# Get system settings
@app.get("/settings/language/default")
def get_default_language(db: Session = Depends(get_db)):
    ...

# Set system default language (Admin only)
@app.put("/settings/language/default")
def set_default_language(language: str, db: Session = Depends(get_db)):
    ...

# Get user's language preference
@app.get("/users/{user_id}/language")
def get_user_language(user_id: int, db: Session = Depends(get_db)):
    ...

# Update user's language preference
@app.put("/users/{user_id}/language")
def update_user_language(user_id: int, lang_update: schemas.UserLanguageUpdate, db: Session = Depends(get_db)):
    ...
```

### 6. **Frontend Integration**
Need to:
- Import i18n in `main.tsx`
- Wrap App with I18nextProvider
- Replace all hard-coded strings with `useTranslation()` hook
- Create LanguageSwitcher component
- Add Settings page for language configuration
- Update User type to include `preferred_language`

### 7. **Components to Update**
- `/frontend/src/main.tsx` - Import i18n
- `/frontend/src/App.tsx` - Wrap with provider
- `/frontend/src/components/Login.tsx` - Use translations
- `/frontend/src/layouts/DashboardLayout.tsx` - Use translations
- `/frontend/src/pages/admin/AdminDashboard.tsx` - Use translations
- `/frontend/src/pages/admin/TaskManagement.tsx` - Use translations
- `/frontend/src/pages/admin/UserManagement.tsx` - Use translations
- `/frontend/src/pages/admin/RoleManagement.tsx` - Use translations
- `/frontend/src/pages/user/UserDashboard.tsx` - Use translations
- `/frontend/src/pages/user/RewardHub.tsx` - Use translations

### 8. **Create LanguageSwitcher Component**
```tsx
// /frontend/src/components/LanguageSwitcher.tsx
// Dropdown to switch between EN/DE
// Shows current selection
// Updates localStorage and i18n instance
```

### 9. **Create Settings Page**
```tsx
// /frontend/src/pages/admin/Settings.tsx
// Admin: Set family default language
// User: Override with personal preference
```

---

## 📋 Quick Start Guide (For Next Session)

### **Step 1: Run Database Migration**
```bash
cd /home/andreas/work/family-chore
./venv/bin/python backend/init_db.py
```

### **Step 2: Import i18n in main.tsx**
```tsx
import './i18n';  // At the top
```

### **Step 3: Start Using Translations**
Example:
```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return <h1>{t('tasks.title')}</h1>;
}
```

---

## 🎯 Implementation Priority

1. **Run DB migration** (critical)
2. **Add backend API endpoints** for language settings
3. **Update main.tsx** to import i18n
4. **Create LanguageSwitcher** component 
5. **Update one page** as proof-of-concept (e.g., Login)
6. **Systematically update all pages**
7. **Add Settings page** for configuration
8. **Test both languages thoroughly**

---

## 🔍 Translation Key Structure

All translations are available via:
- `t('common.loading')` → "Loading..." / "Lädt..."
- `t('tasks.title')` → "Task Management" / "Aufgabenverwaltung"
- `t('tasks.messages.created')` → "Task created successfully! 🎉"
- `t('weekdays.monday')` → "Monday" / "Montag"

With interpolation:
- `t('dashboard.welcome', { name: 'Andreas' })` → "Welcome, Andreas!" / "Willkommen, Andreas!"

---

## 💡 Design Notes

- **Family Default**: Set via Settings page (Admin only)
- **User Override**: Each user can override in their profile
- **Fallback**: Always falls back to English if key missing
- **Persistence**: Stored in localStorage as `chorespec_language`
- **Backend Storage**: 
  - `system_settings.default_language` = family default
  - `users.preferred_language` = per-user override (null = use default)

---

**Status**: Foundation Complete, Integration Pending  
**Estimated Remaining Time**: 1-2 hours for full integration
