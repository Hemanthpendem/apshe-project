# How to Put This Project on GitHub (Beginner Guide)

No coding/terminal experience needed — this uses only the GitHub website.
Total time: about 10 minutes.

## Step 1: Create a GitHub account (skip if you already have one)

1. Go to **https://github.com/join**
2. Enter an email, password, and username → follow the on-screen steps
3. Verify your email if asked

## Step 2: Create a new repository

1. Once logged in, click the **+** icon (top-right) → **New repository**
2. Fill in:
   - **Repository name**: `ai-learning-assistant` (or any name you like)
   - **Description** (optional): "Emotion-aware AI learning assistant — college project"
   - Set visibility to **Public** (so your college can view it) or **Private**
     (only if your college specifically allows private repos + adding them
     as a collaborator)
   - Leave "Add a README file" **unchecked** — you already have one
3. Click **Create repository**

You'll land on an empty repo page with an upload option — keep it open.

## Step 3: Upload the project files

1. On your new repo page, click **"uploading an existing file"**
   (or go to **Add file → Upload files**)
2. Unzip `ai_learning_assistant.zip` on your computer first
3. Open the unzipped `ai_learning_assistant` folder, select **all files and
   folders inside it** (not the outer folder itself), and drag them into
   the GitHub upload box
   - GitHub will show a progress list of every file being added
   - This can take a minute for the `notebooks/` file
4. Scroll down to **"Commit changes"**
   - Add a short message like `Initial commit — AI Learning Assistant`
   - Click **Commit changes**

Your code is now live on GitHub.

> ⚠️ **Important:** Do NOT upload a `.env` file with your real Gemini API
> key. The project's `.gitignore` is set up to skip it automatically if you
> use `git` on the command line — but the drag-and-drop web uploader does
> **not** check `.gitignore`, so just make sure you never created a `.env`
> file inside the folder you're uploading (only `.env.example` should be
> there, which is safe — it has no real key in it).

## Step 4: Get the link to submit to your college

1. On your repo's main page, click the green **"< > Code"** button
2. Copy the **HTTPS URL**, e.g.:
   `https://github.com/your-username/ai-learning-assistant`
3. That URL (without `.git` at the end) is what you submit — it opens
   directly to your project's README and files.

## Optional: Make it look more complete

- **Add a description**: click the ⚙️ gear icon next to "About" on the repo
  homepage, add a one-line description and topics like `streamlit`,
  `nlp`, `emotion-detection`
- **Pin the README**: it already displays automatically on your repo's
  homepage — no action needed
- **Deploy a live demo** (impressive for submission, optional):
  1. Go to **https://share.streamlit.io**, sign in with GitHub
  2. Click **New app**, pick your repo, set main file to `app.py`
  3. Click **Deploy** — you'll get a live URL like
     `https://your-app-name.streamlit.app` to include in your README

## Alternative: Using Git on the command line (if your college wants commit history)

If you have Git installed and want proper commit history instead of a
single web upload:

```bash
cd ai_learning_assistant
git init
git add .
git commit -m "Initial commit — AI Learning Assistant"
git branch -M main
git remote add origin https://github.com/your-username/ai-learning-assistant.git
git push -u origin main
```

You'll be prompted to log in — GitHub now requires a **Personal Access
Token** instead of your password:
1. Go to **GitHub → Settings → Developer settings → Personal access tokens
   → Tokens (classic) → Generate new token**
2. Check the `repo` scope, generate it, and copy the token
3. When `git push` asks for a password, paste the token instead
