import sys
import smtplib

sender = 'simonwgill@gmail.com'
receivers = ['simonwgill@gmail.com']

message = """From: Simon Gill <simonwgill@gmail.com>
To: Simon Gill <simonwgill@gmail.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

try:
   smtpObj = smtplib.SMTP('localhost')
   smtpObj.sendmail(sender, receivers, message)         
   print "Successfully sent email"
except smtplib.SMTPException:
   print "Error: unable to send email", sys.exc_info()
