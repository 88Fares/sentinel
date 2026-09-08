# Setting this up with GitHub Desktop (no terminal needed)

You are here because this folder is on your PC and needs to become a GitHub repository.
Total time: about 10 minutes. You never touch a command line.

## 1. Install GitHub Desktop
Download from https://desktop.github.com and install it. Sign in with your GitHub account
(create one free at https://github.com/signup if you don't have one). Signing in here is what
authorises pushing later — you will not need to create or paste any token.

## 2. Add this folder as a repository
In GitHub Desktop: **File → Add local repository…** → Choose this folder
(`C:\Users\<you>\Downloads\sentinel`) → it will say *"This directory does not appear to be a Git
repository"* → click **create a repository** in that message.
On the next screen leave the name as `sentinel`, leave "Git ignore" as None (a `.gitignore` is
already included), and click **Create repository**.

## 3. Publish it to GitHub
Click the **Publish repository** button at the top.
- Name: `sentinel`
- **Untick "Keep this code private"** if you want the dashboard to be viewable without signing in.
  (Public is simplest. The files contain only simulated portfolio data — no personal or account
  information. If you prefer Private, the dashboard in step 4 will not work unless you have a paid
  GitHub plan; everything else still works.)
- Click **Publish repository**.

## 4. Let the automation commit its results
In your browser go to your new repository → **Settings** → **Actions** → **General** → scroll to
**Workflow permissions** → select **Read and write permissions** → **Save**.

## 5. Turn on the dashboard
Still in Settings → **Pages** → under "Build and deployment", Source: **Deploy from a branch** →
Branch: **main**, folder: **/docs** → **Save**.
After a minute your dashboard is live at `https://<your-username>.github.io/sentinel/`.

## 6. Run it once
Go to the **Actions** tab → click **sentinel** in the left sidebar → **Run workflow** → **Run
workflow**. Wait about two minutes and refresh. When it finishes green, check that `data/` now
contains `prices_daily.csv` and that your dashboard URL shows numbers.

If the Actions tab shows a message asking you to enable workflows, click the green button to enable
them and then run it.

## 7. Tell Claude
Send Claude the repository URL (`https://github.com/<your-username>/sentinel`) and the dashboard URL.
Claude records them in the project runbook so the scheduled daily, weekly and monthly runs read the
repository's data instead of scraping web pages.

If you made the repository **private**, Claude cannot read it without a token — say so and Claude
will explain the one extra step.

## Keeping it updated
When Claude gives you new ledger files, replace them in this folder, then open GitHub Desktop, type
a short summary, click **Commit to main**, then **Push origin**. Nothing else is needed — the
schedule keeps running on GitHub's servers whether your PC is on or off.

## Optional: richer macro data
Get a free API key from https://fred.stlouisfed.org/docs/api/api_key.html, then in your repository:
Settings → Secrets and variables → Actions → New repository secret → Name `FRED_API_KEY`, paste the
key. This adds Fed funds, CPI and Treasury series to the daily pull. The system works fine without it.
