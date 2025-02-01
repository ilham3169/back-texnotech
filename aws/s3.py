from fastapi import APIRouter, File, UploadFile, Response

import boto3
from botocore.exceptions import NoCredentialsError

from starlette import status 

from dotenv import load_dotenv
import os
from datetime import datetime 


load_dotenv()

router = APIRouter(
    prefix="/files",
    tags=["files"]
)

# AWS Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME,
)

ALLOWED_IMAGE_TYPES = ["image/png", "image/gif", "image/avif", "image/jpg", 
    "image/jpeg", "image/jfif", "image/pjpeg", "image/pjp", "image/svg", "image/webp"]


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...)):

    try:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Invalid file type. Only images are allowed."
            )

        time = datetime.now()
        file_content = await file.read()
        file_name = "texnotech" +  "/" + file.filename + str(time)
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=file_content,
            ContentType=file.content_type,
        )
        file_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{file_name}"
        return file_url
    except NoCredentialsError:
        return None
    except Exception as e:
        return None
