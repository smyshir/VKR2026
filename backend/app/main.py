from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import measurements, estimations

app = FastAPI(title='ИС оценки координат источника излучения')
Base.metadata.create_all(bind=engine)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(measurements.router, prefix='/api')
app.include_router(estimations.router, prefix='/api')


@app.get('/api/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
