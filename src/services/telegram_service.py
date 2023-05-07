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

    def start(self):
        log.info("Starting telegram bot...")
        self.__setup()
        log.info("Bot started to run")
        while self.running:
            self.handle_messages()
            time.sleep(self.refresh_rate)

    def __validate(self) -> bool:
        response = requests.get(self.url + "/getMe")
        content = json.loads(response.content)
        return content["ok"]

    def __validate_admin(self, message):
        username = message["chat"]["username"]
        return username in settings["project.admins"]

    def __setup(self):
        self.get_last_offset()
        self.configure_commands()

    def configure_commands(self):
        data = {
            "commands": [
                {"command": "help",
                "description": "Show help options"},
                {"command": "exit",
                "description": "End bot execution"}
            ]
        }
        requests.post(self.url + "/setMyCommands", data)

    def help(self, message: dict):
        user_name = message["chat"]["first_name"]
        chat_id = message["chat"]["id"]
        data = {
            "chat_id": chat_id,
            "text": f"Hello {user_name}, how can i help you today?\n"
            "Will be a pleasure to ignore your needs, as your parents."
        }
        requests.post(self.url + "/sendMessage", data)

    def get_last_offset(self):
        response = requests.get(self.url + "/getUpdates", {"limit": 1})
        content = json.loads(response.content)
        if content["result"]:
            last_update_id = content["result"][0]["update_id"]
            self.offset = last_update_id + 1

    def get_messages(self):
        response = requests.get(self.url + "/getUpdates", {"offset": self.offset})
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
        if option == "/exit" and self.__validate_admin(message):
            self.running = False
        elif option == "/help":
            self.help(message)


    def send_message(self, message: dict):
        user_name = message["chat"]["first_name"]
        chat_id = message["chat"]["id"]
        data = {
            "chat_id": chat_id,
            "text": f"Welcome to WolfGear Bot, {user_name}"
        }
        requests.post(self.url + "/sendMessage", data)
