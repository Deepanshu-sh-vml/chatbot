# Northwind Support Co-pilot — Init and Push to GitHub

This guide covers initializing the repo and pushing to GitHub.

## Step 1: Initialize Local Repository

```bash
cd northwind-support-copilot

# Initialize git
git init

# Configure git (if needed)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial: Northwind Support Co-pilot v1.0 - 4-stage LLM prompt pipeline"
```

## Step 2: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

```bash
# Ensure you're logged in
gh auth login

# Create repository
gh repo create northwind-support-copilot \
  --private \
  --source=. \
  --remote=origin \
  --push

# Verify
git remote -v
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/new
2. Create a new repository named `northwind-support-copilot`
3. Set it to **Private** (recommended for enterprise use)
4. Do NOT initialize with README, .gitignore, or LICENSE (we have those)
5. Click "Create repository"

Then run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/northwind-support-copilot.git
git branch -M main
git push -u origin main
```

## Step 3: Verify Push

```bash
git remote -v
# Should show:
# origin  https://github.com/YOUR_USERNAME/northwind-support-copilot.git (fetch)
# origin  https://github.com/YOUR_USERNAME/northwind-support-copilot.git (push)

git log --oneline
# Should show your commit

git status
# Should show "On branch main" and "nothing to commit"
```

## Step 4: Protect Main Branch (Optional but Recommended)

On GitHub:
1. Go to Settings → Branches
2. Add a branch protection rule for `main`
3. Enable:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging

---

## Continuous Improvements

### To Add New Changes

```bash
# Make changes to files
echo "# Updated feature" >> README.md

# Stage changes
git add README.md

# Commit with descriptive message
git commit -m "docs: update README with new feature"

# Push to GitHub
git push origin main
```

### To Create a Feature Branch

```bash
git checkout -b feature/improved-prompts
# Make changes...
git add .
git commit -m "feat: improve stage 3 prompt clarity"
git push origin feature/improved-prompts

# Then create a Pull Request on GitHub for review
```

---

## Clone Repository (For Team)

```bash
git clone https://github.com/YOUR_USERNAME/northwind-support-copilot.git
cd northwind-support-copilot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.cli run --all
```

---

**Ready to push!** Run the commands above to get your repo on GitHub.
