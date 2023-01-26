# FOODGRAM - твой продуктовый помощник
[![Django-app workflow](https://github.com/zhannaven/FOODGRAM/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)](https://github.com/zhannaven/FOODGRAM/actions/workflows/yamdb_workflow.yml)
### Описание проекта
FOODGRAM - это онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Всю документацию по API можно найти здесь [/redoc]

### Технологии:
- Python 3.7
- Django 2.2.16
- DRF 3.12.4
- JWT
- PostreSQL
- Nginx
- gunicorn
- Docker
- DockerHub
- GitHub Actions (CI/CD)

### Пример наполнения файла .env
 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=postgres
 - POSTGRES_USER=postgres
 - POSTGRES_PASSWORD=postgres
 - DB_HOST=db
 - DB_PORT=5432
 - SECRET_KEY=<секретный ключ проекта Django>

### Запуск проекта (в Unix) 
- Склонировать репозиторий на локальную машину:
```bash
git clone git@github.com:ZhannaVen/FOODGRAM.git
```
- Выполнить вход на удаленный сервер:
- Установить docker на сервер:
```bash
sudo apt install docker.io 
```
- Установить docker-compose на сервер:
```bash
curl -SL https://github.com/docker/compose/releases/download/v2.14.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```
- Отредактировать файл nginx/default.conf, изменив IP адрес сервера
- Скопировать файлы docker-compose.yml и default.conf из проекта на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp default.conf <username>@<host>:/home/<username>/nginx.conf
```
- создать файл .env в соответствии с примером выше. Необходимо изменить значения POSTGRES_USER и POSTGRES_PASSWORD
- Для работы с Workflow добавьте переменные окружения в Secrets GitHub:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<postgres database name>
    DB_USER=<database user>
    DB_PASSWORD=<password>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<password from DockerHub>
    DOCKER_USERNAME=<username on DockerHub>
    
    SECRET_KEY=<Django project secret key>

    USER=<username to connect to the server>
    HOST=<IP of the server>
    PASSPHRASE=<password for the server, if set>
    SSH_KEY=<your SSH key (command: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID of the chat where the message will be sent>
    TELEGRAM_TOKEN=<тyour bot token>
    ```
    4 этапа Workflow:
     - Проверка кода в соответствии PEP8;
     - сборка образов backend/frontend и отправка на Docker Hub;
     - Автоматический деплой на удаленный сервис;
     - Отправка сообщения в telegram чат.

- Запустите docker-compose:
```bash
docker-compose up -d --build
```
- Далее необходимо настроить базу данных:
    * Провести миграции:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
    * Подгрузить статику:
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```  
    * Создать суперпользователя:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

### Наполнение базы данных
- Загрузить ингредиенты:
```bash
docker-compose exec backend python3 manage.py load_ingredients
```
- Загрузить теги:
```bash
docker-compose exec backend python3 manage.py load_tags
```

### Роли пользователей

- Аноним - может просматривать рецепты и страницы пользователей, фильтровать рецепты по тегам.
- Авторизованный пользователь (user) - модет создавать/редактировать/удалять собственные рецепты; просматривать рецепты на главной; просматривать страницы пользователей; просматривать отдельные страницы рецептов; фильтровать рецепты по тегам; работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов; работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок; подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.
- Django суперюзер - может изменять пароль любого пользователя, создавать/блокировать/удалять аккаунты пользователей, редактировать/удалять любые рецепты;  добавлять/удалять/редактировать ингредиенты; добавлять/удалять/редактировать теги.

## Автор

- [Zhanna - Python-разработчик](https://github.com/ZhannaVen)
- [Яндекс.Практикум] - Фронтенд для сервиса Foodgram
