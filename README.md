### Установка

1. Скачать и установить [Python 3.10](https://www.python.org/downloads/)
2. Скачать и установить [Poetry](https://python-poetry.org/docs/#installation) (`pip install poetry`)

---

### Запуск

1. Выполнить команду `pip install poetry`
2. В терминале перейти в папку с ботом и установить зависимости командой `poetry install`
3. Запустить бота командой `poetry run python -m bot`
4. Установить программу на менеджер процессов по типу Supervisor `sudo apt install supervisor`

---

### Работа с локализацией текста

##### Добавление перевода

1. Поиск текста в проекте и сохранение в файл `pybabel extract . -o bot/locales/messages.pot -k TextFilter`
2. Добавление нового языка "en" `pybabel init -i bot/locales/messages.pot -d locales -D messages -l en`
3. Скомпелировать переводы `pybabel compile -d bot/locales -D messages`

##### Обновление перевода

1. Обновление текстов в файле `pybabel extract . -o bot/locales/messages.pot -k TextFilter`
2. Обновление текста в языковых файлов `pybabel update -d bot/locales -D messages -i bot/locales/messages.pot`
3. Скомпелировать переводы `pybabel compile -d bot/locales -D messages`

---

### Функционал бота

#### Фильтры

* Роутер админа
* Локализатор i18n для message хендлеров

#### **Мидлвари**

* Добавление пользователя в бд и получение его объекта
* Устанока chat action по флагу в хенлерах
* Проверка на бан пользователя
* Удаления маркапа у предыдущего сообщения при наличии флага (необходимо во внутреней логике)
* Установка локализатора
* Метрика на созданные ссылки
* Реферальная система
* Установка сервисов
* База данных Tortoise-orm
* Apscheduler
* Антиспам (если за 1 секунду больше 3х message/call)
* Уведомление пользователя, если команда не найдена (если апдейт не обработан каким-то хендлером)

#### **Админка**

* Работа с пользователями
  * Информация о них
    * ID
    * Username
    * Сколько рефералов
    * С какой метрики
    * Реферер
    * Забанил ли бота
    * Дата регистрации
    * Количество доступных проверок
  * Добавить/удалить статус админа
  * Забанить/разбанить
  * Удалить с базы
* Рассылка
  * Всем пользователям
  * Одному
* Статистика
  * Всего пользователей
  * Заблокировавших бота
  * Забаненых
  * Статистика по метрике
  * Добавление/удаление ссылки для метрики
  * Топ 5 пользователей по кол-ву рефералов
  * Excel таблица пользователей

---
