# Complete Deployment & Hosting Guide
## Electric Vehicle Market Analysis and Intelligence System

This guide provides end-to-end instructions for deploying your project across multiple hosting environments:
1. **Free Cloud Deployment on Render** *(Recommended — creates a live public URL for course evaluation)*
2. **Beginner-Friendly Deployment on PythonAnywhere**
3. **Containerized Deployment with Docker & Docker Compose**
4. **Local Windows Production Deployment with Waitress (One-Click Launcher)**
5. **Publishing & Embedding Tableau Public Visualizations**

---

### Deployment Architecture Matrix

| Platform | Best For | Database Engine | Cost | Live URL Format |
| :--- | :--- | :--- | :--- | :--- |
| **Render.com** | Course Evaluation & Public Demo | SQLite (Zero-Config) or Remote MySQL | **Free** | `https://your-app.onrender.com` |
| **PythonAnywhere** | Academic Python Projects | SQLite / MySQL | **Free** | `https://yourusername.pythonanywhere.com` |
| **Docker** | Portability / Local Enterprise | SQLite or MySQL 8.0 Container | **Free** | `http://localhost:5000` |
| **Waitress (Windows)** | Offline Viva / In-Person Demo | SQLite / MySQL 8.0 Local | **Free** | `http://127.0.0.1:5000` |

---

## Option 1: Deploying to Render.com (Recommended Free Cloud Hosting)

Render offers a free tier for Python web applications, automatic HTTPS, and direct GitHub integration.

### Step 1: Push Your Project to GitHub
1. Open PowerShell in the project directory:
   ```powershell
   cd "C:\Users\HP\Desktop\Skill wallet"
   ```
2. Initialize Git (if not already done) and commit the project:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit: EV Market Analysis and Intelligence System"
   ```
3. Create a new repository on your [GitHub](https://github.com) account (e.g., `ev-market-intelligence`).
4. Link and push to GitHub:
   ```powershell
   git branch -M main
   git remote add origin https://github.com/<your-username>/ev-market-intelligence.git
   git push -u origin main
   ```

### Step 2: Create a Web Service on Render
1. Visit [https://render.com](https://render.com) and sign up / log in with your GitHub account.
2. Click **New +** &rarr; Select **Web Service**.
3. Choose your repository: `ev-market-intelligence`.
4. Configure the Web Service settings:
   - **Name:** `ev-market-intelligence` (or your preferred name)
   - **Region:** Nearest region (e.g., Singapore, Frankfurt, Oregon)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python database/seed_or_import.py
     ```
   - **Start Command:**
     ```bash
     gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4
     ```
   - **Instance Type:** `Free`

### Step 3: Configure Environment Variables
Under the **Environment Variables** section on Render, add:
- `FLASK_ENV` = `production`
- `FLASK_DEBUG` = `False`
- `SECRET_KEY` = *(click Generate or enter a random secure string)*
- `USE_MYSQL` = `False` *(runs SQLite out of the box)*
- `TABLEAU_DASHBOARD_URL` = *(Optional: paste your Tableau Public URL if published)*
- `TABLEAU_STORY_URL` = *(Optional: paste your Tableau Public Story URL)*

### Step 4: Deploy and Verify
1. Click **Create Web Service**.
2. Render will build the environment, install packages, seed the database, and start Gunicorn.
3. Once the build log displays `Your service is live 🎉`, your application is accessible at:
   **`https://ev-market-intelligence.onrender.com`**
4. Test the dashboard, manufacturer comparisons, and API endpoints directly from your phone, laptop, or presentation room!

---

## Option 2: Deploying to PythonAnywhere

PythonAnywhere is specifically built for Python Flask/Django hosting.

