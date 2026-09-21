# Publishing the Guardrails Safety Layer

This project is two things at once: a tested Python package (`safeguard`) you can run
from the command line, and a small Streamlit web app that puts the same guards in
front of a demo bot. "Hosting" here means two separate jobs:

1. Get the **source** onto GitHub, with CI that proves the guards still work on every
   push — this is the part that matters most for an interview, because it's evidence,
   not a claim.
2. Get the **demo app** running somewhere public, so someone can type a message into
   a browser and watch the guards fire without installing anything.

Do them in that order. A repo with green CI is worth having even if you never deploy
the app; the reverse isn't true.

Everything below assumes you're working from the repo root (`ai/17-guardrails-safety-layer/`) — the
folder that contains `app.py`, `safeguard/`, `tests/`, and
this `hosting/` folder. That whole project folder is what becomes the GitHub repo.

---

## Step 1 — Get it on GitHub

If you've never used Git before, the "Step 0" section of
`ai/01-data-detective/hosting/HOSTING_GUIDE.md` walks through installing Git, making
a GitHub account, and telling Git who you are. Do that first if you skipped it on
project 1. From here on this guide assumes `git --version` already works.

### 1a. Check what must never be committed

Open `ai/17-guardrails-safety-layer/.gitignore` (the one next to this project's
README) and confirm it has at least:

```
.env
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/
.pytest_cache/
.ipynb_checkpoints/
```

The line that matters most is `.env`. If you ever ran the `--llm` flag or ticked "use
LLM classifier" in the app, you put a real API key in `.env`. A
`.gitignore` line of `.env` (no leading path) matches that file no matter which
folder it's in, so it is covered by this one root-level rule.
**`.env` never gets committed.** If it's on GitHub even once, treat the key as
burned — revoke and re-issue it with the provider, then remove the file from Git
(the troubleshooting section of the project-1 hosting guide covers exactly this).
The repo ships `.env.example` instead — variable names, no
values — and that one is meant to be committed.

### 1b. Init, commit, push

From `ai/17-guardrails-safety-layer/` (the repo root):

```powershell
git init
git add .
git commit -m "Guardrails safety layer: guards, tests, red-team report"
```

Then check the single most important thing before you push anything anywhere:

```powershell
git status
```

You want `nothing to commit, working tree clean`, and you must **not** see `.env`
listed. If it shows up, stop and fix it now (see the troubleshooting section in the
project-1 hosting guide) — it's much easier before the first push than after.

Create an empty repo on github.com (name it something like `guardrails-safety-layer`,
public, and **don't** tick "Add a README" or "Add .gitignore" — you already have
both and an auto-generated one will collide with your first push). Then:

```powershell
git branch -M main
git remote add origin https://github.com/YOURNAME/guardrails-safety-layer.git
git push -u origin main
```

Refresh the repo page on GitHub. You should see `safeguard/`, `tests/`,
`hosting/`, `app.py`, this project's `README.md`, and `.gitignore`.

---

## Step 2 — Add CI as a ship gate, not just a green checkmark

In project 1, CI meant "the tests still pass on a clean machine." Here it means
something sharper, because of what this project actually is: a promise that certain
attacks are handled. A promise nobody re-checks isn't a promise, it's a vibe. CI is
how you make the check automatic and impossible to skip.

The workflow at `hosting/github_actions/ci.yml` does two things on every push and
every pull request:

1. Runs the 33 pytest tests (`pytest`, from the repo root).
2. Runs the full red-team suite: `python -m safeguard --redteam`, also from the
   repo root.

That second line is the one worth understanding properly. `python -m safeguard
--redteam` runs the same 19 attacks documented in
`REDTEAM_REPORT.md` — 5 injection attempts, 4 PII leaks, 4
off-topic questions, 2 unsafe requests, and 4 normal banking questions that should
be *allowed* — straight through the guards, and prints the same pass/fail table you
see in that file. Critically, **the CLI itself exits with code 1 if even one attack
stops being handled as expected** (see `safeguard/cli.py` — `_run_redteam` returns
`0 if s["passed"] == s["total"] else 1`). A non-zero exit code is exactly what makes
a GitHub Actions step fail. So there's no extra scripting to write here: the ship
gate is already built into the tool, and CI just has to run it.

This is the difference it makes in practice: without this step, "we added a guard
against prompt injection" is true today and might quietly stop being true in three
months, after someone tweaks a regex in `injection.py` to fix an unrelated false
positive and accidentally weakens it. Nobody would notice — the app still runs, the
demo still looks fine — until an actual attacker finds the gap. With this step, that
same regex change makes the very next push go red, with a table showing exactly
which attack ID started slipping through. "We added a guard once" becomes "a
regression can never silently ship."

### Install it

Copy the workflow into the exact place GitHub looks for it — `.github/workflows/`
at the repo root:

```powershell
mkdir .github\workflows
copy hosting\github_actions\ci.yml .github\workflows\ci.yml
git add .github\workflows\ci.yml
git commit -m "Add CI: tests + red-team suite as a ship gate"
git push
```

Open the file once and read the comments — it's annotated step by step.

Go to the repo's **Actions** tab on GitHub and watch the run. You'll see two green
checks appear: "Run tests" and "Run the red-team suite (ship gate)". To *see* the
gate work, try breaking something on purpose in a scratch branch — comment out one
line in `safeguard/injection.py` that catches the "ignore your instructions"
pattern, push, and watch the red-team step go red with `inj_ignore ... FAIL` in the
log. Then revert it. That five-minute experiment is worth more than reading about
the concept — it's the whole point of this project made visible.

