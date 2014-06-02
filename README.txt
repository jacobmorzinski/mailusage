This is a port of the perl "mailusage" command to Python.
http://python-packaging-user-guide.readthedocs.org/

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

