## Курсовой проект VKinder
### Задание:
Используя данные из VK, нужно сделать сервис похожий на Tinder, а именно: чат-бота "VKinder". Бот должен искать людей, подходящих под условия, на основании информации о пользователе из VK:
- возраст;
- пол;
- город;
- семейное положение.

У тех людей, которые подошли по требованиям пользователю, получать топ-3 популярных фотографии профиля и отправлять их пользователю в чат вместе со ссылкой на найденного человека.
Популярность определяется по количеству лайков и комментариев.
### Входные данные
1. Имя пользователя или его id в ВК, для которого мы ищем пару.
2. Если информации недостаточно (например она скрыта или не заполнена), нужно дополнительно спросить её у пользователя.
### Требование к сервису:
1. Код программы удовлетворяет PEP8;
2. Получать токен от пользователя с нужными правами;
3. Программа декомпозирована на функции/классы/модули/пакеты;
4. Результат программы записывать в БД;
5. Люди не должны повторяться при повторном поиске;
6. Не запрещается использовать внешние библиотеки для vk.
### Вермя на выполнение работы:
- плановое 336 ч;
- затраченное 189 ч.
### Рекомендации по запуску:
1. Создать группу в VK;
2. Зайти в Управление -> Работа с API, создать ключ;
3. Включить возможность писать сообщения в группу. Управление -> Сообщения -> Сообщения сообщества: включить;
4. Настройки бота. Возможности бота: Включены;
5. Полученное значение ключа занести в переменную token_group;
6. Ключ для переменной token_user получить на сайте https://vk.com/dev;
7. Запустить скрипт main.py.