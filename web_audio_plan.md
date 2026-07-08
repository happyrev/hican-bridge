# Web-Based Calling Implementation Plan

> **Goal:** Build an in-browser voice interface (using WebRTC) for students, eliminating the need for expensive telephony (Twilio/Vonage) and simplifying the setup.

**Architecture:**
- **Frontend:** HTML5 `<audio>` API + Web Speech API (Browser-native voice capture).
- **Backend:** Flask (receives the recorded audio blob, sends to OpenAI for transcription).
- **Processing:** OpenAI Whisper (API) handles the transcription of the blob.

**Tech Stack:** JavaScript (MediaRecorder), Flask, OpenAI API.

---

### Phase 1: Browser-Side Audio Capture
- **Task 1.1:** Add a "Record Report" button to `templates/index.html` using JavaScript `MediaRecorder`.
- **Task 1.2:** Handle the stream permissions (microphone) and capture the audio as a `Blob`.

### Phase 2: Backend Audio Processing
- **Task 2.1:** Create a Flask route `/upload-audio` to receive the binary audio file.
- **Task 2.2:** Save the file temporarily, send it to OpenAI's Whisper API, and retrieve the text.

### Phase 3: Reporting Integration
- **Task 3.1:** Automatically save the transcription text into the "Weekly Report" field in your `reports` list.

---

**Next Steps:** I will implement the UI for the audio recorder now. Shall I proceed?
