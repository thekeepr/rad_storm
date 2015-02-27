import time

class BaseNAS(object):
    """
    This is the base class to act as a skleton
    for different types of NAS being simulated
    """
    nas_type = 'BaseNAS'

    def __init__(self, nas_identifier, nas_ip):
        """
        nas_identifier -- name or description for nas will be sent in
                          Nas-Identifier attribute
        nas_ip         -- ipv4 Address of nas
        """
        self.nas_identifier = str(nas_identifier)
        self.nas_ip = nas_ip

    def _set_radius_general(self, req, session):
        req['NAS-Identifier'] = self.nas_identifier
        req['NAS-IP-Address'] = self.nas_ip
        req['NAS-Port'] = session.nas_port
        req['NAS-Port-Id'] = session.nas_port_id
        req['Acct-Session-Id'] = session.session_id
        req['Framed-Protocol'] = 'PPP'
        req['Service-Type'] = 'Framed-User'
        req['NAS-Port-Type'] = 'Ethernet'
        req['Event-Timestamp'] = long(time.time())

    def _set_radius_acct(self, req, session):
        pass

    def get_authentication_req(self, session, aaa_server, rad_dict):
        pass

    def get_accounting_start_req(self, session, aaa_server, rad_dict):
        pass

    def get_accounting_update_req(self, session, aaa_server, rad_dict):
        pass

    def get_accounting_stop_req(self, session, aaa_server, rad_dict):
        pass