---

## Step 3 — Deploy the Streamlit demo to Hugging Face Spaces

This is the "someone can click a link and try it" part. Hugging Face Spaces hosts
Streamlit apps for free. Reference docs: the
[Spaces overview](https://huggingface.co/docs/hub/spaces) and the
[Streamlit Spaces guide](https://huggingface.co/docs/hub/spaces-sdks-streamlit).

### 3a. What a Space needs, exactly

A Space is its own small Git repo. At its root it needs:

- `app.py` — copy this straight from `app.py`.
- `requirements.txt` — use `hosting/space/requirements.txt` from this project, not
  the root `requirements.txt` (the Space one drops `pytest`, which the
  demo doesn't need, and keeps only what the app actually imports).
- The `safeguard/` package folder — copy `safeguard/` across
  wholesale (the code the app imports; skip the `__pycache__/` subfolders inside it).
- `README.md` with YAML front-matter at the very top telling Spaces how to run it.
  Use `hosting/space/README.md` from this project as-is — it already has:

  ```yaml
  ---
  title: Guardrails Safety Layer
  emoji: 🛡️
  colorFrom: blue
  colorTo: indigo
  sdk: streamlit
  app_file: app.py
  pinned: false
  ---
  ```

  `sdk: streamlit` and `app_file: app.py` are the two lines that actually matter —
  they're what tells Spaces to launch `streamlit run app.py` instead of trying to
  guess what kind of app this is.

### 3b. Create the Space and push these files into it

1. Go to https://huggingface.co (make a free account if you don't have one) →
   **New Space**.
2. Give it a name, pick **Streamlit** as the SDK, choose **Public**, and create it.
   Hugging Face gives you a Space that's itself a Git remote, something like
   `https://huggingface.co/spaces/YOURNAME/guardrails-safety-layer`.
3. Clone it locally, somewhere outside your project folder (a Space repo is separate
   from your GitHub repo — you're pushing the same files to a second remote):

   ```powershell
   git clone https://huggingface.co/spaces/YOURNAME/guardrails-safety-layer
   cd guardrails-safety-layer
   ```

4. Copy in the four things it needs, from your project folder:

   ```powershell
   copy ..\17-guardrails-safety-layer\app.py .
   copy ..\17-guardrails-safety-layer\hosting\space\requirements.txt .
   copy ..\17-guardrails-safety-layer\hosting\space\README.md .
   xcopy ..\17-guardrails-safety-layer\safeguard safeguard\ /E /I /EXCLUDE:nul
   ```

   (Adjust the `..\17-guardrails-safety-layer\` prefix to wherever your project
   folder actually sits relative to the cloned Space.) If the `safeguard/__pycache__`
   folder got copied along with it, delete it — it's just compiled bytecode, not
   needed and not wanted here.

5. Commit and push to the Space:

   ```powershell
   git add .
   git commit -m "Deploy guardrails demo"
   git push
   ```

Hugging Face builds and starts the app automatically. Give it a minute, then open
the Space's URL — you'll see the same "Try a message" and "Red-team report" tabs
you get running `streamlit run app.py` locally.

### 3c. The optional API key

The public demo works with **no key at all** — every guard defaults to offline
regex and rules, which is exactly why the red-team report and every test pass with
zero network access. The "use LLM classifier" checkbox in the sidebar is the one
feature that needs a key, for the fuzzier cases a plain regex can't catch.

If you want that checkbox to actually work on the public Space, add the key as a
**Space secret**, not a plain file (never put a real key in a committed
`requirements.txt`, `app.py`, or `README.md`):

1. On the Space page, go to **Settings → Variables and secrets → New secret**.
2. Name it `GEMINI_API_KEY`, paste in a key from
   https://ai.google.dev/gemini-api/docs/api-key (free tier), and save.
3. The Space restarts automatically. `safeguard/llm.py` reads the key from the
   environment the same way it would read a local `.env` — Spaces injects secrets
   as environment variables, so no code change is needed.

Leave the secret unset if you'd rather keep the demo purely offline — it's a
perfectly complete demo either way, and arguably a better one, since it proves the
guards don't need an LLM to catch the five injection attacks and four PII leaks in
the red-team suite.

---

## Step 4 — Alternative: Streamlit Community Cloud

If you'd rather point at the GitHub repo you already pushed in Step 1 instead of
maintaining a second Space repo, Streamlit Community Cloud does that directly.
Reference:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

1. Go to https://share.streamlit.io, sign in with GitHub, and authorize access to
   your `guardrails-safety-layer` repo.
2. Click **New app**, pick that repo and the `main` branch.
3. Set **Main file path** to `app.py` — this is the one field
   that matters; your `app.py` sits at the repo root.
4. Deploy. Community Cloud looks for a `requirements.txt` next to the app file it's
   running, so it picks up `requirements.txt` automatically —
   no extra config needed there.
5. For the optional key: open the deployed app's **Settings → Secrets** and paste in

   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```

   TOML format, one line per key. Same rule as the Space: leave it out and the demo
   still runs, just without the "use LLM classifier" checkbox doing anything.

Either host is fine — Spaces has a slightly larger free tier and a friendlier UI for
this kind of small demo; Community Cloud is convenient if you're already living in
your GitHub repo. Pick one, don't feel obliged to set up both.
