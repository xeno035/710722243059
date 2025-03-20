from fastapi import FastAPI, Depends, HTTPException, Header
import jwt
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQyNDU4MzYyLCJpYXQiOjE3NDI0NTgwNjIsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjI1NjljMDJiLTU2NzMtNGM3MS05ODk3LTIyZTFkZmJjNTlhNyIsInN1YiI6IjIyYWQwNTlAZHJuZ3BpdC5hYy5pbiJ9LCJjb21wYW55TmFtZSI6IkRyLk5HUElUIiwiY2xpZW50SUQiOiIyNTY5YzAyYi01NjczLTRjNzEtOTg5Ny0yMmUxZGZiYzU5YTciLCJjbGllbnRTZWNyZXQiOiJUWklzQnBYRVFTcXJvZmJsIiwib3duZXJOYW1lIjoiVmlzaG51IEsiLCJvd25lckVtYWlsIjoiMjJhZDA1OUBkcm5ncGl0LmFjLmluIiwicm9sbE5vIjoiNzEwNzIyMjQzMDU5In0.Yhj0e3zxFJc6-bGc-yKpJIrrr18HLlIMhXZO_1xqViw"
ALGORITHM = "HS256"

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

fake_users = [{"id": i, "name": f"User {i}"} for i in range(1, 11)]
fake_posts = [{"id": i, "likes": i * 10, "content": f"Post {i}"} for i in range(1, 11)]

@app.get("/posts/popular", dependencies=[Depends(verify_jwt_token)])
def get_popular_posts():
    return {"popular_posts": sorted(fake_posts, key=lambda x: x["likes"], reverse=True)[:5]}

@app.get("/users/top", dependencies=[Depends(verify_jwt_token)])
def get_top_users():
    return {"top_users": sorted(fake_users, key=lambda x: x["id"], reverse=True)[:5]}

@app.get("/posts/recent", dependencies=[Depends(verify_jwt_token)])
def get_recent_posts():
    return {"recent_posts": sorted(fake_posts, key=lambda x: x["id"], reverse=True)[:5]}