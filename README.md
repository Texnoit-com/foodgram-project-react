# Сайт сборник рецептов 222


## Описание проекта Foodgram
Приложение, на котором пользователи публикуют рецепты, подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис позволяет пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии:
- Python 3.9
- Django 3.2
- Django REST framework 3.12
- Nginx
- Docker
- Postgres


## Запуск с использованием CI/CD

Установить docker, docker-compose на сервере ВМ Yandex.Cloud:
```bash
ssh username@ip
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
Создайте папку infra:
```bash
mkdir infra
```
- Перенести файлы docker-compose.yml и default.conf на сервер.

```bash
scp docker-compose.yml username@server_ip:/home/<username>/
```
```bash
scp default.conf <username>@<server_ip>:/home/<username>/
```
- Создайте файл .env в дериктории infra:

```bash
touch .env
```
- Заполнить в настройках репозитория секреты .env

```python
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

Скопировать на сервер настройки docker-compose.yml, default.conf из папки infra.

## Запуск проекта через Docker
- В папке infra выполнить команду, что бы собрать контейнер:
```bash
sudo docker-compose up -d
```

Для доступа к контейнеру выполните следующие команды:

```bash
sudo docker-compose exec backend python manage.py makemigrations
```
```bash
sudo docker-compose exec backend python manage.py migrate --noinput
```
```bash
sudo docker-compose exec backend python manage.py createsuperuser
```
```bash
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить DB ингредиентами и тэгами:

```bash
sudo docker-compose exec backend python manage.py load_tags
```
```bash
sudo docker-compose exec backend python manage.py load_ingredients
```

## Запуск проекта в dev-режиме

- Установить и активировать виртуальное окружение

```bash
source /venv/bin/activated
```

- Установить зависимости из файла requirements.txt

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

- Выполнить миграции:

```bash
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```bash
python manage.py runserver
```

### Документация к API доступна после запуска
```url
http://127.0.0.1/redoc/
```

Автор: [Бекурин Максим](https://github.com/Texnoit-com)
