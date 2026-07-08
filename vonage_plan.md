# Vonage Voice Integration Plan

> **Goal:** Switch from Twilio to Vonage for the voice check-in system.

**Architecture:**
- **Vonage Voice API:** Handles outbound calls and media streams.
- **Flask Integration:** Replaces Twilio's TwiML with Vonage's NCCO (Nexmo Call Control Objects).

---

### Phase 1: Setup
- **Task 1.1:** Sign up at [Vonage Developer](https://developer.vonage.com/) and create a voice application.
- **Task 1.2:** Get your `VONAGE_API_KEY`, `VONAGE_API_SECRET`, and `VONAGE_APPLICATION_ID` / `PRIVATE_KEY`.
- **Task 1.3:** Install the Vonage Python SDK:
  `pip install vonage`

### Phase 2: Implementation
- **Task 2.1:** Modify `/home/kali/hican-bridge/.env` to include Vonage credentials.
- **Task 2.2:** Update `app.py` to use Vonage's `Client` to initiate calls.
- **Task 2.3:** Replace TwiML logic with Vonage NCCO JSON to play audio or stream AI input.

---

**Next Steps:** I will now provide the exact steps to register for Vonage and prepare your environment.
