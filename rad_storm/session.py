import time
import random
from gevent import Greenlet
from gevent import Timeout
from gevent import monkey
from gevent import socket
from lib.pyrad import packet
from lib.pyrad.dictionary import Dictionary
from lib.util import gen_random_mac
from lib.util import gen_unique_id
from lib.util import gen_random_ip
from lib.util import gen_random_nas_port_id


RADIUS_DICT = Dictionary('lib/pyrad/dictionary/dictionary')

####### State of Session
# Any component that is directly involved in the
# simulation process should be aware of Session State
# to make coherent action.
STATE_AUTH = 1
STATE_START_ACCT = 2
STATE_UPDATE_ACCT = 3
STATE_STOP_ACCT = 4

STATE_CYCLE = [
    STATE_AUTH,
    STATE_START_ACCT,
    STATE_UPDATE_ACCT,
    STATE_STOP_ACCT
]


##############################
class Session(object):
    '''
    This class holds all the required parameters about
    simulating a single user session.
    '''
    __slots__ = ['username', 'password', 'last_state',
                 'start_state', 'ip_addr', 'mac_addr',
                 'nas_port_id', 'nas_port', 'session_id']

    def __init__(self, username, password, start_state=STATE_AUTH):
        self.username = username
        self.password = password
        self.start_state = start_state
        self.last_state = start_state
        ########## Connection Info
        self.session_id = None
        self.ip_addr = None
        self.mac_addr = None
        self.nas_port_id = None
        self.nas_port = None

    def __repr__(self):
        return 'Session %s:%s (session_id=%s, mac=%s, ip=%s, nas_port_id=%s)'%(
            self.username, self.password, self.session_id,
            self.mac_addr, self.ip_addr, self.nas_port_id)

    def set_params(self):
        '''
        Update connection info parameters to valid random values
        '''
        if not self.mac_addr:
            self.mac_addr = gen_random_mac()

        if not self.nas_port_id:
            self.nas_port_id = gen_random_nas_port_id()

        if not self.ip_addr:
            self.ip_addr = gen_random_ip()

        # we need a new session id (Acct-Session-Id)
        if self.last_state == STATE_AUTH:
            self.session_id = gen_unique_id()
            self.nas_port = random.randrange(99999, 999999)

    def reset_state(self):
        self.last_state = STATE_AUTH

    def next_state(self, go_next):
        if go_next:
            state_idx = STATE_CYCLE.index(self.last_state)
            self.last_state = STATE_CYCLE[state_idx+1]


class AAAServer(object):
    '''
    Holds RADIUS Server Info
    '''
    host = '127.0.0.1'
    auth_port = 1812
    acct_port = 1813
    interim_update_interval = 60 #Seconds
    timeout = 3 #Seconds
    retry = 3
    secret_key = 'secret'

    def __repr__(self):
        return 'AAA Server %s@%s:%s:%s'%(
            self.secret_key, self.host,
            self.auth_port, self.acct_port)


class SessionActor(Greenlet):
    '''
    This is the base for Session simulation.
    SessionActor controls the activities related to
    actually simulating that session, independetly
    from others sessions
    '''
    def __init__(self, session, nas, aaa_server):
        Greenlet.__init__(self)
        self.session = session
        self.nas = nas
        self.aaa_server = aaa_server
        self.start_time = None

    def _run(self):
        self.aaa_control_loop()

    def aaa_control_loop(self):
        '''
        This is the simulation orchestration for this session
        '''
        self.start_time = time.time()
        while True:
            if self.session.last_state == STATE_AUTH:
                go_next = self.do_authenticate()
                if not go_next: # not response after all
                    gevent.sleep(random.randrange(1, 50)/10.0)
                    continue

            elif self.session.last_state == STATE_START_ACCT:
                go_next = self.do_acct_start()
                if not go_next: # no good, do auth again
                    self.session.last_state = STATE_AUTH
                    gevent.sleep(random.randrange(1, 30)/10.0)
                    continue

            self.session.next_state(go_next)

    def _send_and_recv(self, pkt, port):
        resp = None
        tries = 0
        while tries < self.aaa_server.retry:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.aaa_server.timeout)
            try:
                sock.sendto(pkt, (self.aaa_server.host, port))
                resp, _addr = sock.recvfrom(1024)
            except socket.timeout:
                sock.close()
                tries += 1

        return resp

    def do_random_sleep(self, up, down):
        gevent.sleep( random.randrange(up, down)/10.0 )

    def do_authenticate(self):
        self.session.set_params()
        radius_req = self.nas.get_authentication_req(self.session, RADIUS_DICT)
        radius_pkt = radius_req.get_radius_packet()
        resp = self._send_and_recv(radius_pkt, self.aaa_server.auth_port)
        if not resp:
            self.do_random_sleep(1,30)
            return False

        #@todo: handle response
        return True

    def do_acct_start(self):
        raise NotImplementedError()

    def do_acct_update(self):
        raise NotImplementedError()

    def do_acct_stop(self):
        raise NotImplementedError()
