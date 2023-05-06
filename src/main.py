from services.telegram_service import TelegramService
from setup import Setup

Setup()
telegram = TelegramService()
telegram.start()
