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

---

## Развертывание на Windows 11 (пошагово)

Ниже инструкция под ваш стек: **GitHub Desktop + VS Code + DBeaver/PostgreSQL + браузер**.

### 1) Что установить
1. **Python 3.11+** (рекомендуется 3.11 или 3.12)
2. **PostgreSQL 15+** (или ваш установленный PostgreSQL)
3. (Опционально) **pgAdmin** — не обязателен, если используете DBeaver

Проверьте в PowerShell:
```powershell
python --version
pip --version
```

### 2) Клонировать проект
Через GitHub Desktop:
- `File -> Clone repository...`
- Выберите репозиторий `VKR2026`
- Папка, например: `C:\Projects\VKR2026`

Или через git:
```powershell
git clone <URL_ВАШЕГО_РЕПО>
cd VKR2026
```

### 3) Создать БД в PostgreSQL
В DBeaver:
1. Подключитесь к вашему PostgreSQL серверу.
2. Создайте БД `VKR2026` (UTF-8).
3. Откройте SQL Editor для этой БД.
4. Выполните содержимое файла `sql/schema.sql`.

Альтернатива через psql:
```powershell
psql -U postgres -c "CREATE DATABASE "VKR2026";"
psql -U postgres -d "VKR2026" -f sql/schema.sql
```

### 4) Открыть проект в VS Code
- `File -> Open Folder...` -> папка `VKR2026`
- Откройте встроенный терминал (`Ctrl+``)

### 5) Настроить Python окружение
В терминале PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Если PowerShell блокирует активацию:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 6) Настроить подключение backend к PostgreSQL
По умолчанию backend использует:
- `postgresql+psycopg://postgres:postgres@localhost:5432/VKR2026`

Если у вас другой пользователь/пароль, задайте переменную окружения перед запуском:
```powershell
$env:DATABASE_URL = "postgresql+psycopg://<user>:<password>@localhost:5432/VKR2026"
```

### 7) Запустить backend
```powershell
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Проверка:
- Откройте `http://127.0.0.1:8000/api/health`
- Должен вернуться JSON: `{"status":"ok"}`

### 8) Запустить frontend
Вариант A (рекомендуется): поднять простой web-server в папке проекта:
```powershell
python -m http.server 5500
```
Открыть:
- `http://127.0.0.1:5500/frontend/index.html`

Вариант B: открыть `frontend/index.html` напрямую в браузере (может блокироваться политиками безопасности некоторых браузеров).

### 9) Проверка полного контура
1. На вкладке **Входные данные** нажмите **"Загрузить demo 100 точек"**.
2. Нажмите **"Обновить список миссий"** и убедитесь, что миссия появилась.
3. Выполните **Предобработку**.
4. На вкладке **Расчёт** запустите расчет.
5. На вкладке **Результаты** проверьте, что появились точки расчета.

Контур должен отрабатывать так:
`frontend -> backend API -> PostgreSQL -> backend API -> frontend`.

---

## Частые проблемы на Windows

### Ошибка подключения к БД
- Проверьте, что PostgreSQL служба запущена.
- Проверьте `host/port/user/password` в `DATABASE_URL`.
- Проверьте, что БД `VKR2026` существует.

### `ModuleNotFoundError`
- Убедитесь, что активировано `.venv`.
- Повторно выполните `pip install -r backend/requirements.txt`.

### Порт занят (`8000`/`5500`)
- Укажите другой порт:
```powershell
uvicorn backend.app.main:app --reload --port 8010
python -m http.server 5600
```

### CORS/доступ из браузера
- Backend уже настроен с CORS для прототипа.
- Используйте URL `http://127.0.0.1:8000` и `http://127.0.0.1:5500`.

---

## Быстрый старт (кратко)
```powershell
# 1) В папке проекта
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# 2) Применить схему (если psql настроен)
psql -U postgres -d "VKR2026" -f sql/schema.sql

# 3) Запустить backend
uvicorn backend.app.main:app --reload

# 4) В новом терминале запустить frontend server
python -m http.server 5500
```

Открыть: `http://127.0.0.1:5500/frontend/index.html`
