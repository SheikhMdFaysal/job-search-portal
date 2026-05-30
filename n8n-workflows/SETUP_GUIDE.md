# Job Hunt AI Agent — Clean Setup Guide (Start Here Tomorrow)

**Goal:** Get all 3 n8n workflows running, end-to-end, with no saving errors and no connection drops.
**Audience:** Non-techy. Every command is copy-paste. Do the steps **in order** and don't skip.

Estimated time: ~90 minutes (most of it is creating accounts/keys, which is one-time).

---

## Why yesterday broke (so it doesn't happen again)

1. **"Autosave failed: Unauthorized"** → n8n was running without a saved encryption key and with secure-cookies on plain `http`. The browser session kept getting rejected. → **Fixed** by the Docker command in Step 2 (it sets `N8N_SECURE_COOKIE=false` and a persistent volume + encryption key).
2. **Workflows landed on one canvas** → they were imported into the same tab. → **Fixed** by importing each file into its own new workflow (Step 6).
3. **Connection drops** → that was the AI-assistant bridge, not your n8n. Tomorrow you'll do the wiring in the n8n UI directly, which is rock-solid.

---

## What you need (gather these first)

Open a notepad and collect these as you go. You'll paste them into n8n later.

| Item | Where to get it | Used by |
|------|-----------------|---------|
| **Anthropic API key** | console.anthropic.com → API Keys | WF1, WF2 |
| **Google account** | the Gmail you already use | WF1, WF2, WF3 |
| **Google Spreadsheet ID** | created in Step 4 | all 3 |
| **Adzuna App ID + Key** | developer.adzuna.com (free) | WF1 |
| **RapidAPI key (JSearch)** | rapidapi.com → JSearch → Subscribe (free tier) | WF1 |

> The Muse, Remotive, and Arbeitnow sources in WF1 need **no key** — they're free/open.

---

## STEP 1 — Install Docker Desktop (one-time)

1. Download **Docker Desktop**: https://www.docker.com/products/docker-desktop/
2. Install it, open it, wait until the whale icon says **"Docker Desktop is running."**
3. Leave it running in the background.

> Docker = the clean, self-contained box n8n runs in. No "it works then breaks" mess.

---

## STEP 2 — Start n8n the RIGHT way

Open your terminal (Mac: **Terminal app**; Windows: **PowerShell**) and paste this **single command**:

```bash
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_SECURE_COOKIE=false \
  -e N8N_ENCRYPTION_KEY=my-super-secret-key-change-this-123 \
  -e GENERIC_TIMEZONE=Asia/Dhaka \
  -e N8N_DEFAULT_BINARY_DATA_MODE=filesystem \
  docker.n8n.io/n8nio/n8n
```

**Windows PowerShell version** (same thing, one line — paste as-is):

```powershell
docker run -d --name n8n --restart unless-stopped -p 5678:5678 -v n8n_data:/home/node/.n8n -e N8N_SECURE_COOKIE=false -e N8N_ENCRYPTION_KEY=my-super-secret-key-change-this-123 -e GENERIC_TIMEZONE=Asia/Dhaka -e N8N_DEFAULT_BINARY_DATA_MODE=filesystem docker.n8n.io/n8nio/n8n
```

