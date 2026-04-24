# Run frontend

```bash
npm run dev --prefix frontend -- --host 0.0.0.0
```

# Run Backend

```sh
source backend/venv/bin/activate && uvicorn main:app --reload --app-dir backend --host 0.0.0.0 --port 8000
```
