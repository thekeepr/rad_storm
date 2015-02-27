from base import BaseNAS
from lib.pyrad import packet

class MikrotikPPPoE(BaseNAS):
    '''
    Simulate a Mikrotik Device as PPPoE terminator
    '''
    nas_type = "mikrotik"

    def get_athentication_req(self, session, aaa_server, rad_dict):
        req = packet.AuthPacket(secret=aaa_server.secret_key,
                                dict=rad_dict)

        req['User-Name'] = session.username
        req['User-Password'] = req.PwCrypt(session.password)


        pass
