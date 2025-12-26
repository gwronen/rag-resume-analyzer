# GitHub Setup Instructions

## Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Choose a repository name (e.g., `rag-resume-analyzer`)
3. Select Public or Private
4. **Don't** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

## Step 2: Connect and Push
After creating the repository, run these commands (replace `YOUR_USERNAME` and `REPO_NAME`):

```bash
# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Alternative: Using SSH (if you have SSH keys set up)
```bash
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Important Notes
- The `.env` file is excluded (contains your API key)
- The `faiss_index` folder is excluded (can be regenerated)
- PDF files in `data/` are included - remove them from git if they're sensitive:
  ```bash
  git rm --cached data/*.pdf
  echo "data/*.pdf" >> .gitignore
  git commit -m "Remove PDFs from tracking"
  ```