1. Create a free account at [https://www.pythonanywhere.com](https://www.pythonanywhere.com).
2. Open a **Bash Console** in your dashboard.
3. Clone your GitHub repository:
   ```bash
   git clone https://github.com/<your-username>/ev-market-intelligence.git
   cd ev-market-intelligence
   ```
4. Create and activate a virtual environment:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python database/seed_or_import.py
   ```
5. Navigate to the **Web** tab in PythonAnywhere:
   - Click **Add a new web app** &rarr; Select **Manual configuration** &rarr; **Python 3.10**.
   - Under **Virtualenv**, set path: `/home/<username>/ev-market-intelligence/venv`.
   - Under **Code**, set source directory: `/home/<username>/ev-market-intelligence`.
   - Edit the **WSGI configuration file** (`/var/www/<username>_pythonanywhere_com_wsgi.py`):
     ```python
     import sys
     import os

     project_home = '/home/<username>/ev-market-intelligence'
     if project_home not in sys.path:
         sys.path.insert(0, project_home)

     from app import app as application
     ```
6. Click the green **Reload** button. Your app is live at `https://<username>.pythonanywhere.com`.

---

## Option 3: Containerized Deployment with Docker

If your course requires containerization or you want to run the app anywhere with Docker:

### Standard Docker Build & Run (Single Container with SQLite)
```powershell
# 1. Build the Docker image
docker build -t ev-market-intelligence .

# 2. Run the container on port 5000
docker run -d -p 5000:5000 --name ev_app ev-market-intelligence

# 3. View live logs
docker logs -f ev_app
```
Access the application at **`http://localhost:5000`**.

### Full Multi-Container Stack with MySQL 8.0 (Docker Compose)
To deploy with a dedicated MySQL 8.0 enterprise container:
```powershell
# Start both Flask and MySQL 8.0
docker compose up -d

# Check running status
docker compose ps
```
Docker Compose automatically initializes MySQL 8 with `database/schema.sql` and `sql/views.sql`, creates persistent storage volumes, and links Flask over an isolated network.

To stop the containers:
```powershell
docker compose down
```

---

## Option 4: Local Windows Production Deployment (One-Click Launcher)

For an in-person college viva, lab exam, or presentation where internet connectivity may be limited:

### Using the One-Click Batch Launcher (`run_app.bat`)
We created a pre-configured launcher:
1. Double-click [**`run_app.bat`**](file:///c:/Users/HP/Desktop/Skill%20wallet/run_app.bat).
2. The script automatically:
   - Detects your Python environment.
   - Activates virtual environment if present.
   - Verifies the database is populated.
   - Starts the server and opens `http://127.0.0.1:5000` in your default browser automatically.

### Running with Waitress (Production WSGI for Windows)
Unlike Flask's built-in development server, Waitress is a multi-threaded production WSGI server:
```powershell
# Install waitress
pip install waitress

# Run production entrypoint
python wsgi.py
```
Open **`http://127.0.0.1:5000`**.

---

## Option 5: Publishing & Embedding Tableau Visualizations

To embed live interactive Tableau Public dashboards into your deployed web application:

1. **Open the Pre-Built Workbook:**
   Launch Tableau Desktop or free Tableau Public. Open:
   [`tableau/ev_market_intelligence.twb`](file:///c:/Users/HP/Desktop/Skill%20wallet/tableau/ev_market_intelligence.twb)
   *(Data source: `data/processed/tableau_ev_market_data.csv`)*

2. **Publish to Tableau Public:**
   - In Tableau, navigate to **Server &rarr; Tableau Public &rarr; Save to Tableau Public As...**.
   - Sign in to your free Tableau Public account.
   - Name the workbook: `Electric Vehicle Market Analysis`.
   - Click **Save**.

3. **Obtain the Shareable Embed URL:**
   - Once published, view the dashboard on your Tableau Public profile.
   - Click the **Share** button below the visualization.
   - Copy the **Link** URL (e.g., `https://public.tableau.com/views/ElectricVehicleMarketAnalysis/Dashboard`).

4. **Connect URL to the Web App:**
   - For **local**: add to your `.env` file:
     ```env
     TABLEAU_DASHBOARD_URL=https://public.tableau.com/views/ElectricVehicleMarketAnalysis/Dashboard
     TABLEAU_STORY_URL=https://public.tableau.com/views/ElectricVehicleMarketAnalysis/Story
     ```
   - For **Render / Cloud**: add `TABLEAU_DASHBOARD_URL` under Environment Variables in the Render dashboard.
   - Refresh the web page: the `/dashboard` and `/story` pages will now display the official interactive Tableau embedded frame!

---

## Post-Deployment Verification Checklist

Once deployed, verify the following:
- [ ] Home page (`/`) loads with 23.9M+ cumulative sales in the KPI cards.
- [ ] Dashboard (`/dashboard`) filters (Year, Brand, Category) update the Plotly charts without refreshing the page.
- [ ] Manufacturers page (`/manufacturers`) displays the 2024 OEM rankings table.
- [ ] Battery Analysis (`/battery-analysis`) renders the interactive scatter plot.
- [ ] All 9 REST API endpoints (e.g. `/api/kpis?year=2024`) return HTTP 200 with JSON payloads.
- [ ] Database indicator shows live connectivity in the top ribbon.
