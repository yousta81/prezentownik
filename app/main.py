from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from datetime import datetime
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User, Gift, Reservation, Friendship
from auth import verify_password, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
import os
from fastapi.staticfiles import StaticFiles
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# obliczamy ścieżkę do folderu static w pakiecie app
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 🔹 Szablony Jinja2
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Endpoint logowania
@app.post("/login")
def login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        return HTMLResponse("Invalid credentials", status_code=401)

    # TOKEN ZAWIERA user.id
    token = jwt.encode({"sub": str(user.id)}, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401)

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401)

    return user

def get_owned_gift(gift_id: int, user: User, db: Session):
    gift = db.query(Gift).filter(
        Gift.id == gift_id,
        Gift.archived_at.is_(None)
    ).first()
    if not gift:
        raise HTTPException(404, "Gift not found")
    if gift.owner_id != user.id:
        raise HTTPException(403, "Not allowed")
    return gift

@app.exception_handler(401)
def unauthorized_handler(request: Request, exc):
    return RedirectResponse(url="/login", status_code=302)

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response



@app.get("/")
def home(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
   

    #wszystkie przyjaźnie uzytkownika
    friendships = db.query(Friendship).filter(
    (Friendship.user_id == current_user.id) |
    (Friendship.friend_id == current_user.id)
    ).all()

    friends_ids = [
    f.friend_id if f.user_id == current_user.id else f.user_id
    for f in friendships
    ]

    # pobierz wszystkie prezenty usera i jego friendsów poza zarchiwizowanymi
    gifts = db.query(Gift).filter(
    ((Gift.owner_id == current_user.id) | (Gift.owner_id.in_(friends_ids))) &
    (Gift.archived_at.is_(None))).all()

    # Pobranie wszystkich właścicieli i stworzenie unikalnej listy nazw
    owners = sorted({gift.owner.name for gift in gifts if gift.owner})

    # pobierz wszystkie rezerwacje
    reservations = db.query(Reservation).all()

    reserved_by_map = {r.gift_id: r.user.name for r in reservations}
    reserved_ids = set(reserved_by_map.keys())
    reserved_by_user_ids = {r.gift_id for r in reservations if r.reserved_by == current_user.id}
    

    def format_price(p):
        return {
            "unknown": "nieznany",
            "cheap": "0 - 50 zł",
            "medium": "50 - 100 zł",
            "expensive": "100 zł +"
        }.get(p, p)

    # budowanie ujednoliconej listy items
    items = [
        {
            "id": g.id,
            "name": g.name,
            "owner": g.owner.name if g.owner else "Brak właściciela",
            "image_url": g.image_url or "/static/logo.png",
            "product_url": g.product_url,
            "description": g.description,
            "est_price": format_price(g.est_price),
            "is_reserved": g.id in reserved_ids,
            "is_reserved_by_user": g.id in reserved_by_user_ids,
            "reserved_by": reserved_by_map.get(g.id, None)
        }
        for g in gifts
    ]

    items = sorted(
        items, 
        key=lambda i: (
        i["is_reserved"],
        i["owner"].lower()     # sortowanie alfabetyczne
    ))

    # print([i["owner"] for i in items])

    reserved_items = [i for i in items if i["is_reserved"]]
    reserved_by_user_items = [i for i in items if i["is_reserved_by_user"]]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Prezentownik",
            "user": {"name": current_user.name, "is_admin": True},
            "items": items,
            "owners": owners,
            "reserved_items": reserved_items,
            "reserved_by_user_items": reserved_by_user_items
        }
    )

@app.post("/gifts/")
def create_gift(
    name: str = Form(...),
    description: str = Form(""),
    est_price: str = Form(""),
    image_url: str = Form(""),
    product_url: str = Form(""),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    

    new_gift = Gift(
        owner_id=current_user.id,
        name=name,
        description=description,
        est_price=est_price,
        image_url=image_url,
        product_url=product_url
    )
    db.add(new_gift)
    db.commit()
    db.refresh(new_gift)

    return {"message": "Gift created", "gift": new_gift}

@app.get("/gifts/")
def gift_page(request: Request, current_user: User = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(
        "gifts.html",
        {"request": request, "user": current_user}
    )

@app.get("/gifts/{gift_id}/edit")
def edit_gift_page(
    gift_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    gift = get_owned_gift(gift_id, current_user, db)

    return templates.TemplateResponse("gift_edit.html", {
            
            "request": request,
            "item": {
                "id": gift.id, 
                "name": gift.name, 
                "image_url": gift.image_url,
                "product_url": gift.product_url,
                "description": gift.description,
                "est_price": gift.est_price
            }
    })

@app.post("/gifts/{gift_id}/edit")
def update_gift(
    gift_id: int,
    name: str = Form(...),
    description: str = Form(None),
    est_price: str = Form(None),
    product_url: str = Form(None),
    image_url: str = Form(None),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    gift = db.query(Gift).filter(
        Gift.id == gift_id,
        Gift.archived_at == None
    ).first()

    if not gift:
        raise HTTPException(404, "Gift not found")

    if gift.owner_id != current_user.id:
        raise HTTPException(403, "Not allowed")

    # aktualizacja danych
    gift.name = name
    gift.description = description
    gift.est_price = est_price
    gift.product_url = product_url
    gift.image_url = image_url
    gift.updated_at = datetime.now()

    db.commit()
    db.refresh(gift)

    return RedirectResponse(url="/#my_wishlist_section", status_code=302)

@app.post("/gifts/{gift_id}/delete")
def delete_gift(
    gift_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    gift = db.query(Gift).filter(
        Gift.id == gift_id,
        Gift.archived_at == None
    ).first()

    if not gift:
        raise HTTPException(404, "Gift not found")

    gift.archived_at = datetime.now()
    db.commit()

    return RedirectResponse(url="/#my_wishlist_section", status_code=302)

@app.post("/reservations/toggle")
def toggle_reservation(
    gift_id: int = Form(...),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    reservation = db.query(Reservation).filter(Reservation.gift_id == gift_id).first()

    if reservation:
        # Kto aktualnie trzyma rezerwację
        who_reserved = db.query(User).filter(User.id == reservation.reserved_by).first()

        # ktoś inny zarezerwował → blokujemy
        if reservation.reserved_by != current_user.id:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "reserved_by_someone_else",
                    "reserved_by": who_reserved.name
                }
            )

        # użytkownik zwalnia swoją rezerwację
        db.delete(reservation)
        db.commit()
        return {"status": "released", "gift_id": gift_id}

    # brak rezerwacji → rezerwujemy
    new_res = Reservation(
        gift_id=gift_id,
        reserved_by=current_user.id,
        reserved_at=datetime.now()
    )
    db.add(new_res)
    db.commit()

    return {"status": "reserved", "gift_id": gift_id}

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using Uvicorn
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True, workers=2)