# AmneziaWG API

Лёгкий API для управления `AmneziaWG` через `SSH`.

Что умеет:

- добавлять серверы;
- показывать список серверов и их доступность;
- создавать клиентов;
- удалять клиентов;
- показывать список клиентов;
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
API_TOKEN=1
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

## Боевые примеры

Ниже примеры для домена:

```text
https://awg.twzrds.ru
```

### 1. Добавить сервер

```bash
curl -X POST https://awg.twzrds.ru/api/servers \
  -H "Authorization: Bearer 1" \
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

### 2. Создать клиента

```bash
curl -X POST https://awg.twzrds.ru/api/clients \
  -H "Authorization: Bearer 1" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": 1,
    "client_name": "artem",
    "expires": "7d"
  }'
```

Пример ответа:

```json
{
  "succsess": true,
  "server_id": 1,
  "client_name": "artem",
  "files": {
    "conf_url": "http://awg.twzrds.ru/api/files/d7476d08dda246f19f857df0ac612135",
    "png_url": "http://awg.twzrds.ru/api/files/74f93f8b78ed48378db1933ae4a8daf0"
  }
}
```

### 3. Получить список серверов

```bash
curl -H "Authorization: Bearer 1" \
  https://awg.twzrds.ru/api/servers
```

Пример ответа:

```json
[
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
]
```

### 4. Получить список клиентов

```bash
curl -H "Authorization: Bearer 1" \
  https://awg.twzrds.ru/api/clients/1
```

Пример ответа:

```json
{
  "succsess": true,
  "server_id": 1,
  "count": 3,
  "clients": [
    {
      "name": "artem",
      "has_conf": true,
      "has_qr": true,
      "status": "no_handshake",
      "status_label": "Нет handshake",
      "expires_in": "6д 23ч"
    },
    {
      "name": "my_laptop",
      "has_conf": true,
      "has_qr": true,
      "status": "no_handshake",
      "status_label": "Нет handshake",
      "expires_in": null
    },
    {
      "name": "my_phone",
      "has_conf": true,
      "has_qr": true,
      "status": "no_handshake",
      "status_label": "Нет handshake",
      "expires_in": null
    }
  ]
}
```

### 5. Удалить клиента

```bash
curl -X DELETE \
  -H "Authorization: Bearer 1" \
  https://awg.twzrds.ru/api/clients/1/artem
```

Пример ответа:

```json
{
  "succsess": true,
  "server_id": 1,
  "client_name": "artem"
}
```

### 6. Скачать `.conf`

```bash
curl -L -H "Authorization: Bearer 1" \
  "https://awg.twzrds.ru/api/files/d7476d08dda246f19f857df0ac612135" \
  -o artem.conf
```

### 7. Скачать `.png`

```bash
curl -L -H "Authorization: Bearer 1" \
  "https://awg.twzrds.ru/api/files/74f93f8b78ed48378db1933ae4a8daf0" \
  -o artem.png
```

## Примечания

- домен указывается в `Caddyfile`, не в `.env`;
- серверы хранятся в `SQLite`;
- при удалении клиента API чистит локальные файлы и записи в БД;
- `succsess` оставлен в таком виде специально, чтобы не ломать текущий контракт API.
