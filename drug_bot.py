from google.appengine.api import app_identity
from location import location_handler
from drug import drug_handler
from hashlib import sha256
from flask import request
from secret import get_bot_token as token
import telegram

bot = telegram.Bot(token=token())
WEB_HOOK_URL = sha256(token()).hexdigest()


def webhook_handler():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True))

    if not update.message:
        return 'ok'

    chat_id = update.message.chat.id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    if update.message.text:
        kwargs = drug_handler(update.message.text.encode('utf-8'))
        bot.sendMessage(chat_id=chat_id, **kwargs)
    elif update.message.location:
        kwargs = location_handler(update.message.location)
        bot.sendMessage(chat_id=chat_id, **kwargs)

    return 'ok'


def get_webhook_url():
    return WEB_HOOK_URL


def send_webhook_url():
    bot.setWebhook(app_identity.get_default_version_hostname() + "/" + WEB_HOOK_URL)
