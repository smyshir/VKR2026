# VKR2026

Полнофункциональный прототип ИС оценки координат источника излучения (Backend + Frontend + PostgreSQL).

## Что связано воедино
- **Backend (FastAPI)**: загрузка измерений, предобработка, расчет по батчам, результаты.
- **Database (PostgreSQL)**: нормализованная схема + совместимость текущего backend.
- **Frontend (HTML/JS)**: рабочие экранные формы "Главная / Входные данные / Расчёт / Результаты" с вызовами API.

## Основные API
- `GET /api/health`
- `GET /api/missions`
- `POST /api/measurements/batch`
- `POST /api/measurements/preprocess`
- `POST /api/stream/run`
- `GET /api/estimations/{mission_id}`

## Запуск
```bash
psql -U postgres -d vkr2026 -f sql/schema.sql
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Открыть UI: `frontend/index.html` (через локальный web server или напрямую в браузере).
