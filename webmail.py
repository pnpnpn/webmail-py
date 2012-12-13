#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import smtplib
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from retry_decorator import *
import logging
import logging.handlers

#####################################################################
# SMTP handler
#####################################################################
def get_smtp_handler(email_subject):
    smtp_hdlr = SMTPHandlerPlus(fetch_email_cfg(), email_subject)
    smtp_hdlr.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        '%Y%m%d|%H:%M:%S'))
    smtp_hdlr.setLevel(logging.WARNING)
    return smtp_hdlr

class SMTPHandlerPlus(logging.handlers.SMTPHandler):
    def __init__(self, email_cfg, email_subject):
        self.email_cfg = email_cfg
        self.email_subject = email_subject
        super(SMTPHandlerPlus, self).__init__(
                mailhost=None, 
                fromaddr=None,
                toaddrs=None,
                subject=None)

    def getSubject(self, record):
        return '(%s) %s' % (record.levelname, self.email_subject)

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            subject = self.getSubject(record)
            body = self.format(record)
            send_smtp_email(self.email_cfg, subject, body)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


@retry(Exception, tries=10)
def send_smtp_email(email_cfg, subject, body):
    if email_cfg['server'] == 'zoho': 
        mail_func = send_zoho_mail
    elif email_cfg['server'] == 'gmail': 
        mail_func = send_gmail
    elif email_cfg['server'] == 'hotmail': 
        mail_func = send_hotmail
    else:
        raise Exception('invalid server %s found' % email_cfg['server'])

    mail_func(
            email_cfg['from'], 
            email_cfg['to'],
            email_cfg['user'], 
            email_cfg['password'], 
            subject, 
            body)
         
def send_hotmail(from_email, to_email, user, password, subject, body):
    text = create_email_MIME(
            from_email, 
            to_email, 
            subject,
            body)

    server = smtplib.SMTP('smtp.live.com:587', timeout=10)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user, password)
    server.sendmail(from_email, to_email, text)
    server.quit()

       
def send_zoho_mail(from_email, to_email, user, password, subject, body):
    text = create_email_MIME(
            from_email, 
            to_email, 
            subject,
            body)

    server = smtplib.SMTP_SSL('smtp.zoho.com:465', timeout=10)
    server.ehlo()
    server.login(user, password)
    server.sendmail(from_email, to_email, text)
    server.quit()

def send_gmail(from_email, to_email, user, password, subject, body):
    text = create_email_MIME(
            from_email, 
            to_email, 
            subject,
            body)

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user, password)
    server.sendmail(from_email, to_email, text)
    server.quit()

def create_email_MIME(from_email, to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Converting email to text
    text = msg.as_string()
    return text

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    subject = 'Testing email 你好吗 %s' % datetime.datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')
    body = u"test test test 粵語 "
    logging.info(body)

    email_cfg = fetch_email_cfg('png.forward')
    send_smtp_email(email_cfg, subject, body)


    #logger = logging.getLogger('logger test')
    #logger.addHandler(get_smtp_handler('logger-test-subject'))
    #logger.warn('body-of-logging')
    #logger.info('INFO body-of-logging')


