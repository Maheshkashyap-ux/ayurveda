# GitHub Setup Guide

## Option 1: Upload through GitHub

1. Create a new empty GitHub repository.
2. Extract this ZIP.
3. Upload the folders and files into the repository.
4. Commit the files.
5. Open `README.md` to verify rendering.

## Option 2: Git from VS Code

```bash
git init
git add .
git commit -m "Initial project documentation and architecture"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_URL` with your actual repository URL.

## Mermaid diagrams

GitHub supports Mermaid blocks inside Markdown files. The `.mmd` files in `architecture/` are also useful when creating external SVG/PNG diagrams for presentations.

## Before submission

Search the repository for:
- passwords
- API keys
- access tokens
- private URLs
- personal data

Remove anything sensitive before making the repository public.
