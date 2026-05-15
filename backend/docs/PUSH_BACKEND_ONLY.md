# Push backend only (keep frontend on student branches)

## Workflow

1. Stay on the **`backend`** branch.
2. Pull frontend when you need to test UI (see `FRONTEND_LOCAL.md`) — usually on `ad-page`.
3. Commit and push **only** files under `backend/`.

## Commands

```powershell
git checkout backend
git pull origin backend

# Stage ONLY backend
git add backend/
git status
# Confirm frontend2/ is NOT listed

git commit -m "feat(api): describe your backend change"
git push origin backend
```

## If Git tries to include frontend2 changes

```powershell
git restore frontend2/
```

The old `frontend/` (Next.js) folder has been removed from the `backend` branch.

## Optional: ignore local frontend edits on backend branch

```powershell
git update-index --assume-unchanged frontend2/index.html
```

Undo with:

```powershell
git update-index --no-assume-unchanged frontend2/index.html
```
