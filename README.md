# VKR2026

Прототип ИС оценки координат источника излучения.

## База данных PostgreSQL
В `sql/schema.sql` реализована физическая схема БД, которая:
1. Покрывает логическую модель из отчёта (roles/users, input_data_sets, raw/processed_measurements, calculation_runs/results, aggregated_results, experimental_runs, destruction_means).
2. Сохраняет совместимость с текущим backend-кодом через таблицы `measurements`, `estimations`, `weapon_profiles`.

Это позволяет не ломать текущие API-эндпоинты и одновременно перейти на нормализованную модель данных.

## Применение схемы
```bash
psql -U postgres -d vkr2026 -f sql/schema.sql
```

## Запуск backend
```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```
