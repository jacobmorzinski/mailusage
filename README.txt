This is a port of the perl "mailusage" command to Python.


========
Will produce inconsistent results if run against servers with
inconsistent behavior.  Note that Microsoft Exchange sometimes
returns "estimates" of message size instead of actual size.


More information about Microsft Exchange behavior is here:

http://lumbgaps.blogspot.com/2009/04/exchange-2007-imap-rfc822size-and.html

http://social.technet.microsoft.com/Forums/exchange/en-US/21adbe96-e21b-458a-8242-2c3894b9d7cf/imappopsettings-and-enableexactrfc822size-false

An Exchange administrator can enable exact size for everyone with:
Set-ImapSettings -EnableExactRFC822Size:$true
Or can enable exact size only for a specific user:
Set-CASMailbox "IMAP User" -ImapUseProtocolDefaults:$false -ImapEnableExactRFC822Size:$true

========
You can test in “editable” mode (like python setup.py develop)
 
virtualenv mailusage
cd mailusage
. bin/activate
pip install -e git+https://github.com/jacobmorzinski/mailusage.git#egg=mailusage
 
You can do full install (into a virtualenv):
 
virtualenv mailusage
git clone https://github.com/jacobmorzinski/mailusage.git
cd mailusage
. bin/activate
python setup.py install
 

Usage, explicitly specifying a server:

$ mailusage -h imap.exchange.mit.edu
Size in KB   #Messages  Mailbox
         0           0  Archive
        35         461  Calendar
         0         112  Contacts
     66311        2583  Deleted Items
…etc
