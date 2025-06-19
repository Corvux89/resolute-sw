

import uuid
from typing import Optional
from fastapi import APIRouter, Request, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from models.G0T0 import *
from models.db import get_db


api = APIRouter()


@api.get("/powers", response_class=JSONResponse)
async def powers(db: Session = Depends(get_db), level: Optional[int] = None):
    powers = db.query(Power).all()

    return jsonable_encoder(powers)