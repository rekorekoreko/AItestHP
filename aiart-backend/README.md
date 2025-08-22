# AIArt Backend (FastAPI)

Run locally
- Requires Python 3.12 (pyenv recommended) and Poetry
- Install deps: poetry install
- Start dev server: poetry run fastapi dev app/main.py
- Server runs at http://127.0.0.1:8000

Environment variables (.env)
- ADMIN_PASSWORD=admin password for login
- JWT_SECRET=secret key for JWT
- MONGODB_URI=MongoDB connection string
- MONGODB_DB=database name
- MONGODB_COLLECTION=collection name

Notes
- Data is stored in MongoDB; configure connection via env variables above.
- Media files are saved under media/uploads and thumbnails under media/thumbs.

API
- POST /api/submissions (multipart: file, title, author_name, description?, tags?) -> {id,status}
- POST /api/admin/login {"password"} -> {token}
- GET /api/admin/submissions?status=pending|approved|rejected (Bearer token)
- POST /api/admin/submissions/{id}/approve (Bearer token)
- POST /api/admin/submissions/{id}/reject (form: reason) (Bearer token)
- GET /api/gallery
- GET /api/items/{id}
