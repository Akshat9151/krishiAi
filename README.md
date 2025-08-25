# krishiAi

Backend: FastAPI on port 8000
Frontend: Static files (serve on 5500)

Environment (.env at repo root) – optional overrides:
- DB_HOST=localhost
- DB_PORT=3306
- DB_USER=root
- DB_PASSWORD=IT@admin123456789
- DB_NAME=krishiAiDb
- JWT_SECRET=change_this_in_production

Run backend locally:
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

Auth flow:
- POST /auth/register {username, password}
- POST /auth/login {username, password} → sets http-only cookie `krishi_token`
- GET /auth/whoami (requires cookie)
- POST /auth/logout clears cookie

Frontend integration:
- Login/Register pages use fetch with `credentials: "include"` and rely on the cookie
- App checks `/auth/whoami` to gate access; no localStorage for auth

Serve frontend:
python3 -m http.server 5500 --directory frontend