# WorkPresence_bot

## Назначение бота

Статистика отметившихся о присутствии на работе (или дома) посредством чата в Telegram.

## Команды

- `/start` - начало работы.
- `/menu` - вывод меню с кнопками основных команд.
- `/stats` - вывод статистики.
- `/came_to_work` - пришёл на работу.
- `/left_work` - ушёл домой.
- `/stayed_at_home` - остался дома.
- `/help` - вывод справки.

## Статистика

По команде `/stats` выводится сообщение со списком пользователей, находящихся на работе и оставшихся дома, с указанием времени обновления данных по каждому пользователю.
Например:

```code
At work:
Vlad came to work
2021-10-24 13:06:15+00:00
Vladimir came to work
2021-10-24 13:01:35+00:00
```

## Регистрация команд в @BotFather:

```raw
came - User came to work.
left - User left work.
stay - User stayed at home.
start - Start bot.
help - Display help message.
menu - Display main menu.
stats - Display stats of users.
poll - Create alarm poll.
```
