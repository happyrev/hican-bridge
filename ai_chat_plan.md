# Hican Bridge AI Chat Implementation Plan

**Goal:** Integrate a chat interface where students can talk to the Hican Bridge AI assistant using their OpenAI API key.

### Task 1: Chat Frontend
- Add a new "Chat" tab to the navigation menu.
- Create a chat UI (input box + display messages).

### Task 2: Backend AI Integration
- Create `/chat` route in `app.py`.
- Use the OpenAI API (stored in your `.env`) to process student messages.
- Maintain a small context history (session-based) so the AI remembers the conversation.

### Task 3: Security
- Ensure the API key is used only on the server side (not exposed to the frontend).
