# [Порядок запуска сервисов с помощью docker-compose](docker_service.md)

# Техническое задание

Предлагается выполнить проект «Асинхронное API». Этот сервис будет точкой входа для всех клиентов. В первой итерации в сервисе будут только анонимные пользователи. Функции авторизации и аутентификации запланированы в модуле «Auth».

# Перечень заданий на 4 спринт
0. [~~Создать репозитарий, дать в него доступы (Оценка 1)~~ Выполнено ikanashov](./tasks/00_create_repo.md)
1. [~~Создать базовую структуру приложения (Оценка 3)~~ Выполнено ikanashov](./tasks/01_create_basis.md)
2. [~~Настроить докерфайл и докеркомпоуз (Оценка 5)~~ Выполнено ikanashov](./tasks/02_docker.md)
3. [~~Создать модели для фильмов и связанных данных (Оценка 5)~~ Выполнено ikanashov](./tasks/03_models.md)
4. [~~Написать сервис для получения информации о фильмах (Оценка 13)~~ Выполнено ikanashov](./tasks/04_film_logic.md)
5_0. ~~Добавить контейнер с ETL пайпланом для выполнения заданий 5 и 6 (Оценка 3)~~ Выполнено ikanashov. 
5. [Доработать ETL для записи в ES данных жанров (Оценка 5)](./tasks/05_etl_genre.md)
6. [Доработать ETL для записи в ES данных персоналий (Оценка 5)](./tasks/06_etl_person.md)
7. [Написать сервисы для получения информации об персоналиях и жанрах (Оценка 13)](./tasks/07_genre_person_logic.md)
8. [Кеширование данных в Redis (Оценка 8)](./tasks/08_cache.md)

## Используемые технологии

- Код приложения пишется на **Python + FastAPI**.
- Приложение запускается под управлением сервера **ASGI**(uvicorn).
- Хранилище – **ElasticSearch**.
- За кеширование данных отвечает – **redis cluster**.
- Все компоненты системы запускаются через **docker**.

## Описание
В папке tasks ваша команда сможет найти задачи, которые необходимо выполнить в первом спринте второго модуля. Обратите внимание на задачи 00_create_repo и 01_create_basis – они являются блокирующими для командной работы, их необходимо выполнить как можно раньше.

Мы оценили задачи в story point'ах, значения которых брались из [последовательности Фибоначчи](https://ru.wikipedia.org/wiki/Числа_Фибоначчи) (1,2,3,5,8,…).
Вы можете разбить имеющиеся задачи на более маленькие – например, чтобы распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа story points в спринте.**
