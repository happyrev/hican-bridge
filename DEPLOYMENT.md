# Deployment Plan: Hican Bridge to Render

> **Goal:** Deploy the Hican Bridge Flask application to a permanent public URL using Render.com.

**Steps:**

### 1. Prepare for Deployment
- **Task 1.1: Create a `requirements.txt` file**
  - Render needs to know which packages to install.
  - Command: `/home/kali/hican-bridge/venv/bin/pip freeze > /home/kali/hican-bridge/requirements.txt`

- **Task 1.2: Add a `gunicorn` configuration**
  - Render needs a production server (Flask's `debug=True` is not for production).
  - Install gunicorn: `/home/kali/hican-bridge/venv/bin/pip install gunicorn`
  - Update `requirements.txt` again.

### 2. Prepare the Codebase
- **Task 2.1: Add a Procfile**
  - Create `Procfile` in the root directory:
    ```text
    web: gunicorn app:app
    ```

### 3. Push to GitHub
- **Task 3.1: Create Repository**
  - Initialize git: `git init` in `/home/kali/hican-bridge/`
  - Create a repo on GitHub.
  - Push the code:
    ```bash
    git add .
    git commit -m "Initial commit for deployment"
    git remote add origin https://github.com/YOUR_USERNAME/hican-bridge.git
    git push -u origin main
    ```

### 4. Deploy on Render
- **Task 4.1: Connect to Render**
  - Sign up for [Render.com](https://render.com/).
  - Click "New +" -> "Web Service".
  - Connect your GitHub repository.
  - Set "Build Command" to `pip install -r requirements.txt`.
  - Set "Start Command" to `gunicorn app:app`.
  - Click "Create Web Service".

---

**Ready to start?**
I can help you create the `requirements.txt` and `Procfile` immediately. Should I start those files?
