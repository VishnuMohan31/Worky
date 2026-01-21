## Worky – End‑to‑End Application Workflow

This document explains **how to use the Worky application from end to end**.  
It is written so that **anyone on the team (non‑technical or technical)** can read and understand the core flows.

---

## 1. Accessing the Application

- **Open the UI**
  - Local development: `http://localhost:3007`
  - Production: use the team’s configured URL (for example `http://62.171.191.132:3007`).

- **Log in**
  - Enter your **email / username** and **password**.
  - On success you are redirected to the **main workspace** (usually dashboard / main navigation area).

- **User roles**
  - Typical roles: **Admin, Developer, Tester, Architect, Designer, Owner, Contact Person, Project Manager, DevOps**, etc.
  - What you can see/do depends on your role (for example, only Admin / Owner can manage some master data).

---

## 2. High‑Level Concept Map

At a high level the tool is organized around these concepts:

- **Clients** – Companies or customers for whom you are doing work.
- **Projects** – Work you do for a given client.
- **Teams & Users** – People who work on projects and tasks.
- **User Stories / Use Cases / Tasks** – Breakdown of actual work items.
- **Assignments** – Who is responsible for which item (story or task).
- **Decisions** – Key decisions taken during the project (for traceability).

The usual flow is:

> Create / manage **Clients** → Create **Projects** → Configure **Teams & Users** →  
> Capture **User Stories / Use Cases** → Break them into **Tasks** →  
> **Assign** work → Track with **Decisions** and status updates.

---

## 3. Client & Project Setup

### 3.1 Manage Clients

1. Go to the **Clients** page from the main navigation.
2. For each client:
   - **Create / Edit**:
     - `Name`
     - `Short description`
     - `Long description` (detailed context, background, scope, etc.).
   - **Save** to update the record.
3. The **client detail view** shows:
   - Basic info (name, descriptions).
   - Key statistics used by other areas (projects, stories, tasks, etc.).

**Goal:** Everyone can quickly understand **who the client is** and **what problem we are solving**.

### 3.2 Create and Configure Projects

1. From **Projects** (or sometimes from the client detail page) create a new project.
2. Fill in:
   - Project name
   - Associated client
   - Basic description / objectives
3. Save the project – it becomes the container for **user stories, tasks, decisions, and team assignments**.

---

## 4. Teams, Users, and Roles

### 4.1 Users

1. Navigate to the **Users** page.
2. For each person:
   - Add user (or edit existing user).
   - Set:
     - Name, email
     - **Role** (Admin, Developer, Tester, Architect, Designer, Owner, Contact Person, PM, DevOps, etc.).
3. Save changes.

### 4.2 Teams

1. Navigate to the **Teams** page.
2. Create / edit a team:
   - Team name
   - Purpose / area (e.g., Backend, Frontend, QA, DevOps, etc.).
3. **Add members** to the team:
   - Pick users from the list.
   - Optionally set responsibilities or tags.
4. Some views let you see:
   - Which **projects / areas** the team covers.
   - How assignments map to teams.

**Goal:** It should always be clear **who is on which team** and **who can be assigned to what**.

---

## 5. User Stories / Use Cases

User stories (and sometimes “use cases”) describe **functional pieces of work** from an end‑user perspective.

### 5.1 Creating User Stories

1. Go to the **User Stories** or **Backlog** page.
2. Click **“Create User Story”**.
3. Fill in:
   - Title
   - Description (what problem it solves, acceptance criteria)
   - Links to **Client** and **Project** (if needed)
   - Optional: priority, phase, status.
4. Save.

### 5.2 Parent Use Case / Hierarchy

When creating or editing a story, you may see a **“Parent Usecase / Parent Story”** area:

1. Use this to connect the current story to a **bigger feature or parent item**.
2. This helps you build a **hierarchy**:
   - Epics / big features at the top
   - User stories / smaller use cases in the middle
   - Tasks at the bottom.

---

## 6. Tasks and Detailed Work Breakdown

Tasks are the **smallest actionable items** that developers / testers actually work on.

### 6.1 Creating Tasks

1. Open a **User Story** or go to the **Tasks** area.
2. Add a **Task**:
   - Title (what needs to be done)
   - Description (details, links, technical notes)
   - Optional fields: estimate, status, priority, tags.
3. Save.

Tasks often appear:
- On the **right‑hand side “Tasks” panel**.
- Inside the **hierarchical views** (e.g., tree of features → stories → tasks).

### 6.2 Viewing Task Details

