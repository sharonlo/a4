from __future__ import division
from mailbot import Callback, MailBot, register
import getpass
import imaplib
import time
import email
import re
import ast
import csv
from email.utils import parsedate
from time import mktime
from datetime import datetime
import cPickle

class MyCallback(Callback):
	#rules = {'subject': [r'Hello']}

	def trigger(self):

		#Keys#
		# ['Delivered-To', 'Received', 'X-Received', 'Return-Path', 'Received', 'Received-SPF', 
		# 'Authentication-Results', 'Received', 'DKIM-Signature', 'X-Google-DKIM-Signature', 
		# 'X-Gm-Message-State', 'X-Received', 'Return-Path', 'Received', 'From', 'Content-Type', 
		# 'Content-Transfer-Encoding', 'Mime-Version', 'Subject', 'Message-Id', 'Date', 'To', 'X-Mailer']


		#features: 
	    #0: contact ratio
	    #1: avg response time
	    #2: day of week recesived
	    #3: day of week sent, 
	    #4: time of day
	    #5: boolean: certain words in email address
	    #6: how many people cc'd

		m_sender = self.message['From']
		p = re.compile('\<.*>')
		m_sender = p.findall(m_sender)
		m_sender = m_sender[0]
		m_sender = m_sender.replace('<','')
		m_sender = m_sender.replace('>','')
		m_numcc = len(self.message['To'].split(','))

		print '*' + m_sender + '*'

		contact_avg_response = {}
		contact_ratio = {}
	
		with open('avg_response.csv', 'rb') as avg_f:
		    avg_reader = csv.reader(avg_f)
		    contact_avg_response = dict(avg_reader)

		with open('contact_ratio.csv', 'rb') as ratio_f:
		    ratio_reader = csv.reader(ratio_f)
		    contact_ratio = dict(ratio_reader)

		m_avg_response = 0.0
		if m_sender in contact_avg_response.keys():
			m_avg_response = float(contact_avg_response[m_sender])

		m_ratio = 0.0
		if m_sender in contact_ratio.keys():
			m_ratio = float(contact_ratio[m_sender])

		m_date = self.message['Date']
		m_time = datetime.fromtimestamp(mktime(parsedate(m_date)))
		m_day_received = m_time.weekday()

		m_now = datetime.now()
		m_day_now = m_now.weekday()
		m_hour_now = m_now.hour

		if m_hour_now >=0 and m_hour_now < 6:
			m_tofday = 3
		elif m_hour_now >=6 and m_hour_now < 12:
			m_tofday = 0
		elif m_hour_now >=12 and m_hour_now < 18:
			m_tofday = 1
		else:
			m_tofday = 2


		address_set = ['brown', 'google', 'microsoft', 'pinterest', 'qualtrics', 'square', 'uber', 'airbnb', 'fb', 'twitter']
		m_address = 0
		for a in address_set:
			if a in m_sender:
				m_address = 1

		#set numbers
		aggregate_avg_response = 217674.249233
		aggregate_contact_ratio = 0.359973620336

		features = [0.2*m_ratio + 0.8*aggregate_contact_ratio, 0.4*m_avg_response + 0.6*aggregate_avg_response, m_day_received, m_day_now, m_tofday, m_address, m_numcc]

		imap_server = 'imap.gmail.com'
		imap_user = 'sharon_lo@brown.edu'
		imap_password = getpass.getpass()

		conn = imaplib.IMAP4_SSL(imap_server, port=993)
		conn.login(imap_user, imap_password)
		conn.select('[Gmail]/Drafts')

		with open('my_lin_classifier.pkl', 'rb') as fid:
			clf = cPickle.load(fid)
		prediction = clf.predict(features)
		final_prediction = prediction/3600

		body = "Hi lovely person! a.k.a "
		body += m_sender.split("@")[0]
		body += "\n \n"#body of the email
		body += "This is an email prediction on when Sharon will reply to you. Cool right? \n"
		body += "Based on your past history, Sharon has a reply ratio of "
		body += str(round(m_ratio,2))
		body += " meaning num of replied emails/num of email transactions. Don't take offense if this is low! She still likes you a lot as a person. \n \n" 
		body += "Also, her average response rate to you is "
		body += str(round(m_avg_response/3600,2))
		body += " hours. Also don't take offense of this number is high! She's generally a slow responder with an overall average response rate of "
		body += str(round(aggregate_avg_response/3600,2))
		body += " hours.\n \n"
		body += "Finally, what you've been waiting for. Given these factors as well as other contextual cues, she'll probably respond to you in "
		body += str(round(final_prediction[0],2))
		body += " hours. \n \n"
		body += "Have a good day :)"
		new_message = email.message_from_string(body)

		new_message['Subject'] = 'Automated: Reply Prediction (we are getting futuristic)'
		new_message['From'] = 'sharon_lo@brown.edu'
		new_message['To'] = m_sender

		try:
		    conn.append("[Gmail]/Drafts",'', imaplib.Time2Internaldate(time.time()), str(new_message))
		        
		finally:
		    try:
		        conn.close()
		    except:
		        pass
		    conn.logout()

def main():
    # register your callback
	register(MyCallback)

	imap_server = 'imap.gmail.com'
	imap_user = 'sharon_lo@brown.edu'
	imap_password = getpass.getpass()

	mailbot = MailBot(imap_server, imap_user, imap_password, port=993, ssl=True)

	#conn = imaplib.IMAP4_SSL(imap_server)
	# (retcode, capabilities) = conn.login(imap_user, imap_password)

	# check the unprocessed messages and trigger the callback
	mailbot.process_messages()

if __name__ == '__main__':
    main()
