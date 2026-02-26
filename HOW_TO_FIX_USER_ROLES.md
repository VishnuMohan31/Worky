# How to Fix User Roles - Step by Step

## The Problem

When you try to create a user with these roles:
- HR
- DevOps
- Owner
- Product Manager
- Contact Person

You get this error:
```
❌ 500 Internal Server Error
```

## The Solution (3 Steps)

### Step 1: Make Sure Application is Running

```bash
cd App_Development_scripts/New_development_scripts
./01_startup_complete_application.sh
```

Wait for all services to start (about 30-60 seconds).

### Step 2: Run the Fix Script

```bash
cd ../..  # Go back to project root
./fix_user_roles_constraint.sh
```

You should see:
```
✓ User roles constraint fixed successfully!
```

### Step 3: Test It

Open your browser and:
1. Go to `http://localhost:3000`
2. Login as Admin:
   - Email: `admin@datalegos.com`
   - Password: `admin123`
3. Click "Users" in the sidebar
4. Click "+ Add User"
5. Fill in:
   - Full Name: `HR Manager`
   - Email: `hr@example.com`
   - Role: Select "HR"
6. Click "Create User"

You should see:
```
✓ User created successfully! Default password: password123
```

## That's It!

You can now create users with all roles:
- ✓ Admin
- ✓ Developer
- ✓ Tester
- ✓ Architect
- ✓ Designer
- ✓ HR
- ✓ Product Manager
- ✓ DevOps
- ✓ Owner
- ✓ Contact Person

## Email Validation Bonus

The fix also adds email validation. Try entering an invalid email like `notanemail` and you'll see:
```
❌ Please enter a valid email address
```

## Automated Test (Optional)

Want to test all roles automatically?

```bash
python3 test_new_user_roles.py
```

This will:
- Login as Admin
- Try to create users with all new roles
- Test email validation
- Show you the results

## If Something Goes Wrong

### Option 1: Run Fix Script Again

```bash
./fix_user_roles_constraint.sh
```

### Option 2: Fresh Start

```bash
cd App_Development_scripts/New_development_scripts
./00_complete_fresh_start.sh
```

This will:
- Stop everything
- Delete all data
- Rebuild from scratch
- Apply all fixes automatically

**Warning**: This deletes all your data! Only use if you're okay starting fresh.

## Visual Guide

```
Before Fix:
┌─────────────────────────────────┐
│  Add New User                   │
├─────────────────────────────────┤
│  Full Name: HR Manager          │
│  Email: hr@example.com          │
│  Role: HR                       │
│                                 │
│  [Create User]  [Cancel]        │
└─────────────────────────────────┘
         ↓
    ❌ 500 Error!

After Fix:
┌─────────────────────────────────┐
│  Add New User                   │
├─────────────────────────────────┤
│  Full Name: HR Manager          │
│  Email: hr@example.com          │
│  Role: HR                       │
│                                 │
│  [Create User]  [Cancel]        │
└─────────────────────────────────┘
         ↓
    ✓ User created successfully!
```

## Need More Help?

Check these files:
- `QUICK_FIX_USER_ROLES.md` - Quick reference
- `USER_ROLES_FIX_COMPLETE.md` - Full documentation
- `USER_CREATION_FIX_SUMMARY.md` - Summary of changes

## Common Questions

**Q: Do I need to restart the application?**  
A: No, the fix script updates the database while it's running.

**Q: Will this delete my existing users?**  
A: No, it only updates the constraint. All existing users are safe.

**Q: Can I undo this?**  
A: Yes, but you shouldn't need to. The fix only adds support for more roles.

**Q: What if I already have users with these roles?**  
A: The fix will allow you to create more users with these roles. Existing users are not affected.

---

**Quick Command Reference**:
```bash
# Fix the database
./fix_user_roles_constraint.sh

# Test it
python3 test_new_user_roles.py

# Fresh start (if needed)
cd App_Development_scripts/New_development_scripts
./00_complete_fresh_start.sh
```
