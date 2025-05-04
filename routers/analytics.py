from fastapi import APIRouter, HTTPException, status
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
import os
import logging

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

logger = logging.getLogger("uvicorn.error")

# Set the path to the service account JSON key
credentials_path = os.path.join(os.getcwd(), "cool-arch.json")
logger.info(f"Credentials path: {credentials_path}")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

GA_PROPERTY_ID = os.getenv("GA_PROPERTY_ID")

@router.get("/users-last-24h", status_code=status.HTTP_200_OK)
async def get_users_last_24h():
    try:
        logger.info("Initializing BetaAnalyticsDataClient")
        client = BetaAnalyticsDataClient()
        logger.info("Client initialized successfully")
        
        logger.info(f"Creating RunReportRequest for property: properties/{GA_PROPERTY_ID}")
        request = RunReportRequest(
            property=f"properties/{GA_PROPERTY_ID}",
            date_ranges=[DateRange(start_date="yesterday", end_date="today")],
            metrics=[Metric(name="activeUsers")],
        )
        logger.info("RunReportRequest created successfully")

        logger.info("Running report Theoretical API report")
        response = client.run_report(request)
        logger.info("Report run successfully")

        user_count = int(response.rows[0].metric_values[0].value) if response.rows else 0
        logger.debug(f"Fetched {user_count} users from Google Analytics")
        return {"count": user_count}
    except Exception as e:
        logger.error(f"Error fetching Google Analytics data: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Stack trace: ", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching analytics data: {str(e)}")