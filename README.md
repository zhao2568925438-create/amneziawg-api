# AmneziaWG API

Лёгкий API для управления `AmneziaWG` через `SSH`.

Что умеет:

- добавлять серверы;
- показывать список серверов и их доступность;
- создавать клиентов;
- удалять клиентов;
- показывать список клиентов;
- продлевать подписку клиента по дате;
- отдавать ссылки на скачивание `.conf` и `.png`.

## Стек

- `FastAPI`
- `SQLite`
- `SSH` к серверам с установленным `manage_amneziawg.sh`

## Переменные окружения

Пример `.env`:

```env
API_HOST=127.0.0.1
API_PORT=8000
API_TOKEN=TEST
DATABASE_PATH=./data/app.db
STORAGE_DIR=./storage
```

## Локальный запуск

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить API:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

## Docker Compose

Сборка и запуск:

```bash
docker compose build
docker compose up -d
```

## Авторизация

Во всех запросах нужен заголовок:

```text
Authorization: Bearer <API_TOKEN>
```

## Локальные примеры запросов

Ниже примеры для локального запуска:

```text
http://127.0.0.1:8000
```

Токен:

```text
TEST
```

### 1. Добавить сервер

```bash
curl -X POST http://127.0.0.1:8000/api/servers \
  -H "Authorization: Bearer TEST" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "main-server",
    "host": "2.27.30.2",
    "user": "root",
    "port": 22,
    "identity_file": null,
    "manage_script_path": "/root/awg/manage_amneziawg.sh",
    "strict_host_key_checking": "accept-new"
  }'
```

Пример ответа:

```json
{
  "id": 1,
  "name": "main-server",
  "host": "2.27.30.2",
  "user": "root",
  "port": 22,
  "identity_file": null,
  "manage_script_path": "/root/awg/manage_amneziawg.sh",
  "strict_host_key_checking": "accept-new",
  "created_at": "2026-03-25 08:43:45",
  "is_reachable": true,
  "status": "online",
  "status_label": "Доступен"
}
```

### 2. Получить список серверов

```bash
curl -H "Authorization: Bearer TEST" \
  http://127.0.0.1:8000/api/servers
```

### 3. Создать клиента

```bash
curl -X POST http://127.0.0.1:8000/api/clients \
  -H "Authorization: Bearer TEST" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": 1,
    "client_name": "egor",
    "expires_until": "01.04.2026"
  }'
```

Пример ответа:

```json
{
  "succsess": true,
  "server_id": 1,
  "client_name": "egor",
  "files": {
    "conf_url": "http://127.0.0.1:8000/api/files/CONF_FILE_ID",
    "png_url": "http://127.0.0.1:8000/api/files/PNG_FILE_ID"
  }
}
```

### 4. Получить список клиентов

```bash
curl -H "Authorization: Bearer TEST" \
  http://127.0.0.1:8000/api/clients/1
```

Пример ответа:

```json
{
  "succsess": true,
  "server_id": 1,
  "count": 3,
  "clients": [
    {
      "name": "egor",
      "has_conf": true,
      "has_qr": true,
      "status": "no_handshake",
      "status_label": "Нет handshake",
      "expires_in": "6д 23ч"
    }
  ]
}
```

### 5. Продлить подписку клиента

Формат даты:

```text
ДД.ММ.ГГГГ
```

Успешный пример:

```bash
curl -X PATCH http://127.0.0.1:8000/api/clients/subscription \
  -H "Authorization: Bearer TEST" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": 1,
    "client_name": "egor",
    "prolong_until": "18.04.2026"
  }'
```

Пример ответа:

```json
{
  "succsess": true,
  "server_id": 1,
  "client_name": "egor",
  "prolong_until": "18.04.2026",
  "applied_duration": "416h",
  "expires_at": "2026-04-19 00:30:25"
}
```

Если новая дата меньше текущей подписки:

```bash
curl -X PATCH http://127.0.0.1:8000/api/clients/subscription \
  -H "Authorization: Bearer TEST" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": 1,
    "client_name": "egor",
    "prolong_until": "10.04.2026"
  }'
```

Пример ошибки:

```json
{
  "succsess": false,
  "error": "У клиента уже есть подписка до 2026-04-19 00:30:25. Новая дата должна быть больше текущей."
}
```

### 6. Удалить клиента

```bash
curl -X DELETE \
  -H "Authorization: Bearer TEST" \
  http://127.0.0.1:8000/api/clients/1/egor
```

Пример ответа:

```json
{
  "succsess": true,
  "server_id": 1,
  "client_name": "egor"
}
```

### 7. Скачать `.conf`

```bash
curl -L -H "Authorization: Bearer TEST" \
  "http://127.0.0.1:8000/api/files/CONF_FILE_ID" \
  -o egor.conf
```

### 8. Скачать `.png`

```bash
curl -L -H "Authorization: Bearer TEST" \
  "http://127.0.0.1:8000/api/files/PNG_FILE_ID" \
  -o egor.png
```

## Боевые примеры

Если API стоит за доменом, просто меняешь:

```text
http://127.0.0.1:8000
```

на:

```text
https://awg.twzrds.ru
```

Например:

```bash
curl -H "Authorization: Bearer 1" https://awg.twzrds.ru/api/servers
```

## Примечания

- домен указывается в `Caddyfile`, не в `.env`;
- серверы хранятся в `SQLite`;
- при удалении клиента API чистит локальные файлы и записи в БД;
- `succsess` оставлен в таком виде специально, чтобы не ломать текущий контракт API;
- в корне проекта лежит актуальный `manage_amneziawg.sh`, скачанный с VPN-сервера.
