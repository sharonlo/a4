import imaplib, email, getpass
from email.utils import getaddresses

def strip_string(string):
    return string.replace('\t', ' ').replace('\r\n', ' ').replace('\n', ' ').encode('string_escape')

# Email settings
imap_server = 'imap.gmail.com'
imap_user = 'sharon_lo@brown.edu'
imap_password = getpass.getpass()

# Connection
conn = imaplib.IMAP4_SSL(imap_server)
(retcode, capabilities) = conn.login(imap_user, imap_password)

#conn.select("INBOX.Sent Items")
#conn.select("INBOX.Archive", readonly=True)   # Set readOnly to True so that emails aren't marked as read
#conn.select('eInternship', readonly=True)
conn.select('[Gmail]/All Mail', readonly = True)

# Search for email ids between dates specified
result, data = conn.uid('search', None, '(SINCE "01-SEP-2015")')
# result, data = conn.uid('search', None, '(SINCE "01-Jan-2013" BEFORE "01-Jan-2014")')
# result, data = conn.uid('search', None, '(BEFORE "01-Jan-2014")')
# result, data = conn.uid('search', None, '(TO "user@example.org" SINCE "01-Jan-2014")')
uids = data[0].split()

# Download headers
result, data = conn.uid('fetch', ','.join(uids), '(RFC822)')

# Where data will be stored
raw_file = open('raw-email-rec.tsv', 'w')

# Header for TSV file
raw_file.write("Message-ID\tDate\tSubj\tSenders\tReceivers\tCc\tMinReplyTo\n")

# Parse data and spit out info
for i in range(0, len(data)):
    print i
    
    # If the current item is _not_ an email header
    if len(data[i]) != 2:
        continue
    
    # Okay, it's an email header. Parse it.
    msg = email.message_from_string(data[i][1])
    mids = msg.get_all('message-id', None)
    for mid in mids:
        mid = strip_string(mid)
    mdates = msg.get_all('date', None)
    for mdate in mdates:
        mdate = strip_string(mdate)
    msubj = msg.get_all('subject', None)
    if msubj:
        for m in msubj:
            m = strip_string(m)
    minreplyto = msg.get_all('in-reply-to', [])
    for inreplyto in minreplyto:
        inreplyto = strip_string(inreplyto)
    senders = msg.get_all('from', [])
    for s in senders:
        s = strip_string(s)
    receivers = msg.get_all('to', [])
    for r in receivers:
        r = strip_string(r)
    ccs = msg.get_all('cc', [])
    for cc in ccs:
        cc = strip_string(cc)
    
    row = "\t" if not mids else mids[0] + "\t"
    row += "\t" if not mdates else mdates[0] + "\t"

    row += "\t" if not msubj else msubj[0] + "\t"
    
    # Only one person sends an email, but just in case
    for name, addr in getaddresses(senders):
        row += addr + " "
    row += "\t"
    
    # Space-delimited list of those the email was addressed to
    for name, addr in getaddresses(receivers):
        row += addr + " "
    row += "\t"
    
    # Space-delimited list of those who were CC'd
    for name, addr in getaddresses(ccs):
        row += addr + " "
    row += "\t"

    for name, addr in getaddresses(minreplyto):
        row += addr + " "
    row += "\t"
    
    row += "\n"

    
    # DEBUG    
    # print msg.keys()
    
    # Just going to output tab-delimited, raw data. Will process later.
    raw_file.write(row)

print "done writing"

# Done with file, so close it
raw_file.close()