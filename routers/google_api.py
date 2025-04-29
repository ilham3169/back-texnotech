from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response  # type: ignore
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import text  # type: ignore
from database import sessionLocal
import logging
import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request  
import os

TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/google-api",
    tags=["google-api"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")


CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = ["https://www.googleapis.com/auth/webmasters"]
SITE_URL = 'sc-domain:texnotech.com'


CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [REDIRECT_URI],
    }
}

def get_credentials():
    creds = None
    token_path = "token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())
    
    return creds


@router.get("/search-console/impressions")
async def get_impressions():
    try:
        creds = get_credentials()
        service = build("webmasters", "v3", credentials=creds)

        request = {
            "startDate": "2025-03-29",  # Last 30 days
            "endDate": "2025-04-29",
            "dimensions": [],
            "rowLimit": 1,
        }

        response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
        impressions = response.get("rows", [{}])[0].get("impressions", 0)
        return impressions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching impressions: {str(e)}")
    
@router.get("/search-console/impressions-by-date")
async def get_impressions_by_date():
    try:
        creds = get_credentials()
        service = build("webmasters", "v3", credentials=creds)

        request = {
            "startDate": "2025-03-29",
            "endDate": "2025-04-29",
            "dimensions": ["date"],
            "rowLimit": 1000,
        }

        response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
        rows = response.get("rows", [])

        data = [{"date": row["keys"][0], "impressions": int(row.get("impressions", 0))} for row in rows]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@router.get("/google-api/analytics/visitors")
async def get_visitors():
    try:
        creds = get_credentials()
        service = build('analyticsreporting', 'v4', credentials=creds)

        # Prepare the report request
        request = {
            "reportRequests": [
                {
                    "viewId": 11162485317,
                    "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
                    "metrics": [{"expression": "ga:users"}],  # 'ga:users' counts the number of unique users
                }
            ]
        }

        response = service.reports().batchGet(body=request).execute()

        # Extract the users data from the response
        users = response['reports'][0]['data']['totals'][0]['values'][0]
        return {"users": users}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching visitors data: {str(e)}")
