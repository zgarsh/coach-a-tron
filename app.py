# -*- coding: utf-8 -*-
import os
import schedule
import logging
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# set env variables
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']
my_number = os.environ['MY_NUMBER']

# create twilio client object
client = Client(twilio_account_sid, twilio_auth_token)

app = Flask(__name__)


# see if i can delete this
# if __name__ != '__main__':
#     gunicorn_logger = logging.getLogger("‘gunicorn.error’")
#     app.logger.handlers = gunicorn_logger.handlers
#     app.logger.setLevel(gunicorn_logger.level)



@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():

    # log incoming message for debugging
    print('message from:', request.values['From'])
    message_body = request.form['Body']
    print('message:', message_body)


    responseText = "Responding beep boop"

    resp = MessagingResponse()
    resp.message(responseText)


    return str(resp)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')