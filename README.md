# Quest Bot

В проекте представлен бот-квест, который предоставляет пользователям интерактивные задания и квесты через Telegram. 
Бот разработан на Python с использованием библиотеки Aiogram для взаимодействия с Telegram API. 
Пользователи могут проходить различные квесты, решать задачи и получать награды.

---

## Установка:

- На Windows вы можете использовать `python`.
- На Linux рекомендуется использовать `python3`.
- Telegram аккаунт для создания бота


1. Клонируйте репозиторий:
```
git clone git@github.com:zerin2/api_yamdb.git
```
2. Cоздайте и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/scripts/activate
```
3. Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
4. Настройка переменных окружения:
Создайте файл .env в корневой директории проекта и добавьте в него следующие параметры:
```
TOKEN=<ваш_токен_бота>
DB_URL=<ваша_строка_подключения_к_базе_данных>
```
TOKEN — токен вашего Telegram бота, полученный у BotFather.
DB_URL — строка подключения к вашей базе данных (например, PostgreSQL).

5. Применение миграций базы данных:
```
alembic upgrade head
```
6. Запуск бота из папки src:
```
cd src
python app.py
```

---

## Примеры использования:

1. Начало работы с ботом
2. Откройте Telegram и найдите бота по имени @YourQuestBot.
3. Нажмите кнопку Start или отправьте команду /start для начала работы.
4. Бот приветствует вас и предлагает начать первый квест.

---

## Доступные команды:
/start — начать взаимодействие с ботом.
/help — получить список доступных команд и помощь.

---

## Зависимости
Проект использует следующие основные библиотеки:

aiogram==3.13.1 — фреймворк для создания Telegram-ботов.
asyncpg==0.29.0 — асинхронный клиент для PostgreSQL.
SQLAlchemy==2.0.34 — ORM для работы с базами данных.
Alembic==1.13.2 — инструмент для управления миграциями базы данных.
loguru==0.7.2 — библиотека для удобного логирования.
python-dotenv==1.0.1 — для загрузки переменных окружения из файла .env.

Полный список зависимостей находится в файле requirements.txt.

---

