# UI Ownership Functionality Guide

## Step-by-Step Instructions to See Ownership Functionality

### 🎯 **IMPORTANT**: The ownership functionality is in the **Entity Details** page, not the list view!

## For Client Ownership (Multiple Owners):

### Step 1: Navigate to Hierarchy
1. Open your browser and go to: **http://localhost:3007**
2. Login with: `admin@datalegos.com` / `password`
3. Click on **"Hierarchy"** in the sidebar

### Step 2: Go to Clients
1. In the hierarchy page, click on **"Clients"** tab or section
2. You should see a list of clients including "Acme Corp"

### Step 3: Open Client Details (THIS IS KEY!)
1. **Click on "Acme Corp"** (or any client name) to open the details page
2. **DO NOT** look at the list view - you need to click on the client name to see the details

### Step 4: Find the Ownership Section
1. Scroll down in the client details page
2. Look for a section titled **"Owners:"** 
3. This should appear after the metadata (dates, description, etc.) and before the Actions buttons
4. You should see:
   - Current owners displayed as blue tags (e.g., "Admin User")
   - Each owner tag has an "×" button to remove them
   - A **"+ Add Owner"** button to add new owners

### Step 5: Test Adding Owners
1. Click the **"+ Add Owner"** button
2. A dropdown should appear with:
   - Search box to find users
   - List of available users who can be owners
   - Users with compatible roles (Admin, Owner, Project Manager)
3. Click on a user to assign them as an owner
4. The new owner should appear as a blue tag

## For Task/Subtask Assignments (Multiple Assignees with Roles):

### Step 1: Navigate to Tasks
1. In the hierarchy page, click on **"Tasks"** tab or section
2. You should see a list of tasks

### Step 2: Open Task Details
1. **Click on a task name** (e.g., "testing for creating tasks") to open the details page
2. Again, you need to click on the task name, not just view the list

### Step 3: Find the Assignment Section
1. Scroll down in the task details page
2. Look for a section titled **"Assigned:"**
3. This should appear in the same location as the ownership section for clients
4. You should see:
   - Current assignments displayed as colored tags (e.g., "Bob Johnson (Developer)")
   - Each assignment tag has an "×" button to remove them
   - A **"+ Assign"** button to add new assignments

### Step 4: Test Adding Assignments
1. Click the **"+ Assign"** button
2. A dropdown should appear with:
   - Search box to find team members
   - Role selection dropdown (Developer, Tester, Designer, Reviewer, Lead)
   - List of available users who can be assigned
3. Select a role and click on a user to assign them
4. The new assignment should appear as a colored tag with the role

## 🔍 **Troubleshooting - If You Don't See the Ownership/Assignment Sections:**

### Check 1: Are you in the Details View?
- Make sure you clicked on the entity name to open the details page
- The URL should look like: `http://localhost:3007/hierarchy?type=client&id=CLI-002`
- You should see a detailed view with metadata, description, etc.

### Check 2: Scroll Down
- The ownership/assignment sections appear after the metadata grid
- Scroll down past the dates, description, and timestamps sections

### Check 3: Check Browser Console
1. Press F12 to open developer tools
2. Go to Console tab
3. Look for any JavaScript errors
4. If you see errors, the components might not be loading

### Check 4: Verify Components are Loaded
1. In the browser console, type: `console.log('OwnershipDisplay loaded')`
2. Check if the OwnershipDisplay and EnhancedAssignmentDisplay components are imported

## 📍 **Exact Locations in UI:**

### For Clients/Programs/Projects:
- **Section Title**: "Owners:"
- **Location**: After metadata grid, before Actions buttons
- **Component**: OwnershipDisplay
- **Features**: Blue tags, + Add Owner button, remove (×) buttons

### For Use Cases/User Stories/Tasks/Subtasks:
- **Section Title**: "Assigned:"
- **Location**: After metadata grid, before Actions buttons  
- **Component**: EnhancedAssignmentDisplay
- **Features**: Colored role tags, + Assign button, role selection dropdown

## 🎯 **Quick Test:**
1. Go to: http://localhost:3007/hierarchy
2. Click "Clients" → Click "Acme Corp" → Scroll down → Look for "Owners:" section
3. Click "Tasks" → Click any task → Scroll down → Look for "Assigned:" section

If you still don't see these sections, there might be a component loading issue that we need to debug further.