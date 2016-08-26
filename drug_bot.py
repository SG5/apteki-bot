from google.appengine.api import app_identity
from location import get_nearest_subway
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
        text = update.message.text.encode('utf-8')
        bot.sendMessage(chat_id=chat_id, text=text)
    elif update.message.location:
        nearest = get_nearest_subway((update.message.location.latitude, update.message.location.longitude))
        bot.sendMessage(chat_id=chat_id, text=nearest[2])

    return 'ok'


def get_webhook_url():
    return WEB_HOOK_URL


def send_webhook_url():
    bot.setWebhook(app_identity.get_default_version_hostname() + "/" + WEB_HOOK_URL)
