# Deployment Guide for Railway 🚂

This guide will help you deploy **ActionWatch** to [Railway](https://railway.app/).

## Prerequisites

1.  A [Railway](https://railway.app/) account.
2.  This repository pushed to GitHub.
3.  A GitHub App created (see `README.md` for setup).

## Architecture

We will deploy two services on Railway:
1.  **Backend**: Python (FastAPI) + PostgreSQL Database.
2.  **Frontend**: Node.js (React/Vite) serving static files.

## 🤖 Automated Deployment (Recommended)

This repository includes a GitHub Action to deploy automatically.

1.  **Get a Railway Token**:
    *   Go to [Railway Dashboard](https://railway.app/project/tokens).
    *   Generate a new token.
2.  **Add to GitHub Secrets**:
    *   Go to your GitHub Repo > Settings > Secrets and variables > Actions.
    *   Add a New Repository Secret named `RAILWAY_TOKEN` with the value you copied.
3.  **Push to Main**:
    *   Any push to the `main` branch will now trigger a deployment.

---

## Step 1: Create Project & Database

1.  Go to your Railway Dashboard and click **New Project**.
2.  Select **Provision PostgreSQL**.
3.  This will create a project with a Postgres database.

## Step 2: Deploy Backend

1.  Click **New** > **GitHub Repo** > Select your `gha-cron-monitor` repo.
2.  Click on the new service card to open settings.
3.  **Settings** tab:
    *   **Root Directory**: `/` (default)
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
    *   **Watch Paths**: `app/**` (optional, for auto-redeploy)
4.  **Variables** tab: Add the following:
    *   `DATABASE_URL`: *Reference the Postgres service variable* (Type `${` to autocomplete).
    *   `GITHUB_APP_ID`: *From your GitHub App (General settings)*
    *   `GITHUB_APP_PRIVATE_KEY`: *Paste the contents of your .pem file here*
    *   `GITHUB_CLIENT_ID`: *From your GitHub App*
    *   `GITHUB_CLIENT_SECRET`: *From your GitHub App*
    *   `GITHUB_WEBHOOK_SECRET`: *From your GitHub App*
    *   `GITHUB_REDIRECT_URI`: `https://<YOUR_BACKEND_URL>/api/auth/callback` (You'll get the URL after deployment).
    *   `FRONTEND_URL`: `https://<YOUR_FRONTEND_URL>` (You'll add this later).
    *   `SECRET_KEY`: *Generate a random string (e.g., `openssl rand -hex 32`)*.
    *   `SLACK_WEBHOOK_URL`: *(Optional) For Slack alerts*
5.  **Networking** tab:
    *   Click **Generate Domain** to get your backend URL (e.g., `web-production-123.up.railway.app`).
    *   **Update your GitHub App**: Go to your GitHub App settings and update the **Callback URL** to match this domain + `/api/auth/callback`.

## Step 3: Deploy Frontend

1.  Click **New** > **GitHub Repo** > Select the `gha-cron-monitor` repo *again*.
2.  Click on the new service card.
3.  **Settings** tab:
    *   **Root Directory**: `/frontend`
    *   **Build Command**: `npm run build`
    *   **Start Command**: `npm run start`
4.  **Variables** tab:
    *   `VITE_API_URL`: `https://<YOUR_BACKEND_URL>` (The URL from Step 2).
5.  **Networking** tab:
    *   Click **Generate Domain** to get your frontend URL.
    *   **Update Backend Variable**: Go back to your Backend service variables and update `FRONTEND_URL` with this new domain.

## Step 4: Finalize Configuration

1.  **Redeploy**: Trigger a redeploy of the Backend service so it picks up the `FRONTEND_URL`.
2.  **Verify**: Open your Frontend URL. You should see the ActionWatch login screen.

## Troubleshooting

*   **CORS Errors**: Ensure `FRONTEND_URL` in Backend variables matches your Frontend domain exactly (no trailing slash).
*   **Database Connection**: Ensure `DATABASE_URL` is correctly linked in Railway.
*   **Build Fails**: Check the "Build Logs" in Railway. Ensure `package.json` dependencies are correct.

---

## Optional: Stripe (Billing)

If you are using the billing features, add these variables to the **Backend** service:
*   `STRIPE_SECRET_KEY`: *From Stripe Dashboard*
*   `STRIPE_WEBHOOK_SECRET`: *From Stripe Dashboard*
*   `STRIPE_PRICE_ID`: *Price ID for the subscription*
