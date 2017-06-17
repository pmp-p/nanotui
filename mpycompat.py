import sys
sys.path.insert(0,'%s/mpy' % __file__.rsplit('mpycompat',1)[0] )

import builtins

try:
    import utime as time
except:
    import time

import _thread



class select:
    ioq = {}
    iow = []

    @classmethod
    def select(cls,rl,wl,xl,timeout=0):
        fd=rl[0]
        fdid=id(fd)
        if not fdid in cls.ioq:
            cls.ioq[fdid]=[]
            cls.iow.append( iowait(fd, len(cls.iow)+1 ) )

        return [len( cls.ioq[fdid] )]

    @classmethod
    def readall(cls,fd):
        buf=b''
        fdid=id(fd)
        while len(select.ioq[fdid]):
            buf += select.ioq[fdid].pop(0)
        return buf



class iowait:

    select = select

    def __init__(self,fd,tid):
        self.fd = fd
        _thread.start_new_thread(self.run,[tid,0])

    def run(self,*argv):
        fdid=id(self.fd)
        while True:
            try:
                if 0:
                    self.select.ioq[fdid].append( self.fd.read(1) )
                else:
                    d=os.read(0,1)
                    if d:
                        self.select.ioq[fdid].append( d )

            except Exception as e:
                print(self.fd,e)
                return

builtins.Time = time
builtins.sys = sys


def isDefined(varname,name=None):
    if not hasattr(__import__(name or __name__),varname):
        try:
            eval(varname)
        except NameError:
            return False
    return True

class robject(object):
    def ref(self):
        RunTime.CPR[id(self)]=self
        try:
            tips=self.to_string()
        except:
            try:
                tips= str( self )
            except:
                tips=object.__repr__(self)
        return 'µO|%s|%s' % ( id(self) , tips )

#TODO: unref

    def __repr__(self):
        if not RunTime.SerFlag:
            try:
                return self.to_string()
            except:
                return object.__repr__(self)
        return self.ref()

def noop(*argv,**kw):pass

class RunTime:

    SerFlag = 0

    CPR = {}

    Timers = {}

    builtins = builtins
    IP = '0.0.0.0'

    urpc = None

    srv = 'http://192.168.1.66/mpy'

    ANSI_CLS = ''.join( map(chr, [27, 99, 27, 91, 72, 27, 91, 50, 74] ) )

    SSID = 'SSID'
    WPA = 'password'

    webrepl = None
    server_handshake = None
    server_http_handler = None

    I2C_FOLLOWER = 0x0

    MEM_init = 32678

    @classmethod
    def add(cls,entry,value):
        global protect
        setattr(builtins,entry,value)
        if not entry in protect:
            protect.append(entry)

    @classmethod
    def to_json(cls,data):
        cls.SerFlag += 1
        try:
            return json.dumps(data)
        finally:
            cls.SerFlag -= 1



builtins.RunTime = RunTime
builtins.use = RunTime
builtins.isDefined = isDefined
builtins.robject = robject
builtins.do_gc = noop
