from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Measurement, Estimation, WeaponProfile
from ..schemas import StreamRunRequest, StreamRunOut
from ..services import weighted_least_squares_intersection, area_center_and_radius, pairwise_intersections, filter_anomalous_points, convex_hull

router = APIRouter(tags=['estimations'])


def _ensure_weapon_profiles(db: Session):
    if db.query(WeaponProfile).count() > 0:
        return
    db.add_all([
        WeaponProfile(name='РСЗО "Град"', category='РСЗО', min_range_km=5, max_range_km=20, lethal_radius_m=15, notes='залповое поражение площадной цели'),
        WeaponProfile(name='ОФС 122мм', category='Артиллерия', min_range_km=3, max_range_km=15, lethal_radius_m=12, notes='фугасный снаряд среднего радиуса'),
        WeaponProfile(name='ОФС 152мм', category='Артиллерия', min_range_km=5, max_range_km=24, lethal_radius_m=20, notes='повышенный радиус сплошного поражения'),
    ])
    db.flush()


def _pick_weapon(db: Session, radius: float) -> str:
    _ensure_weapon_profiles(db)
    options = db.query(WeaponProfile).order_by(WeaponProfile.lethal_radius_m).all()
    for w in options:
        if w.lethal_radius_m >= radius:
            return f'{w.name} ({w.category}, R={w.lethal_radius_m}м)'
    return f'{options[-1].name} ({options[-1].category}, R={options[-1].lethal_radius_m}м)'


@router.get('/estimations/{mission_id}')
def list_estimations(mission_id: str, db: Session = Depends(get_db)):
    rows = db.query(Estimation).filter(Estimation.mission_id == mission_id).order_by(Estimation.batch_no).all()
    return [{'batch_no': r.batch_no, 'x': r.estimated_x, 'y': r.estimated_y, 'rmse': r.rmse, 'created_at': r.created_at.isoformat()} for r in rows]


@router.post('/stream/run', response_model=StreamRunOut)
def stream_run(payload: StreamRunRequest, db: Session = Depends(get_db)):
    data = db.query(Measurement).filter(Measurement.mission_id == payload.mission_id, Measurement.is_valid.is_(True)).order_by(Measurement.timestamp_utc).all()
    if len(data) < 2:
        raise HTTPException(status_code=400, detail='Недостаточно данных')

    db.query(Estimation).filter(Estimation.mission_id == payload.mission_id).delete()

    points = []
    for i in range(0, len(data), payload.batch_size):
        batch = data[i:i + payload.batch_size]
        if len(batch) < 2:
            continue
        x, y, rmse = weighted_least_squares_intersection([{'uav_x': b.uav_x, 'uav_y': b.uav_y, 'bearing_deg': b.bearing_deg, 'quality_weight': b.quality_weight} for b in batch])
        points.append((x, y))
        db.add(Estimation(mission_id=payload.mission_id, batch_no=len(points), estimated_x=x, estimated_y=y, rmse=rmse))

    if not points:
        raise HTTPException(status_code=400, detail='Не удалось рассчитать точки')

    all_intersections = pairwise_intersections([{'uav_x': b.uav_x, 'uav_y': b.uav_y, 'bearing_deg': b.bearing_deg, 'quality_weight': b.quality_weight} for b in data])
    core_points = filter_anomalous_points(all_intersections, keep_ratio=0.85)
    region = convex_hull(core_points)

    center_x, center_y, radius = area_center_and_radius(points)
    accuracy = None
    if payload.mode == 'experimental' and payload.reference_x is not None and payload.reference_y is not None:
        accuracy = ((center_x - payload.reference_x) ** 2 + (center_y - payload.reference_y) ** 2) ** 0.5

    db.commit()
    return StreamRunOut(mission_id=payload.mission_id, mode=payload.mode, points_count=len(points), center_x=center_x, center_y=center_y, radius=radius, region_polygon=[[x, y] for x, y in region], suggested_grid_segments=payload.grid_segments, recommended_weapon=_pick_weapon(db, radius), accuracy_rmse=accuracy)
