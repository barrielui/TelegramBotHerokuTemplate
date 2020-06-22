# TelegramBotHerokuTemplate
[![Build Status](https://travis-ci.com/barrielui/TelegramBotHerokuTemplate.svg?branch=master)](https://travis-ci.com/barrielui/TelegramBotHerokuTemplate) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/barrielui/TelegramBotHerokuTemplate/blob/master/LICENSE)


### Please comply with RSS usage terms and conditions

Rebuilt upon NZ-Newsfeed-Telegram with simplified architecture.

Improved compatibility with cloud container host. The project can be seamlessly hosted on Heroku.

## Set-up with Telegram

1. Create a bot with [BotFather](https://t.me/BotFather). [doc](https://botsfortelegram.com/project/the-bot-father/)
2. Save the token. Keep it secret.
3. If you are sending message to a channel, add the bot to the channel and give it permission to send messages. If you are sending message to individual users, obtain the chatID on `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
Further detail: [https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id]

## Running on local machine

1. Install required python packages
Python 3.X
```sh 
pip install feedparser
pip install python-telegram-bot
```
2. Clone the script.
3. Replace your chatID and Token. For channels, the chatid is `@<YourChannelID>` (remember @). It is recommended to be saved as environmental variables
4. Add the feeds you want to follow
4. Save and run

## Running on Heroku

1. Clone the script. Add the feeds you want to follow.
2. Create new app on Heroku. Select deployment method as `Connect to GitHub`.
3. Select the repo. Make sure the repo contains `requirements.txt` and `Procfile`. They will instruct Heroku to install the required packages and the execution command.
4. Go to `Settings tab > Config Vars`. Put the `tg_bot_token` and the `tg_push_channel` there.
5. Go to `Overview tab > Configure Dynos`. Change the task to run.

Remarks: It is recommended to stop the Dyno before any git push.
