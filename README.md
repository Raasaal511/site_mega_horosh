# FastAPI Demo + деплой

Минимальный проект: FastAPI (REST API) + статический фронт (vanilla JS, без сборки).

```
project_delpoy/
├── app/
│   ├── main.py            # приложение и API
│   └── static/            # фронт: index.html, style.css, app.js
├── deploy/
│   ├── myapp.service      # unit для systemd
│   └── myapp.nginx.conf   # конфиг nginx
└── requirements.txt
```

API: `GET /api/health`, `GET /api/tasks`, `POST /api/tasks`,
`POST /api/tasks/{id}/toggle`, `DELETE /api/tasks/{id}`.
Документация — `/docs`.

> Задачи хранятся в памяти процесса: после перезапуска список пустой, и при
> `--workers > 1` у каждого воркера свой список. Для реального использования
> подключите БД (SQLite/Postgres).

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Открыть http://127.0.0.1:8000

---

# Деплой на сервер (Ubuntu/Debian)

## 1. Подготовка

```bash
sudo apt update
sudo apt install -y python3-venv nginx
```

## 2. Код и окружение

```bash
sudo mkdir -p /var/www/myapp
# загрузите код, например:
#   git clone <repo> /var/www/myapp
#   или с локальной машины:
#   rsync -av --exclude '.venv' ./ user@server:/var/www/myapp/

cd /var/www/myapp
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt

sudo chown -R www-data:www-data /var/www/myapp
```

Проверка, что приложение поднимается:

```bash
sudo -u www-data /var/www/myapp/.venv/bin/uvicorn app.main:app --port 8000
# в другом терминале: curl localhost:8000/api/health
```

## 3. systemd

```bash
sudo cp deploy/myapp.service /etc/systemd/system/myapp.service
sudo systemctl daemon-reload
sudo systemctl enable --now myapp
sudo systemctl status myapp
```

Полезные команды:

```bash
sudo systemctl restart myapp     # после обновления кода
sudo systemctl stop myapp
sudo journalctl -u myapp -f      # логи в реальном времени
sudo journalctl -u myapp -n 100  # последние 100 строк
```

Если правите сам unit-файл — обязательно `sudo systemctl daemon-reload`
перед `restart`.

## 4. nginx

```bash
sudo cp deploy/myapp.nginx.conf /etc/nginx/sites-available/myapp
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/myapp
sudo rm -f /etc/nginx/sites-enabled/default   # если дефолтный сайт не нужен

# замените server_name на свой домен или IP
sudo nano /etc/nginx/sites-available/myapp

sudo nginx -t          # проверка синтаксиса
sudo systemctl reload nginx
```

## 5. Файрвол

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

Порт 8000 наружу открывать не нужно: uvicorn слушает только `127.0.0.1`,
снаружи доступен лишь nginx.

## 6. HTTPS (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

Certbot сам правит конфиг nginx (добавляет 443 и редирект с 80) и настраивает
автопродление. Проверить: `sudo certbot renew --dry-run`.

## Обновление версии

```bash
cd /var/www/myapp
sudo -u www-data git pull
sudo .venv/bin/pip install -r requirements.txt
sudo systemctl restart myapp
```

## Если что-то не работает

| Симптом | Что смотреть |
|---|---|
| 502 Bad Gateway | `systemctl status myapp`, `journalctl -u myapp -n 50` — приложение упало или слушает не тот порт |
| 403/404 на `/static/` | права на `/var/www/myapp`, завершающий слэш в `alias` |
| Изменения не видны | `systemctl restart myapp`; для статики — кэш браузера (Ctrl+Shift+R) |
| nginx не стартует | `nginx -t`, `journalctl -u nginx -n 50` |
