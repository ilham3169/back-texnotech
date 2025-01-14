from datetime import timedelta, datetime, timezone
from typing import Annotated 

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from sqlalchemy.orm import Session
from starlette import status 

from passlib.context import CryptContext
from jose import jwt, JWTError

from database import sessionLocal 
from models import User
from schemas import UserCreate, Token, EmailSchema, PasswordResetConfirmModel
from routers.utils import email as email_service
from routers.utils import services as utils_service

import os

from dotenv import load_dotenv


load_dotenv()


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM =os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = sessionLocal()
    
    try:
        yield db
    finally:
        db.close() 

db_dependency = Annotated[Session, Depends(get_db)]


# Create user
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user: UserCreate):
    
    # Check is user with this phone number already exists
    user_phone_number = db.query(User).filter(User.phone == create_user.phone).first()
    if user_phone_number:
        raise HTTPException(status_code=400, detail="User with this phone number already exists")

    # Check is user with this email already exists
    if create_user.email:
        user_email = db.query(User).filter(User.email == create_user.email).first()
        if user_email:
            raise HTTPException(status_code=400, detail="User with this phone number already exists")

    # Check password security level
    password_status, password_detail = utils_service.is_secure_password(create_user.password)
    if not password_status:
        raise HTTPException(status_code=400, detail=password_detail)

    # Check if password and confirm_password match
    if create_user.password != create_user.confirm_password:
        raise HTTPException(status_code=400, detail="User's passwords don't match")

    # Create user
    create_user_model = User(
        first_name = create_user.first_name,
        last_name = create_user.last_name,
        hashed_pass = bcrypt_context.hash(create_user.password),
        email = create_user.email,
        phone = create_user.phone,
        is_active = False,
        fin = create_user.fin,
        provider = "phone"
    )
    # Verification email sending
    token = email_service.token(create_user.email)
    email_verification_endpoint = f'http://127.0.0.1:8000/auth/confirm-email/{token}/'
    mail_body = {
        'email':create_user.email,
        'project_name': "Texno Tech",
        'url': email_verification_endpoint
    }

    mail_status = await email_service.send_email_async(subject="Email Verification: Registration Confirmation",
        email_to=create_user.email, body=mail_body, template='email_verification.html') 

    if mail_status:
        db.add(create_user_model)
        db.commit()
        return {
            "message":"mail for Email Verification has been sent, kindly check your inbox.",
            "status": status.HTTP_201_CREATED
        }
    else:
        return {
            "message":"mail for Email Verification failed to send, kindly reach out to the server guy.",
            "status": status.HTTP_503_SERVICE_UNAVAILABLE
        }


# Get Access & Refresh token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):
    
    # Check if user exists
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    
    token = create_access_token(user.phone, user.id, timedelta(minutes=20))
    refresh_token = create_refresh_token(user.phone, user.id)

    return {"access_token": token, "refresh_token": refresh_token, "token_type": "bearer"}


# Refresh Access & Refresh token
@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type."
            )
        
        user_id = payload.get("id")
        phone_number = payload.get("sub")
                
        if not user_id or not phone_number:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )
        
        access_token = create_access_token(phone_number, user_id, timedelta(minutes=20))
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )


def authenticate_user(phone_number: str, password: str, db):
    
    user = db.query(User).filter(User.phone == phone_number).first()
    # Check if user with such username exists
    if not user:
        return False
    # Check if input password matches user's actual password
    if not bcrypt_context.verify(password, user.hashed_pass):
        return False
    
    return user


def create_access_token(phone_number: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": phone_number, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(phone_number: str, user_id: int):
    encode = {"sub": phone_number, "id": user_id}
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    encode.update({"exp": expires, "type": "refresh"})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends (oauth2_bearer)],
                           db: db_dependency
                           ):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get ('sub')
        user_id: int = payload.get('id')

        # Check if payload is valid
        if phone_number is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user.')
        
        user = db.query(User).filter(User.id == user_id).first()
        return {"phone": phone_number, 
                "id": user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_admin": user.is_admin,
                }
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')


