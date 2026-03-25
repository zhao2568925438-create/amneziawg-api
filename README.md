# AmneziaWG API

Лёгкий API для управления клиентами `AmneziaWG` через `SSH`.

Что умеет:

- создавать клиента;
- удалять клиента;
- получать список клиентов;
- хранить несколько серверов в `SQLite`;
- защищать API через `Bearer`-токен;
- отдавать ссылки на скачивание `.conf` и `.png`.

## Стек

- `FastAPI`
- `SQLite`
- существующий `SSH`-раннер поверх `manage_amneziawg.sh`

## Быстрый старт

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Создать `.env` на основе примера:

```bash
cp .env.example .env
```

3. Заполнить главное:

- `API_TOKEN`
- при желании `API_HOST`
- при желании `API_PORT`

4. Запустить API:

```bash
uvicorn app:app --reload
```

## Что лежит в `.env`

Туда вынесено только важное:

- `API_HOST`
- `API_PORT`
- `API_TOKEN`
- `DATABASE_PATH`
- `STORAGE_DIR`

Параметры SSH-серверов лежат в базе, а не в `.env`.

## Авторизация

Во все запросы нужно передавать заголовок:

```text
Authorization: Bearer <API_TOKEN>
```

## Эндпоинты

### 1. Добавить сервер

`POST /api/servers`

Пример тела:

```json
{
  "name": "main-server",
  "host": "2.27.30.2",
  "user": "root",
  "port": 22,
  "identity_file": null,
  "manage_script_path": "/root/awg/manage_amneziawg.sh",
  "strict_host_key_checking": "accept-new"
}
```

### 2. Получить список серверов

`GET /api/servers`

### 3. Получить список клиентов сервера

`GET /api/clients/{server_id}`

### 4. Создать клиента

`POST /api/clients`

Пример тела:

```json
{
  "server_id": 1,
  "client_name": "my_phone",
  "expires": "7d"
}
```

API в ответе вернёт:

- результат выполнения команды;
- ссылку на скачивание `.conf`;
- ссылку на скачивание `.png`.

### 5. Удалить клиента

`DELETE /api/clients/{server_id}/{client_name}`

### 6. Скачать файл

`GET /api/files/{artifact_id}`

## Пример сценария

1. Добавить сервер.
2. Вызвать создание клиента.
3. Забрать из ответа `conf_url` и `png_url`.
4. Скачать оба файла обычным HTTP-запросом.

## Примечания

- API хранит файлы локально в `STORAGE_DIR`.
- База создаётся автоматически.
- Для теста сейчас используется простой `Bearer`-токен без пользователей и ролей.
