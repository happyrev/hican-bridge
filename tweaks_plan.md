# Hican Bridge Tweak Implementation Plan

**Goal:** Refine the user experience by adding a navigation menu, persistent state, PDF reading content, and photo uploads.

### Task 1: Navigation & State Persistence
- **Task 1.1:** Add a navigation bar to `index.html` to switch between Profile, Reports, Diary, and Reading Plan.
- **Task 1.2:** Use Flask `session` to remember if a student has completed their profile, so the form doesn't show again.

### Task 2: Profile Photo Uploads
- **Task 2.1:** Update `/profile` route to handle `request.files['profile_photo']`.
- **Task 2.2:** Update `index.html` profile form to include `<input type="file" name="photo">`.

### Task 3: PDF Reading Content & Menu
- **Task 3.1:** Create a `data/daring_greatly.json` mapping days to chapters/PDF page ranges.
- **Task 3.2:** Update the Reading Plan to show the specific content for the current day.
- **Task 3.3:** Serve the actual PDF file from a `static/` directory.

---
**Shall I proceed with Task 1 (Navigation Menu) first?**