What each part does:
- `-v n8n_data:...` → **persists everything** (workflows, credentials) so nothing is lost on restart. This is the key fix.
- `N8N_SECURE_COOKIE=false` → **kills the "Unauthorized / autosave failed" error**.
- `N8N_ENCRYPTION_KEY=...` → stable key so saved credentials keep working. (You can leave the example value; just don't change it later.)
- `--restart unless-stopped` → n8n comes back automatically if your PC restarts.

Wait ~30 seconds, then open: **http://localhost:5678**

Create your owner account (email + password). **This time it will save.**

> ✅ Checkpoint: edit any workflow and it should save with NO red error banner.

### Useful Docker commands (keep these handy)
```bash
docker stop n8n      # pause n8n
docker start n8n     # resume n8n
docker logs n8n      # see what it's doing if something's off
```

---

## STEP 3 — (Optional) ngrok — you probably DON'T need it

Good news: **all 3 workflows use polling triggers, not webhooks**, and Google OAuth accepts `http://localhost:5678`. So **skip ngrok for now.**

Only set up ngrok if, in Step 5, Google refuses your `localhost` redirect URL. If that happens, come back here:
1. Sign up free at https://ngrok.com, install it, run `ngrok config add-authtoken YOUR_TOKEN`
2. Run: `ngrok http 5678`
3. Copy the `https://....ngrok-free.app` URL it gives you.
4. Stop n8n (`docker stop n8n && docker rm n8n`) and re-run the Step 2 command with one extra line added:
   `-e WEBHOOK_URL=https://YOUR-NGROK-URL.ngrok-free.app \`
5. Use the ngrok URL (not localhost) when adding the Google redirect URI.

---

## STEP 4 — Create the Google Sheet (the shared database)

1. Go to https://sheets.google.com → **Blank spreadsheet**.
2. Name it **Job Hunt Tracker**.
3. In **row 1**, paste these column headers (one per cell, columns A→K):

```
url	title	company	location	source	matchScore	reasoning	status	dateFound	resumeDocUrl	reminderSentAt
```
   (Tip: paste that whole line into cell A1 — tabs will spread it across columns.)

4. From the browser URL, copy your **Spreadsheet ID** — the long code between `/d/` and `/edit`:
   `docs.google.com/spreadsheets/d/`**`THIS_LONG_PART`**`/edit`
   Save it in your notepad. You'll paste it into 5 nodes.

---

## STEP 5 — Set up Google credentials (Sheets, Docs, Gmail)

This is the fiddliest part — do it once, calmly.

### 5a. Create a Google Cloud project + enable APIs
1. Go to https://console.cloud.google.com → top bar → **Create Project** → name it `n8n-jobhunt` → Create.
2. Left menu → **APIs & Services → Library**. Search for and **Enable** each of these (3 total):
   - **Google Sheets API**
   - **Google Docs API**
   - **Gmail API**

### 5b. Configure the consent screen
1. **APIs & Services → OAuth consent screen** → choose **External** → Create.
2. Fill App name (`n8n jobhunt`), your email for both support fields → Save and continue.
3. **Scopes** → Save and continue (leave default).
4. **Test users** → **+ Add users** → add your own Gmail address → Save.
   *(Important: without this, Google blocks the login.)*

### 5c. Create the OAuth credential
1. **APIs & Services → Credentials → + Create Credentials → OAuth client ID**.
2. Application type: **Web application**.
3. Under **Authorized redirect URIs → + Add URI**, paste exactly:
   ```
   http://localhost:5678/rest/oauth2-credential/callback
   ```
   *(If you ended up using ngrok, use your ngrok URL instead of `localhost:5678`.)*
4. **Create** → a popup shows your **Client ID** and **Client Secret** → copy both to notepad.

### 5d. Add the credentials inside n8n
In n8n: **Settings (top-right ⋯ or left menu) → Credentials → + Add credential**. Create **three**, all using the SAME Client ID + Secret from above:

1. **Google Sheets OAuth2 API** → paste Client ID + Secret → click **Sign in with Google** → approve.
2. **Google Docs OAuth2 API** → same Client ID + Secret → Sign in.
3. **Gmail OAuth2** → same Client ID + Secret → Sign in.

Then one more:
4. **Anthropic** → paste your Anthropic API key.

> ✅ Checkpoint: all 4 credentials show a green "Connected/Account connected" status.

---

## STEP 6 — Import the 3 workflows (each in its OWN tab)

The 3 JSON files are in your repo at `n8n-workflows/`. Get them onto your computer (download from GitHub branch `claude/trusting-goodall-9Z27P`, folder `n8n-workflows/`).

For **each** file, do this separately:
1. n8n left menu → **Overview → Create Workflow** (blank canvas).
2. Top-right **⋯ menu → Import from File** → pick the JSON.
3. **Save** (Ctrl/Cmd + S).
4. Repeat for the next file. **Never import two into the same canvas.**

Files:
- `workflow1-...json` → Daily job search & scoring (if present; otherwise it's already on your ngrok instance)
- `workflow2-jd-resume-tailor.json` → Resume tailoring
- `workflow3-application-reminder.json` → Gmail reminder

---

## STEP 7 — Wire each node (clear the red ⚠️ triangles)

Red ⚠️ = "pick a credential / fill a field." Click each flagged node:

### Workflow 2 (Resume Tailoring)
| Node | Set this |
|------|----------|
| `New Job Added` | Credential = Google Sheets · Document = your Spreadsheet ID · Sheet = `Sheet1` |
| `Master Resume` | Double-click → replace placeholder with your real resume text |
| `Claude` (small node under the Agent) | Credential = Anthropic |
| `Create Google Doc` | Credential = Google Docs |
| `Insert Resume Text` | Credential = Google Docs |
| `Update Sheet — Resume Ready` | Credential = Google Sheets · same Spreadsheet ID |

### Workflow 3 (Reminder)
| Node | Set this |
|------|----------|
| `Sheet Updated` | Credential = Google Sheets · Spreadsheet ID · Sheet = `Sheet1` |
| `Send Application Reminder` | Credential = Gmail (To is already your email) |
| `Update Sheet — Awaiting Submission` | Credential = Google Sheets · Spreadsheet ID |

### Workflow 1 (if importing fresh)
| Node | Set this |
|------|----------|
| `Search & Profile Settings` | Edit your job keywords + a short profile summary |
| Adzuna HTTP node | Add your Adzuna App ID + Key |
| JSearch HTTP node | Add RapidAPI key in the header |
| `Score Job Match` → Claude | Credential = Anthropic |
| `Save Scored Jobs` | Credential = Google Sheets · Spreadsheet ID |

---

## STEP 8 — Test before going live

1. Open **Workflow 2** → click **Execute Workflow** (manual run) with a test row already in the sheet. Watch each node turn green.
2. Fix any red node (usually a missing Spreadsheet ID or sheet name).
3. Do the same for Workflow 3 and 1.

---

## STEP 9 — Activate

For each workflow, flip the **Active** toggle (top-right) to ON.
- WF1 runs daily at 9 AM.
- WF2 checks for new job rows every hour.
- WF3 checks for status changes every minute.

> ✅ Done. The loop: WF1 finds & scores jobs → you (or WF2) trigger tailoring → WF2 builds a Google Doc resume + marks "Resume Ready" → WF3 emails you the apply link → you click Apply → mark it done.

---

## If something breaks (quick triage)

| Symptom | Fix |
|---------|-----|
| "Autosave failed: Unauthorized" | You didn't use the Step 2 command. Stop n8n, `docker rm n8n`, re-run Step 2 exactly. |
| Google "Access blocked / app not verified" | You forgot Step 5b → add yourself as a **Test user**. |
| Google "redirect_uri_mismatch" | The redirect URI in Step 5c doesn't match exactly. Re-copy it character-for-character. |
| Node red ⚠️ won't clear | Open it, pick the credential from the dropdown, fill the Spreadsheet ID. |
| n8n won't open at localhost:5678 | `docker logs n8n` to see the error; make sure Docker Desktop is running. |

---

## The order, in one line

**Docker running → run Step 2 command → open localhost:5678 → make Google Sheet → set up Google + Anthropic creds → import 3 workflows (separate tabs) → wire nodes → test → activate.**

You've got this. Work top to bottom, don't skip the checkpoints. 🚀
