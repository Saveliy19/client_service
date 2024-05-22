from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from asyncpg.exceptions import UniqueViolationError


from app.models import UserRegistration, UserToToken, Token, NewPassword, UserAbout, TokenForData
from app.auth import hash_password, authentificate_user, create_access_token, verify_token
from app.utils import add_user, get_city_by_user_id, get_user_by_id, update_user_password_by_user_id, get_cities_per_region

router = APIRouter()

# обработка аутентификаций по токену
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# маршрут регистрации нового пользователя в системе
@router.post("/registration")
async def registration(user_data: UserRegistration):
    try:
        await add_user(user_data.email, 
                        (await hash_password(user_data.password)).decode('utf-8'), 
                        user_data.last_name, 
                        user_data.first_name, 
                        user_data.patronymic,
                        False,
                        user_data.city)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "User successfully registered"}, status.HTTP_201_CREATED

# маршрут для создания админа
@router.post("/make_admin")
async def make_admin(admin: UserRegistration):
    try:
        await add_user(admin.email, 
                        (await hash_password(admin.password)).decode('utf-8'), 
                        admin.last_name, 
                        admin.first_name, 
                        admin.patronymic,
                        True,
                        admin.city)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "User successfully registered"}, status.HTTP_201_CREATED

# маршрут для получения access токена     
@router.post("/token")
async def login_for_access_token(user_data: UserToToken):
    user = await authentificate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.id, "is_moderator": user.is_moderator, "email": user.email})
    return Token(access_token=access_token, token_type="bearer", is_moderator=user.is_moderator)


# маршрут для верификации пользователя
@router.post("/verify_user")
async def verify_user(token_data: TokenForData):
    user_id = await verify_token(token_data.token)
    if user_id:
        user_data = await get_user_by_id(user_id)
        if (user_data is None):
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_data["id"], "is_moderator": user_data["is_moderator"], "email": user_data["email"]}, status.HTTP_200_OK


# маршрут для получения списка всех городов системы
@router.get("/get_cities")
async def get_cities():
    try:
        cities_per_region = await get_cities_per_region()
    except:
        raise HTTPException(status_code=500)
    return cities_per_region, status.HTTP_200_OK

# маршрут для обновления пароля пользователя
@router.post("/change_password")
async def change_user_password(user_data: NewPassword):
    user_id = await verify_token(user_data.token)
    if user_id:
        if (await get_user_by_id(user_id) is None):
            raise HTTPException(status_code=404, detail="User not found")
        await update_user_password_by_user_id((await hash_password(user_data.password)).decode('utf-8'), user_id)
    else:
        raise HTTPException(status_code=404, detail="User not found")
    return status.HTTP_200_OK

# маршрут для получения данных о пользователе
@router.post("/get_data")
async def get_user_data(token_data: TokenForData):
    user_id = await verify_token(token_data.token)
    if user_id:
        info = await get_user_by_id(user_id)
        if (info is None):
            raise HTTPException(status_code=404, detail="User not found")
        city = await get_city_by_user_id(user_id)
    else:
        raise HTTPException(status_code=404, detail="User not found")
    return UserAbout(id = info["id"],
                     email =info["email"],
    		        last_name = info["last_name"], 
                     first_name=info["first_name"], 
                     patronymic=info["patronymic"], 
                     rating=info["rating"], 
                     city=city["city_name"],
                     region = city["region_name"]), status.HTTP_200_OK