# Verify Access token
@router.get("/token/verify", status_code=status.HTTP_200_OK)
async def verify_token(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        user_id: int = payload.get("id")

        if phone_number is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        return {"is_authenticated": True}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")



# Validate Verification Email token
@router.get('/email/verification/{token}', status_code=status.HTTP_200_OK)
async def user_verification(token:str, db: db_dependency):

    token_data = email_service.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail= "Token for Email Verification has expired."
        )
    
    user = db.query(User).filter(User.email == token_data['email']).first()

    if not user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"User with email {token_data['email']} does not exist"
        )
    
    if user.mail_verified:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= f"User with email {user.email}, is already verified"
        )
    
    user.mail_verified = True
    db.commit()
    db.refresh(user)
    
    return {
            'message':'Email Verification Successful',
            'status':status.HTTP_202_ACCEPTED
        }


# Resend Verification Email
@router.post('/email/verification/resend', status_code=status.HTTP_201_CREATED)
async def resend_email_verification(email_data:EmailSchema, db: db_dependency):
 
    user_check = db.query(User).filter(User.email == email_data.email).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail= "User information does not exist")
        
    if user_check.is_verified:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= f"User with email {user_check.email}, is already verified"
        )    

    token = email_service.token(email_data.email)
    email_verification_endpoint = f'https://eventify-az.onrender.com/auth/confirm-email/{token}/'
    mail_body = { 
        'email': user_check.email,
        'project_name': "eventify.az",
        'url': email_verification_endpoint
    }

    mail_status = await email_service.send_email_async(subject="Email Verification: Registration Confirmation",
    email_to=str(user_check.email), body=mail_body, template='email_verification.html')

    if mail_status:
        return {
            "message":"mail for Email Verification has been sent, kindly check your inbox.",
            "status": status.HTTP_201_CREATED
        }
    else:
        return {
            "message":"mail for Email Verification failled to send, kindly reach out to the server guy.",
            "status": status.HTTP_503_SERVICE_UNAVAILABLE
        }
    

# Send Password Reset Email
@router.post("/password/reset")
async def password_reset_request(data: EmailSchema, db: db_dependency):

    email = data.email
    # Check if user with input email exists
    if not db.query(User).filter(User.email == email).first():
        return {
            "message":"User with this email address doesn't exist",
            "status": status.HTTP_400_BAD_REQUEST
        }

    token = email_service.token(email)
    link = f"https://eventify-az.onrender.com/auth/password-reset-confirm/{token}"

    mail_body = {
        'email': email,
        'project_name': "eventify.az",
        'url': link
    }
    mail_status = await email_service.send_email_async(subject="Password reset",
        email_to=email, body=mail_body, template='reset_password.html') 

    if mail_status:
        return {
            "message":"Please check your email for instructions to reset your password.",
            "status": status.HTTP_200_OK
        }
    
    return {
        "message":"mail for password reset failled to send, kindly reach out to the server guy.",
        "status": status.HTTP_503_SERVICE_UNAVAILABLE
    }


# Validate Password Reset Token
@router.post("/password/reset/confirm/{token}")
async def reset_account_password(token: str, passwords: PasswordResetConfirmModel, db: db_dependency):
    
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    # Make sure passwords match
    if new_password != confirm_password:
        raise HTTPException(detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST)
    # Make sure password is secure
    password_status, password_detail = utils_service.is_secure_password(new_password)
    if not password_status:
        raise HTTPException(detail=password_detail, status_code=400)

    token_data = email_service.verify_token(token)
    # Make sure mail is valid
    email = token_data["email"]
    if email:
        # Make sure user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                detail="User doesn't exist", 
                status_code=status.HTTP_403_FORBIDDEN
            )
        # Hash the password
        passwd_hash = bcrypt_context.hash(new_password)
        # Update user password
        setattr(user, "hashed_password", passwd_hash)
        # Commit changes to database
        db.commit()
        db.refresh(user)

        return {
            "message":"Password reset Successfully.",
            "status": status.HTTP_200_OK
        }

    return {
            "message":"Token is not valid, or expired.",
            "status": status.HTTP_400_BAD_REQUEST
        }


# Get user data
@router.post("/user")
async def user_data(user: Annotated[get_current_user, Depends()]):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return user   


# Get user email verification status
@router.get("/user/verification", status_code=status.HTTP_200_OK)
def get_verification_status(email: str, db: db_dependency):

    user = db.query(User).filter(User.email == email).first()
    if user.mail_verified:
        return True

    return False
