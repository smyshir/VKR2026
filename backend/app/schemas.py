from datetime import datetime
from pydantic import BaseModel, Field


class MeasurementCreate(BaseModel):
    mission_id: str
    timestamp_utc: datetime
    uav_x: float | None = None
    uav_y: float | None = None
    bearing_deg: float | None = Field(default=None, ge=0, le=360)
    quality_weight: float | None = Field(default=1.0, gt=0)


class BatchIngestRequest(BaseModel):
    mission_id: str
    rows: list[MeasurementCreate]


class PreprocessRequest(BaseModel):
    mission_id: str
    min_quality: float = 0.7
    outlier_sigma: float = 2.0


class StreamRunRequest(BaseModel):
    mission_id: str
    mode: str = Field(pattern='^(experimental|practical)$')
    batch_size: int = Field(default=100, ge=1, le=10000)
    grid_segments: int = Field(default=30, ge=10, le=100)
    reference_x: float | None = None
    reference_y: float | None = None


class StreamRunOut(BaseModel):
    mission_id: str
    mode: str
    points_count: int
    center_x: float
    center_y: float
    radius: float
    region_polygon: list[list[float]]
    suggested_grid_segments: int
    recommended_weapon: str
    accuracy_rmse: float | None = None
