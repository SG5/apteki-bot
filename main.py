from flask import Flask
import drug_bot as bot

app = Flask(__name__)
bot.send_webhook_url()


@app.route('/')
def hello():
    return 'Hello World'


@app.route('/' + bot.get_webhook_url(), methods=['POST'])
def webhook_handler():
    return bot.webhook_handler()


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
