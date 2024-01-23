This project is for learning purpose.
Main goal is to build a telegram bot that helps support in keeping their question \ answer organized and anonymous.

Instructions for launching on your own host. -
1. Create a telegram bot and get a unique token, more details on how to do this here - https://core.telegram.org/bots/tutorial
2. place the token in the .env file without quotes and spaces
3. open the terminal in the main derictory that contain py_telegram_bot.py file.
4. run this comand - "poetry run python py_telegram_bot.py"
5. define groups, for this run 2 commands in the bot’s personal messages - /set_support_group_id (id of the support group)
/set_client_group_id (id of the client group).
6. Add the bot to these groups the same way you would add a regular user.
7. Restart the bot by pressing the combination "ctrl+C" in the terminal and typing "poetry run python py_telegram_bot.py"