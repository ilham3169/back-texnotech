from fastapi import APIRouter, HTTPException, status, Response, Depends
from typing import Annotated
from redis import Redis

from .utils.services import get_redis


router = APIRouter(
    prefix="/others",
    tags=["others"]
)

redis_dependency = Annotated[Redis, Depends(get_redis)]



@router.delete("/cache/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cache(redis: redis_dependency):
    try:
        redis.flushall()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
