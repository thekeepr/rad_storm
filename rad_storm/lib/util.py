import random
from uuid import uuid4


def gen_random_mac():
    """
    Generate a random MAC Address
    """
    int_mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]

    mac = ':'.join(map(lambda x: '%02x'%x, int_mac))
    return mac

def gen_unique_id():
    return str(uuid4())

def gen_random_ip():
    """
    Generate a random IPv4 Address
    """
    return '.'.join([str(random.randrange(172,218)),
                     str(random.randrange(1,254)),
                     str(random.randrange(1,254)),
                     str(random.randrange(1,254))
                 ])

def gen_random_nas_port_id():
    '''
    Generate a random DSLAM port to be used as Nas-Port-Id value.
    @todo: accept a connection type and generate the value accordingly
    '''
    rrange = random.randrange
    return 'Dummy-DSLAM atm %s/%s/%s/%s:1.35'%(
        rrange(1, 10), rrange(1, 10),
        rrange(1, 10), rrange(1,64))
