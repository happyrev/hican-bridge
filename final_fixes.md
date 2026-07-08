# Final Hican Bridge Upgrade Plan

**Goal:** Correct the dashboard workflow, integrate the PDF, and activate the AI Chat.

### Task 1: Fix Dashboard & Profile Flow
- **Task 1.1:** Update `app.py` to ensure `/profile` redirects to `/dashboard` after saving.
- **Task 1.2:** Update `dashboard.html` to include the Menu (Profile, Reading, Chat, Diary) so users don't get stuck.

### Task 2: PDF Integration
- **Task 2.1:** Ensure `static/daring_greatly.pdf` is in the folder.
- **Task 2.2:** Update `index.html` and `dashboard.html` links to point to `/static/daring_greatly.pdf`.

### Task 3: AI Chat Activation
- **Task 3.1:** Ensure `openai` is fully configured and the `/chat` route sends the correct request to GPT-4o.
- **Task 3.2:** Update frontend JS to handle the response properly.

---

**I will now apply these updates.**
