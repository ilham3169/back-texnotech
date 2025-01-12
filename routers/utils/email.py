from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors

from itsdangerous import URLSafeTimedSerializer, BadTimeSignature,SignatureExpired

from pathlib import Path
from dotenv import load_dotenv
import os

from schemas import EmailStr


load_dotenv()

token_algo = URLSafeTimedSerializer(os.getenv("SECRET"), salt='Email_Verification_&_Forgot_password')

config = ConnectionConfig(
    MAIL_USERNAME = str(os.getenv('MAIL_USERNAME')),
    MAIL_PASSWORD = str(os.getenv('MAIL_PASSWORD')),
    MAIL_FROM = str(os.getenv('MAIL_FROM')),
    MAIL_PORT = int(os.getenv('MAIL_PORT')),
    MAIL_SERVER = str(os.getenv('MAIL_SERVER')),
    MAIL_FROM_NAME= str(os.getenv("MAIL_FROM_NAME")),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    TEMPLATE_FOLDER = Path(__file__).resolve().parent.parent.parent/'templates/',
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
)

async def send_email_async(subject:str, email_to:EmailStr, body:dict, template:str):
    
    message = MessageSchema(
        subject=subject,
        recipients= [email_to,],
        template_body=body,
        subtype=MessageType.html,
    )

    fm = FastMail(config)
    try:
        await fm.send_message(message, template)
        return True
    except ConnectionErrors as e:
        return False
    

# Token 

def token(email: EmailStr):
    _token = token_algo.dumps(email)
    return _token


def verify_token(token:str):
    try:
        email = token_algo.loads(token, max_age=1800)
    except SignatureExpired:
        return None
    except BadTimeSignature:
        return None
    return {'email':email, 'check':True}