1. Click on a task card or row.
2. You can typically see:
   - Title and description
   - Linked story / use case
   - Assigned user(s)
   - Status and other metadata (e.g., phase, due date).

---

## 7. Assignments – Who Does What

Assignment controls **who is responsible** for a certain story or task.

### 7.1 Assigning People from Lists and Cards

You will see **assignment controls** in multiple places:

- **User Story / Use Case detail** – Assign owners / contributors.
- **Task cards / entity cards** – Usually with a small **badge or number** (e.g., blue “2” button) indicating how many people are assigned.

When you click these assignment actions:

1. A **modal (popup)** opens instead of a cramped dropdown.
2. Inside the modal you can:
   - **Search** for a user by name / role.
   - See **user cards** with name, role, avatar/initials.
   - Select or deselect people.
   - Confirm assignments with clear action buttons (e.g., **Save**, **Cancel**, sometimes **Clear**).
3. Once saved:
   - The UI updates the counts / avatars.
   - The backend is updated so assignments are consistently used across views.

### 7.2 Assignment Counts (Badges)

- Small badge buttons (like the blue number at the **top‑right of a card**) show:
  - **How many people** are assigned.
  - Clicking them opens the **assignment modal** for quick editing.

**Goal:** It should be **easy and visually clear** who is working on each item without confusing dropdowns.

---

## 8. Decisions and Governance

Decisions capture **important project choices** so that the team has an audit trail.

### 8.1 Recording a Decision

1. Go to the **Decisions** page or tab for a client/project.
2. Click **“Add Decision”**.
3. Fill in:
   - Decision title (short summary)
   - Description / context
   - Outcome (e.g., accepted, rejected, pending)
   - Related project / area / story (if applicable).
4. Save.

### 8.2 Reviewing Decisions

1. Use filters (by project, status, date) to find decisions.
2. Read through decisions to understand **why** certain technical or product choices were made.

**Goal:** New team members can quickly understand **history and rationale** without digging through chat logs or emails.

---

## 9. Daily Usage Flow (Example)

Here is a realistic **day‑to‑day workflow** that a team might follow:

1. **Morning**
   - Team members log in.
   - Check **board / stories / tasks** assigned to them.
2. **Planning / Grooming**
   - Product Owner / PM reviews **Clients & Projects**.
   - Adds or updates **User Stories** and **Tasks**.
   - Uses assignment modals to assign work to the correct **Teams / Users**.
3. **Execution**
   - Developers / testers open their tasks.
   - Update **status**, add notes, and complete work.
4. **Decisions**
   - When a significant choice is made (architecture, tools, scope changes), it is recorded in **Decisions**.
5. **Review**
   - At end of day or sprint:
     - Review **completed tasks & stories**.
     - Ensure **assignments** and statuses are accurate.
     - Review **decisions** to ensure everything important is documented.

---

## 10. Backend / Infrastructure (High‑Level Overview)

This section is for people who need a **quick high‑level understanding** of how the system runs (without deep technical details).

- **Database**
  - PostgreSQL database (stores users, clients, projects, stories, tasks, decisions, assignments, etc.).
  - Runs in a Docker container, typically exposed on port `5437` locally.

- **API**
  - FastAPI backend (Python).
  - Provides REST endpoints `/api/v1/...` used by the UI.
  - Runs in a Docker container, usually on port `8007`.

- **UI**
  - React + TypeScript frontend.
  - In development: `npm run dev` on port `3007`.
  - In production: served through Nginx (or similar) pointing to the built static assets.

**You usually do not need to touch these** as a normal user.  
They are managed by the DevOps / engineering team.

---

## 11. Quick “How To” Reference

- **Log in** → Use your credentials on the login page.
- **See clients** → Go to **Clients** page.
- **See projects** → Use the **Projects** / **Clients → Projects** view.
- **Create a user story** → Go to **User Stories / Backlog**, click **Create**.
- **Create a task** → From a user story or the **Tasks** panel, click **Add Task**.
- **Assign work** → Click on assignment buttons / badges → edit in the **modal**, then save.
- **Record a decision** → Open **Decisions** page → **Add Decision**.
- **Review responsibilities** → Check **Teams**, **Users**, and assignment badges on stories/tasks.

If you follow the sections above in order, you get a complete **end‑to‑end flow**:

> Set up **Clients → Projects → Teams & Users → User Stories → Tasks → Assignments → Decisions → Daily execution & review**.

This is the core workflow of the Worky application.

