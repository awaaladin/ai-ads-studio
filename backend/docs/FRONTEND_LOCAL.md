# Run the student frontend locally (you pull — do not push)

Use the **unified stack** (recommended): see **`LOCAL_FULL_STACK.md`**.

```powershell
cd backend
powershell -File scripts/dev.ps1
```

Then open http://localhost:8000/

Student files are copied into `backend/dev-frontend/` (gitignored). Your repo’s `frontend2/` folder is **not** modified.

To refresh UI from GitHub:

```powershell
powershell -File scripts/pull-frontend.ps1
```

Push rules: **`PUSH_BACKEND_ONLY.md`**
