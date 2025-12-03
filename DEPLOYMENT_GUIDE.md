# 🚀 Deployment Guide: AI Avatar Empire

This guide will help you deploy your new **AI Avatar Automation System** to Render.

## 1. Prerequisites
-   **Render Account** (Free Tier is fine)
-   **D-ID Account** (Free Trial) -> Get API Key
-   **Cloudinary Account** (Free Tier) -> Get API Key
-   **YouTube Channel** -> Get OAuth Credentials (you already have this)

## 2. Environment Variables
You need to add these new variables to your Render Service:

| Variable Name | Value Description |
| :--- | :--- |
| `DID_KEY` | Your D-ID API Key (Basic Auth) |
| `DID_KEY_1` | (Optional) Backup D-ID Key |
| `DID_KEY_2` | (Optional) Another Backup Key |
| `AVATAR_IMAGE_URL` | URL to the photo of YOU (or your avatar) |
| `PEXELS_API_KEY` | Your Pexels API Key (for fallback B-roll) |
| `PIXABAY_API_KEY` | Your Pixabay API Key (for fallback B-roll) |

## 3. How to Deploy
1.  **Commit & Push:**
    ```bash
    git add .
    git commit -m "feat: Add AI Avatar System"
    git push origin main
    ```
2.  **Render Dashboard:**
    -   Go to your Render Dashboard.
    -   Select your service (`anslyzer` or similar).
    -   Go to **Environment**.
    -   Add the new variables listed above.
    -   Click **Save Changes**.
3.  **Manual Trigger:**
    -   Once deployed, go to `https://your-app-url.onrender.com/trigger` to test it immediately.

## 4. Verification
-   Check the **Logs** in Render.
-   Look for `✅ Avatar Generator initialized`.
-   Look for `🤖 Attempting AI Avatar generation...`.
-   If it says `✅ Avatar video generated`, check your Cloudinary/YouTube!

## 5. Troubleshooting
-   **"Avatar system not found"**: Ensure `avatar_automation_system.py` is committed.
-   **"D-ID generation failed"**: Check your `DID_KEY`. It should be `username:password` encoded or the raw key provided by D-ID.
-   **"Memory Error"**: The system will automatically fallback to the optimized Faceless mode if Avatar fails.
