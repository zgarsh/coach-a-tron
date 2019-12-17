
# -*- coding: utf-8 -*-

import os
import schedule
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']
my_number = os.environ['MY_NUMBER']

client = Client(twilio_account_sid, twilio_auth_token)

app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger(‘gunicorn.error’)
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def send_sms():

    body = "it's past eleven!"

    to = my_number,
    client.messages.create(
        to,
        from_=twilio_number,
        body=body)


# schedule.every().day.at("19:30").do(send_sms)


def pulse_check():
    print('I am alive!')
    app.logger.debug(‘this is a DEBUG message’)
    app.logger.info(‘this is an INFO message’)
    app.logger.warning(‘this is a WARNING message’)
    app.logger.error(‘this is an ERROR message’)
    app.logger.critical(‘this is a CRITICAL message’)

schedule.every().minute.do(pulse_check)

print('Please print this')

while True:
    schedule.run_pending()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')