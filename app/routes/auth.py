from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import SessionLocal
from app.models import User
from app.security import verify_password

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_form():
    return """
    <html>
        <body>
            <h2>Login</h2>
            <form method="post">
                <input name="username" placeholder="Username" required><br><br>
                <input type="password" name="password" placeholder="Password" required><br><br>
                <button type="submit">Log in</button>
            </form>
        </body>
    </html>
    """


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user or not verify_password(password, user.password_hash):
        return HTMLResponse("Invalid credentials", status_code=401)

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
