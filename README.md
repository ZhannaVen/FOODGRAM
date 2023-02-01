# FOODGRAM - your product assistant
[![Django-app workflow](https://github.com/zhannaven/FOODGRAM/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)](https://github.com/zhannaven/FOODGRAM/actions/workflows/yamdb_workflow.yml)
### Description
FOODGRAM - is an online service and an API for it. Using this service, users can publish recipes, subscribe to publications of other users, add recipes they liked to the "Favorites", and before going to the store, download a list of needed products.

All API documentation can be found here [/redoc]

### Used frameworks and libraries:
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

### Template description of .env
 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=postgres
 - POSTGRES_USER=postgres
 - POSTGRES_PASSWORD=postgres
 - DB_HOST=db
 - DB_PORT=5432
 - SECRET_KEY=<Django project secret key>

### How to start a project (Unix) 
- Clone repository:
```bash
git clone git@github.com:ZhannaVen/FOODGRAM.git
```
- Log in to a remote server
- Install docker on the server:
```bash
sudo apt install docker.io 
```
- Install docker-compose on the server:
```bash
curl -SL https://github.com/docker/compose/releases/download/v2.14.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```
- Edit file locally nginx/default.conf, be sure to enter the server's IP address in the server_name line
- Copy the docker-compose.yml and default.conf from the infra directory to the server:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp default.conf <username>@<host>:/home/<username>/nginx.conf
```
- Create .env according to the template above. Be sure to change the POSTGRES_USER and POSTGRES_PASSWORD values
- To work with Workflow, add environment variables to Secrets GitHub:
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
    Four steps of Workflow:
     - Checking code for PEP8 compliance;
     - Building and delivering a docker image for the web container on Docker Hub;
     - Automatic deployment to a remote server;
     - Sending a notification to a telegram chat.

- build and run containers on the server:
```bash
docker-compose up -d --build
```
- After a successful build, perform the following steps (only for the first deployment):
    * Run migrations inside containers:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
    * Collect static:
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```  
    * Create a Django superuser, after prompting from the terminal, enter the username and password for the superuser:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

### Filling the database
- Fill the database with ingredients:
```bash
docker-compose exec backend python3 manage.py load_ingredients
```
- Fill the database with tegs:
```bash
docker-compose exec backend python3 manage.py load_tags
```

### User roles

- Anonymous - can view recipes and user pages, filter recipes by tags.
- Authenticated user (user) - can, like Anonymous, read everything, in addition, can publish/edit/delete own recipes; add recipes to Favorites and Shopping Cart; download ingredients for shopping; follow other users.
- Django Superuser - has administrator rights (admin).

## Author

- [Zhanna - Python-Developer](https://github.com/ZhannaVen)
- [Яндекс.Практикум](https://github.com/yandex-praktikum) - Фронтенд для сервиса Foodgram
