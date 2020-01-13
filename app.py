# -*- coding: utf-8 -*-

import os
import schedule
import logging
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
    gunicorn_logger = logging.getLogger("‘gunicorn.error’")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)





# @app.route("/sms", methods=['GET', 'POST'])
# def send_sms():

#     body = "it's past eleven!"

#     to = my_number,
#     client.messages.create(
#         to,
#         from_=twilio_number,
#         body=body)


# schedule.every().day.at("19:30").do(send_sms)




@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    print('message from:', request.values['From'])

    message_body = request.form['Body']
    print('message:', message_body)

    # user = db.session.query(User).filter_by(phone = request.values['From']).one()

    # if user.id == 1:
    #     # user is me
    #     responseText = choose_action_host(request)
    #     print('response to Zach:', responseText)
    # else:
    #     # user is someone else
    #     responseText = choose_action_guest(request)
    #     print('response to someone else:', responseText)

    #     host_alert = "message from " + str(user.name) + ': ' + message_body + "\n\n"
    #     host_alert += "response: " + responseText
    #     message_host(host_alert)

    responseText = "Responding beep boop"

    resp = MessagingResponse()
    resp.message(responseText)


    return str(resp)









# def pulse_check():
#     print('I am alive!')
#     app.logger.debug("‘this is the DEBUG message’")
#     app.logger.info("‘this is an INFO message’")
#     app.logger.warning("‘this is a WARNING message’")
#     app.logger.error("‘this is an ERROR message’")
#     app.logger.critical("‘this is a CRITICAL message’")

# pulse_check()

# schedule.every().minute.do(pulse_check)

# print('Please print this')

# while True:
#     schedule.run_pending()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')