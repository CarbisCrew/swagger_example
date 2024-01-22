from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.responses import JSONResponse
from enum import Enum


app = FastAPI(docs_url="/docs/api/v1.0", title="Carbis Test API")


# Имитация базы данных
class User(BaseModel):
    username: str
    password: str
    role: str


users_db = [
    User(username="admin", password="admin", role="admin"),
    User(username="user", password="password", role="user"),
]

# Отвечает за кнопку Autorize и сохранение токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Post метод с выбором параметра и телом запроса
class UserEnum(str, Enum):
    one = "1"
    two = "2"
    three = "3"


class Person(BaseModel):
    name: str = "Alex"
    second_name: str = "Ray"


@app.post("/items/{item_id}", tags=["Users"])
async def create_user(
    item_id: UserEnum,
    body: Person,
):
    """
    Создание нового пользователя.
    """
    return {"user_id": item_id, "body": body}


# Проверка наличия токена (секьюрность)
def get_current_user(token: str = Depends(oauth2_scheme)):
    return token


# Docstring для описания метода
# dependencies для требования авторизации
# x_token: str = Header(None) для передачи x_token в хедере
# description="The ID of the item" описание непосредственно параметра
@app.get("/secure_endpoint", tags=["Authorization"], dependencies=[Depends(get_current_user)])
def secure_endpoint(
    x_token: str = Header(None, description="X-Token header for authentication"),
    y_token: str = Header(None, description="Y-Token header for authentication"),
    item_id: int = Query(None, description="The ID of the item"),
):
    """
    Секьюрный метод для проверки авторизации пользователя.
    """
    return {"item_id": item_id, "message": "Authorized user"}


# Проверка на авторизацию
def is_admin(token: str = Depends(oauth2_scheme)):
    return False


# include_in_schema для условий отображения в зависимости от юзера
@app.get("/secret_method", tags=["Admin"], include_in_schema=is_admin())
async def secret():
    """
    Секретный метод, доступный только админам.
    """
    return JSONResponse(content={"message": "This is a secret message."})


# Простейшая авторизация с выдачей токена "example_token"
@app.post("/docs/api/token", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Получение токена для авторизации пользователя.
    """
    user = None
    for one_user in users_db:
        if (
            one_user.username == form_data.username
            and one_user.password == form_data.password
        ):
            user = one_user
            break
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = "example_token"
    return {"access_token": token, "token_type": "bearer"}
