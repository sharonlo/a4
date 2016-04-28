#PART 1:
    #1) Parse raw email tsv, filter into mid_replied and mid_all
    #2) Create contact_total_count, meaning # of total email exchanges between contact
    #3) Output mid_replied and mid_all:
    #FINAL OUTPUT:
        #mid_all and mid_replied [TIME, RECEIVER LIST, INREPLYTO, Subj, numCC]
    
import csv
from email.utils import parsedate
from time import mktime
from datetime import datetime
from __future__ import division
import numpy
import pickle

contact_total_count = {} #format: K:receiver, V: #count

with open('raw-email-rec.tsv', 'rb') as tsv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    next(tsv_file)
    mid_replied = {}
    mid_all = {}
    for row in tsv_reader:
        print row
        if len(row) != 8 or not row[4]: #poorly formatted email or no receiver
            continue
        # index of all e-mails
        m_content = []
        mid = row[0].strip()
        mid = mid.replace('<','')
        mid = mid.replace('>','')
        m_date = row[1].strip()
        m_subj = row[2]
        m_senders = row[3]
        m_receivers = row[4]
        m_numcc = len(row[5].strip().split(","))

        #adjust total count of contacts (sender-side)
        sender_list = m_senders.strip().split(' ')
        for s in sender_list:
            s = s.strip()
            if s in contact_total_count:
                contact_total_count[s]+=1
            else:
                contact_total_count[s]=1
        
        #adjust total count of contacts (receiver_side)
        receiver_list = m_receivers.strip().split(' ')
        for r in receiver_list:
            r = r.strip()
            if r in contact_total_count:
                contact_total_count[r]+=1
            else:
                contact_total_count[r]=1
            
        in_reply_to = row[6].strip()
        time = datetime.fromtimestamp(mktime(parsedate(m_date)))
        m_content.append(time)
        m_content.append(receiver_list)
        if in_reply_to: #if string is not empty, actually part of a thread  
            m_content.append(in_reply_to)
        else:
            m_content.append('None')
        m_content.append(m_subj)
        m_content.append(m_numcc)

        print m_content
        print "====="
        
        if len(m_content) == 6:
             mid_all[mid] = m_content
        
        # I responded
        if row[3].strip() == 'sharon_lo@brown.edu':
            mid_replied[mid] = m_content

#PART 2:
    #1) Create contact_reply_times = list of response times for each contact
    #2) Create contact_reply_count = total count of emails initiated or replied to this contact
    #3) contact_avg_response = avg response time for each contact
    #4) contact_ratio = #reply/#total
    #5) write both dictionaries to file for MailBot to parse


contact_reply_times = {} #format receiver: time, time, time,...
contact_reply_count = {} #format receiver: #count

for mid_key in mid_replied:
    mid_meta= mid_replied[mid_key]
    m_date_1 = mid_meta[0]
    m_receiver_list = mid_meta[1]
    m_inreplyto = mid_meta[2]
    if m_inreplyto == 'None':
        for r in m_receiver_list:
            if r in contact_reply_count:
                contact_reply_count[r]+=1
            else:
                contact_reply_count[r]=1
    else: #should be in reply to something, look up in all_messages hashmap
        in_reply_mid = mid_meta[2]
        if in_reply_mid in mid_all:
            m_date_2 = mid_all[in_reply_mid][0]
            diff = (m_date_1 - m_date_2).total_seconds()
        else:
            diff = 172800.0 #default value of 2 days
        for r in m_receiver_list:
            if r in contact_reply_count:
                contact_reply_count[r]+=1
            else:
                contact_reply_count[r]=1
            if r in contact_reply_times:
                reply_time_list = contact_reply_times[r]
                reply_time_list.append(diff)
                contact_reply_times[r] = reply_time_list
            else:
                reply_time_list = []
                reply_time_list.append(diff)
                contact_reply_times[r] = reply_time_list

#make receiver avg map
contact_avg_response = {}
for r in contact_reply_times.keys():
    time_list = numpy.array(contact_reply_times[r])
    contact_reply_times[r] = numpy.mean(time_list)

#write avg_response to file:
output = open('contact_avg_response.txt', 'ab+')
pickle.dump(contact_avg_response, output)
output.close()
    
contact_ratio = {}
for r in contact_reply_times.keys():
    reply_count = 0
    if r in contact_reply_count:
        reply_count = contact_reply_count[r] 
    contact_ratio[r] = reply_count/contact_total_count[r]

#write ratio to file:
output = open('contact_ratio.txt', 'ab+')
pickle.dump(contact_ratio, output)
output.close()