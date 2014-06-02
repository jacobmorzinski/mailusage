#!/usr/bin/env python

# https://tools.ietf.org/html/rfc4752

import base64
import kerberos

AUTH_GSS_CONTINUE = kerberos.AUTH_GSS_CONTINUE # 0
AUTH_GSS_COMPLETE = kerberos.AUTH_GSS_COMPLETE # 1

# Bit-masks for SASL security layers
GSS_AUTH_P_NONE      = 1
GSS_AUTH_P_INTEGRITY = 2
GSS_AUTH_P_PRIVACY   = 4

STATE_ONE = 1                                  # initialize context
STATE_TWO = 2                                  # decide protection+username

class GSSAPI_SASL(object):
    '''Use it like this:
    
    host = 'imap.server.example.com'
    user = 'username'
    with gssapisasl.GSSAPI_SASL('imap@{}'.format(host), user) as gs:
        tag,data = m.authenticate('gssapi', gs.callback)

    '''
    
    service = ''
    username = ''
    context = None
    state = STATE_ONE

    def __init__(self, service, username):
        '''service is in the form service@host
        for example host@server.example.com
        username will be passed to the server'''
        self.service = service
        self.username = username

    def __enter__(self):
        '''Initialize the GSS context.'''
        rc,ctx = kerberos.authGSSClientInit(self.service)
        if (rc != AUTH_GSS_CONTINUE and rc != AUTH_GSS_COMPLETE):
            raise Exception("Bad GSSAPI return code: {}".format(rc))
        self.context = ctx
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        '''Clean up the GSS context.'''
        rc = kerberos.authGSSClientClean(self.context)
        if (rc != AUTH_GSS_CONTINUE and rc != AUTH_GSS_COMPLETE):
            raise Exception("Bad GSSAPI return code: {}".format(rc))
        self.context = None

    def callback(self,response):
        '''Callback for use with imaplib.authenticate(mech,callback)
        Will be repeatedly called with data from server,
        and its return data passed back to server.
        '''


        response = "".join(str(response).encode('base64').splitlines())
##        print "Entering callback with response={}".format(response)

        ctx = self.context
        if ctx is None:
            raise Exception("GSS context is None.")

        # GSSAPI SASL: two states
        # First negotiate GSS security context
        # Then negotiate security protection layer

        if (self.state == STATE_ONE): 
            # Negotiating security context
            rc = kerberos.authGSSClientStep(ctx, response)
            if (rc != AUTH_GSS_CONTINUE and rc != AUTH_GSS_COMPLETE):
                raise Exception("Bad GSSAPI return code: {}".format(rc))
            elif (rc == AUTH_GSS_COMPLETE):
                # -> State transition
                self.state = STATE_TWO 
            payload = kerberos.authGSSClientResponse(ctx)

        elif (self.state == STATE_TWO):
            # Negotiating protection layer
            rc = kerberos.authGSSClientUnwrap(ctx, response)
            if (rc != AUTH_GSS_CONTINUE and rc != AUTH_GSS_COMPLETE):
                raise Exception("Bad GSSAPI return code: {}".format(rc))
            data = kerberos.authGSSClientResponse(ctx)

            # At this point, the protocol says we should unwrap a
            # security mask from the leading bytes of the decoded
            # data.  However we can't, because the C code in
            # kerberosgss.c forces GSS_AUTH_P_NONE and also does
            # not allow setting conf_flag in the wrap.

            ### Stuff we should do, but can't ###
            # bytestring = base64.b64decode(data)
            # bytes = struct.unpack('4B', bytestring)
            # bufsiz = ((bytes[1] << 8) + bytes[2] << 8) + bytes[3]
            # security_mask = bytes[0]
            # for layer in 4,2,1:
            #     then choose a desired_security layer from security_mask
            # bytestring = struct.pack('4B', desired_security, *bytes[1:])
            # then wrap with conf_flag suitable for the desired_security
            ### End stuff ###

            # So instead of unwrapping a security mask, we just
            # assert that we use GSS_AUTH_P_NONE ('\x01')

            bytestring = base64.b64decode(data)
            newdata = '\x01' + bytestring[1:]
            newdata = str(newdata).encode('base64')
            rc = kerberos.authGSSClientWrap(ctx, newdata, self.username)
            if (rc != AUTH_GSS_CONTINUE and rc != AUTH_GSS_COMPLETE):
                raise Exception("Bad GSSAPI return code: {}".format(rc))
            payload = kerberos.authGSSClientResponse(ctx)

        else:
            raise Exception("Unexpected state: {}".format(self.state))

        if payload is None:
            payload = ''
##        print "Leaving callback with payload={}".format(payload)
        payload = str(payload).decode('base64')
        return payload

    

# If you were doing it by hand in a REPL, it might look like:
# 

# m = imaplib.IMAP4_SSL('imap.exchange.mit.edu')
# service = 'imap@imap.exchange.mit.edu'

# m.sslobj.send('x authenticate gssapi\r\n')
# ps = m.sslobj.recv() ; ps
# rc,vc = kerberos.authGSSClientInit(service)
# rc = kerberos.authGSSClientStep(vc,"")          # is it 1 or 0 ? it is 0
# pc = kerberos.authGSSClientResponse(vc) ; pc
# m.sslobj.send((pc or '') + '\r\n')
# ps = m.sslobj.recv() ; ps
# ps = ps[2:].strip()
# rc = kerberos.authGSSClientStep(vc,ps) ; rc     # is it 1 or 0 ? it is 1
# pc = kerberos.authGSSClientResponse(vc) ; pc
# m.sslobj.send((pc or '') + '\r\n')
# ps = m.sslobj.recv() ; ps
# ps = ps[2:].strip()
# rc = kerberos.authGSSClientUnwrap(vc,ps) ; rc
# pc = kerberos.authGSSClientResponse(vc) ; pc
### flags = base64.b64decode(pc)
# rc = kerberos.authGSSClientWrap(vc, pc, 'jmorzins') ; rc
# pc = kerberos.authGSSClientResponse(vc) ; pc
# m.sslobj.send((pc or '') + '\r\n')
# ps = m.sslobj.recv() ; ps

# rc = authGSSClientClean(vc)

# m.logout()
