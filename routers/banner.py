from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database import sessionLocal
from models import Banner
from schemas import BannerResponse, BannerCreate, BannerUpdate, BannerStatusUpdate
import logging
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("Asia/Baku")

router = APIRouter(
    prefix="/api/banners",
    tags=["banners"]
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
logger = logging.getLogger("uvicorn.error")

@router.get("", response_model=List[BannerResponse])
def get_banners(db: Session = Depends(get_db)):
    """Get all banners, ordered by creation date (newest first)"""
    try:
        logger.debug("Fetching all banners")
        db_banners = db.query(Banner).order_by(Banner.created_at.desc()).all()
        logger.debug(f"Found {len(db_banners)} banners")
        return db_banners
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

@router.get("/active", response_model=List[BannerResponse])
def get_active_banners(db: Session = Depends(get_db)):
    """Get only active banners for frontend display"""
    try:
        logger.debug("Fetching active banners")
        db_banners = db.query(Banner).filter(Banner.active == True).order_by(Banner.created_at.desc()).all()
        logger.debug(f"Found {len(db_banners)} active banners")
        return db_banners
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

@router.get("/count", status_code=status.HTTP_200_OK)
async def get_banner_count(db: db_dependency):
    """Get total count of banners"""
    try:
        logger.debug("Fetching banner count")
        banner_count = db.query(Banner).count()
        logger.debug(f"Total banners: {banner_count}")
        return {"count": banner_count}
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

@router.get("/{banner_id}", response_model=BannerResponse, status_code=status.HTTP_200_OK)
async def get_banner(banner_id: int, db: db_dependency):
    """Get a specific banner by ID"""
    try:
        logger.debug(f"Fetching banner with ID: {banner_id}")
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            logger.warning(f"Banner with ID {banner_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
        return banner
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

@router.post("", response_model=BannerResponse, status_code=status.HTTP_201_CREATED)
async def create_banner(banner_data: BannerCreate, db: db_dependency):
    """Create a new banner"""
    try:
        logger.debug(f"Creating new banner: {banner_data.title}")
        banner_data_dict = banner_data.dict(exclude_unset=True)
        
        new_banner = Banner(**banner_data_dict)
        db.add(new_banner)
        db.commit()
        db.refresh(new_banner)
        
        logger.info(f"Banner created successfully with ID: {new_banner.id}")
        return new_banner
    except Exception as e:
        logger.error(f"Error creating banner: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create banner: {str(e)}")

@router.put("/{banner_id}", response_model=BannerResponse, status_code=status.HTTP_200_OK)
async def update_banner(banner_id: int, banner_data: BannerUpdate, db: db_dependency):
    """Update an existing banner"""
    try:
        logger.debug(f"Updating banner with ID: {banner_id}")
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            logger.warning(f"Banner with ID {banner_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")

        # Update only provided fields
        update_data = banner_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(banner, field, value)
        
        banner.updated_at = datetime.now(TIMEZONE)
        db.commit()
        db.refresh(banner)
        
        logger.info(f"Banner {banner_id} updated successfully")
        return banner
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating banner: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update banner: {str(e)}")

@router.delete("/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_banner(banner_id: int, db: db_dependency):
    """Delete a banner"""
    try:
        logger.debug(f"Deleting banner with ID: {banner_id}")
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        
        if not banner:
            logger.warning(f"Banner with ID {banner_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
        
        db.delete(banner)
        db.commit()
        
        logger.info(f"Banner {banner_id} deleted successfully")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting banner: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete banner: {str(e)}")

@router.patch("/{banner_id}/status", response_model=BannerResponse, status_code=status.HTTP_200_OK)
async def update_banner_status(banner_id: int, update_data: BannerStatusUpdate, db: db_dependency):
    """
    Update the active status of an existing banner.
    Expects a JSON payload with 'active' field, e.g., {"active": true}
    """
    try:
        logger.debug(f"Updating status for banner ID: {banner_id}")
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            logger.warning(f"Banner with ID {banner_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")

        # Update the banner's active status
        banner.active = update_data.active
        banner.updated_at = datetime.now(TIMEZONE)
        db.commit()
        db.refresh(banner)
        
        logger.info(f"Banner {banner_id} status updated to: {update_data.active}")
        return banner
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating banner status: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update banner status: {str(e)}")