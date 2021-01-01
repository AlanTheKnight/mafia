# Mafia Bot

Discord bot for playing Mafia party game.

## Installation/Установка

### :gb:

1. Download files of this repository on your computer/server
2. In the main folder create a file named ``settings.ini`` with the following content:

```
[MAIN]
TOKEN = <Your Discord bot Token>
GUILD = <Name of guild (server) where you want to play> 
ADMINROLES = <Names of roles who can manage bot administrator status separated with spaces>
```

3. In the same directory create empty files named ``users.json`` and ``roles.json``
4. Launch the bot using

```bash
python -m pip install discord.py
python main.py
```

### :ru:

1. Скачайте этот репозиторий к себе на компьютер/сервер
2. В основной папке создайте файл ``settings.ini`` со следующим содержимым:

```
[MAIN]
TOKEN = <Токен Discord бота>
GUILD = <Название Discord-сервера, где вы хотите играть> 
ADMINROLES = <Разделенные пробелами названия ролей на сервере, которые могут назначать ведущего>
```

3. В той же папке создайте пустые файлы ``users.json`` и ``roles.json``
4. Запустить бота при помощи команд

```bash
python -m pip install discord.py
python main.py
```
