import json
import time

import requests
from loguru import logger as log
from stela import settings


class TelegramService:
    def __init__(self, language: str = settings["project.default_language"]) -> None:
        self.token = settings["TELEGRAM_TOKEN"]
        self.url = settings["telegram.url"] + self.token
        self.language = language
        self.offset = 0
        self.running = True
        self.refresh_rate = 1

        self.welcome = (
            "Hello {user_name} and welcome to our Telegram bot.\n\n"
            "We provides ETL (Extract, Transform, Load) services for Shopee data!\n"
            "We're thrilled that you've chosen to use our bot to help streamline your data processing needs.\n\n"
            "Use the command /help to check all the options avaible.\n"
            "Enjoy ;)"
        )

        self.help = (
            "Here are the commands that you can use with our bot:\n\n"
            "/start - Start the bot and receive a welcome message.\n"
            "/help - View a list of available commands and their descriptions.\n"
            "/register - Register to our exclusive service.\n"
            "/transform - Transform data to your desired format.\n"
            "/feedback - Send feedback to the bot developers.\n\n"
            "If you have any further questions or need assistance, please don't hesitate to reach out to us."
            "We're always here to help!"
        )

    def start(self):
        log.info("Starting telegram bot...")
        self.__setup()
        log.info("Bot started to run")
        while self.running:
            self.handle_messages()
            time.sleep(self.refresh_rate)

    def __validate_admin(self, message):
        username = message["chat"]["username"]
        return username in settings["project.admins"]

    def __setup(self):
        self.get_last_offset()
        self.configure_commands()

    def configure_commands(self):
        data = {
            "commands": [
                {"command": "start", "description": "Start the bot and receive a welcome message."},
                {"command": "help", "description": "View a list of available commands and their descriptions."},
                {"command": "register", "description": "Register to our exclusive service."},
                {"command": "transform", "description": "Transform data to your desired format."},
                {"command": "feedback", "description": "Send feedback to the bot developers."},
            ]
        }
        requests.post(self.url + "/setMyCommands", data, timeout=5)

    def send_message(self, message: dict, text: str):
        chat_id = message["chat"]["id"]
        data = {"chat_id": chat_id, "text": text}
        requests.post(self.url + "/sendMessage", data, timeout=5)

    def get_last_offset(self):
        response = requests.get(self.url + "/getUpdates", {"limit": 1}, timeout=5)
        content = json.loads(response.content)
        if content["result"]:
            last_update_id = content["result"][0]["update_id"]
            self.offset = last_update_id + 1

    def get_messages(self):
        response = requests.get(self.url + "/getUpdates", {"offset": self.offset}, timeout=5)
        content = json.loads(response.content)
        return content["result"]

    def handle_messages(self):
        for message in self.get_messages():
            log.debug(message)
            self.offset = message["update_id"]

            if not message["message"]["from"]["is_bot"] and message["message"]["entities"][0]["type"] == "bot_command":
                self.command_options(message["message"])

        self.offset += 1

    def command_options(self, message):
        option = message["text"].split()[0]
        if option == "/start":
            user_name = message["chat"]["first_name"]
            self.send_message(message, self.welcome.format(user_name))
        elif option == "/exit" and self.__validate_admin(message):
            self.running = False
        elif option == "/help":
            self.send_message(message, self.help)
