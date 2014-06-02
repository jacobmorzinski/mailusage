#!/usr/bin/python

'''Show mail storage used by messages in IMAP folders.'''

import argparse
import getpass
import gssapisasl
import imaplib
import re
import socket
import sys

debug = False


# Parse a LIST (or LSUB) response for a mailbox name
# and its attributes and delimiter.
#
# The response contains three elements, of the form:
#
#     (<attribute> ...) <delimiter> "<name>"
#
# For example:
#
#     (\HasChildren) "." "INBOX"
# The delimiter is either a quoted single character, e.g. ".",
# or NIL.

def list_mailboxes(client, reference, mailbox, onlysubscribed):
    '''Given an imaplib client object,
    sends a LIST or LSUB command for the named reference and mailbox.

    LIST reference mailbox
    LSUB reference mailbox
    '''
    
    if onlysubscribed:
        list_cmd = client.lsub
    else:
        list_cmd = client.list

    tag,data = list_cmd(reference, mailbox)

    pattern = re.compile(
        r'''^\((?P<attributes>[^\)]*)\)\s+     # (\Attributes)
            (?:"(?P<delimiter>.)"|NIL)\s+      # "/" or "." or NIL
            (?P<mailbox>"(?:.+)"|(?:.+))       # "mailbox"
        ''',
        re.VERBOSE|re.IGNORECASE)
    results = {}
    for item in data:
        if item is None:
            break
        match = re.match(pattern,item)
        md = match.groupdict()
        mbox = re.sub(r'^"(.*)"$', r'\1', md['mailbox'])
        results[mbox] = { 'attributes': md['attributes'],
                          'delimiter' : md.get('delimiter') }
    return results


def get_usage(client, mailbox):
    '''Given an imaplib client object and mailbox name,
    sums and returns RFC822.SIZE data for all messages in the mailbox.'''

    usage = { 'totalsize': 0, 'msgcount': 0 }

    tag,data = client.select(mailbox, readonly=True)
    if re.match(r'OK', tag, re.IGNORECASE):
        msgcount = int(data[0])
        usage['msgcount'] = msgcount

        # 50 at a time... 1:50, 51:100, etc
        sizes = []
        n = 1
        while n <= msgcount:
            n_upper = min(n+49, msgcount)
            sizes.extend(get_sizes(client, n, n_upper))
            n = n+50

        totalsize = sum(sizes)
        usage['totalsize'] = totalsize

    return (usage['totalsize'],usage['msgcount'])



def get_sizes(client, low, high):
    '''Given an imaplib client object,
    fetches RFC822.SIZE data for messages low:high
    in the active folder.'''

    global debug

    sizes = []
    tag,data = client.fetch('{}:{}'.format(low,high),
                            '(UID RFC822.SIZE)')
    for item in data:
        if debug:
            print item
        if item is None:
            break
        match = re.match(
            r'\S+\s+\((?:(?:UID\s+(?P<uid>\d+)\s*)|(?:RFC822.SIZE\s+(?P<size>\d+)\s*))+\)\s*',
            item, re.IGNORECASE)
        sz = match.groupdict()['size']
        sizes.append(int(sz))

    return sizes
 

def main():

    global debug

    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--help', action='help', default=argparse.SUPPRESS,
                        help='show this help message and exit')
    parser.add_argument('-h',
                        dest='host', metavar='HOST',
                        help='query %(metavar)s instead of default post office server')
    parser.add_argument('-m',
                        dest='mailbox', metavar='MAILBOX',
                        help='query for %(metavar)s only (default is all)')
    parser.add_argument('-n', action='store_true',
                        dest='noheader',
                        help='suppress the header line')
    parser.add_argument('-r', action='store_true',
                        dest='recurse',
                        help='query recursively for all mailbox descendents')
    parser.add_argument('-s', action='store_true',
                        dest='onlysubscribed',
                        help='display only subscribed mailboxes')
    parser.add_argument('-d', action='store_true',
                        dest='debug',
                        help='turn on debugging')

    ns = parser.parse_args()

    username = getpass.getuser()
    debug = ns.debug
    hostname = None
    if ns.host:
        hostname = ns.host
    else:
        hostname = socket.gethostbyaddr('%s.mail.mit.edu' % username)[0]
        if not hostname:
            raise Exception('Cannot find Post Office server for %s' % username)
    mbox = ns.mailbox if ns.mailbox is not None else '*'
    noheader = ns.noheader
    recurse = ns.recurse
    onlysubscribed = ns.onlysubscribed
    
    client = imaplib.IMAP4_SSL(hostname)
    if debug:
        client.debug = 4

    with gssapisasl.GSSAPI_SASL('imap@{}'.format(hostname),username) as gs:
        tag,data = client.authenticate('gssapi', gs.callback)

    # get mailboxes of interest
    mailboxes = {}

    # First list the given mailbox.
    mailboxes.update( list_mailboxes(client, '', mbox, onlysubscribed) )
    
    # If recursing, also list all descendents of the mailbox,
    # unless the given name contains a trailing wildcard.
    if ( recurse and
         mailboxes.get(mbox) and
         mailboxes[mbox].get('delimiter') and
         not mbox.endswith("*")):
        glob = '{}{}*'.format(mbox, mailboxes[mbox]['delimiter'])
        mailboxes.update( list_mailboxes(client, '', glob, onlysubscribed) )
        

   # We now have all of the mailboxes of interest.  Get and display
   # the total size and number of messages for each one.
    if mailboxes:
        for box in sorted(mailboxes.keys()):
            if (mailboxes[box]['attributes']).lower().find(r'\noselect') >=0 :
                continue
            size,nmsgs = get_usage(client, box)
            if not noheader:
                print "Size in KB   #Messages  Mailbox"
                noheader = True
            print "{:10}  {:10}  {}".format((size+1023)/1024,nmsgs,box)

    


if __name__ == '__main__':
    sys.exit(main())

