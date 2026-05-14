from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Measurement
from ..schemas import MeasurementCreate, MeasurementOut, BatchIngestRequest, PreprocessRequest
from ..services import preprocess_rows

router = APIRouter(tags=['measurements'])


@router.post('/measurements', response_model=MeasurementOut)
def create_measurement(payload: MeasurementCreate, db: Session = Depends(get_db)):
    obj = Measurement(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post('/measurements/batch')
def ingest_batch(payload: BatchIngestRequest, db: Session = Depends(get_db)):
    for row in payload.rows:
        db.add(Measurement(**row.model_dump(), mission_id=payload.mission_id))
    db.commit()
    return {'ingested': len(payload.rows)}


@router.post('/measurements/preprocess')
def preprocess_dataset(payload: PreprocessRequest, db: Session = Depends(get_db)):
    data = db.query(Measurement).filter(Measurement.mission_id == payload.mission_id).order_by(Measurement.timestamp_utc).all()
    rows = [{'uav_x': d.uav_x, 'uav_y': d.uav_y, 'bearing_deg': d.bearing_deg, 'quality_weight': d.quality_weight} for d in data]
    cleaned, stats = preprocess_rows(rows, payload.min_quality, payload.outlier_sigma)
    for d in data:
        d.is_valid = False
    for i, row in enumerate(cleaned):
        if i < len(data):
            data[i].uav_x, data[i].uav_y, data[i].bearing_deg, data[i].quality_weight, data[i].is_valid = row['uav_x'], row['uav_y'], row['bearing_deg'], row['quality_weight'], True
    db.commit()
    return stats
