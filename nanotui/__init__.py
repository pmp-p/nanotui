# -*- coding: utf-8 -*-
from __future__ import with_statement
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# http://www.linusakesson.net/programming/tty/
# fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


import sys
if not '.' in sys.path:sys.path.insert(0,'.')

try:
    import builtins
    builtins.p3bytes = bytes
except:
    import __builtin__ as builtins
    builtins.builtins = builtins
    def p3bytes(s,c):return str(s)
    builtins.p3bytes=p3bytes

ec={}


crt = None

dlg = []


my = __import__(__name__)


try:
    NX = True
    import tty
    import termios
    termios = None

except:
    NX = False
    class tty:
        @classmethod
        def setraw(*argv,**kw):pass
    termios = None
    try:
        import msvcrt
    except:
        pass

def Override(mname,module):
    warn('Overriding',mname,module)
    setattr( builtins , mname , module )
    sys.modules[mname]= module

if UPY:
    import utime as time
    #from mpycompat import *
    import os
    import os.path
else:
    import select
    import os
    import os.path
    import time


Override('os',os)
Override('Time',time)
#Override('sys',sys)

class Continue:pass

def boxpipe(wdg,shell,clear=False):
    lines=[]
    for line in os.popen(shell).readlines():
        lines.append( line.strip() )

    if clear:
        wdg.items=[]
        wdg.dirty=True

    if len(lines):
        wdg.items.extend( lines )
        wdg.items_count = len( wdg.items)
        wdg.redraw()




def zfill(i,places,char='0'):
    i=str(i)
    if len(i)<places:  i = '%s%s' % (  char * ( places-len(i) ) , i )
    return i



RunTime.add('zfill', zfill )
RunTime.add('boxpipe',boxpipe)



import nanotui.screen

from nanotui.widgets import *

nanotui.screen.NX = NX
nanotui.screen.tty = tty

BusyLoop = -1
Pass = -1

def clock(sep=':'):
    import time
    y,my,d,h,m,s = time.localtime( Time.time() )[:6]
    return '%s%c%s%c%s'  % ( zfill(h,2),sep,zfill(m,2),sep,zfill(s,2) )


def x0y1(*argv):
    return argv

def xy(*argv):
    return argv


#
#class Point:
#    def __init__(self,dialog,fmt,width):
#        self.width = width
#        self.d = dialog
#        self.x = dialog.x + dialog.layout.cx
#        self.y = dialog.y + dialog.layout.cy
#        self.fmt =fmt
#        self.i = None
#
#    def __call__(self,__text__=None,**kw):
#        #FIXME: update self.width to just erase last output
#        if __text__ is not None:
#            __text__=str(__text__)
#            kw['text']=__text__ + ( self.width - len(__text__)) * ' '
#        if not self.i:
#            self.i  = nanotui.widgets.WLabel()
#            self.i.setup( text= self.fmt % kw , x= -self.x, y = -self.y)
#            return True
#        else:
#            #return self.i.set_text(  (self.fmt % kw)[:self.width] )
#            return self.i.set_text(  (self.fmt % kw)[:] )


class Anchor:
    def __init__(self,lbl,fmt):
        self.i = lbl
        self.fmt =fmt

    def reparent_to(self,*argv,**kw):
        return self.i.reparent_to(*argv,**kw)


    def __call__(self,__text__=None,**kw):
        if __text__ is not None:
            __text__=str(__text__)
            kw['text']=__text__ + ( (self.i.np.parent.node.width-2) - len(__text__)) * ' '

        return self.i.set_text(  (self.fmt % kw)[:(self.i.np.parent.node.width-2)] )

class defdict(dict):

    def __missing__(self,key):
        return key


class Progress:
    def __init__(self,frm,anchor):
        self.container = frm
        self.fmkeys = {None:None}
        self.format = gt= frm.get_text()
        while True:
            try:
                gt = gt % self.fmkeys
                break
            except KeyError as k:
                k= str(k)[1:-1]
                self.fmkeys[k]='${%s}'%k

        self.i = anchor
        self.percent  = 0


    def __getattr__(self, attr):
        if hasattr(self.container,attr):
            return getattr(self.container,attr)

    def update(self,percent=None,**kw):
        self.i.reparent_to( self.container, expand=True )
        if percent is not None:
            if percent>100:
                percent = 100
            kw['percent'] = self.percent = percent
            percent  = int( ( ( float( self.container.width ) - 2 ) / 100.0) * percent )
            self.i.set_text('X' * percent )

        if not len(kw):return

        for k in kw:
            self.fmkeys[k]=kw.get(k)

        warn(self.fmkeys, self.format)
        self.container.set_text( self.format % self.fmkeys )




class VisualPage(nanotui.widgets.Dialog):
    top = RunTime.unset

    def __init__(self,name,text='Nanotui app',width=0,height=0,x=0,y=0,z=0,stream=sys.stdin):
        global crt, dlg
        self.by_names = {}

        if crt is None:
            warn('<crt>',file=sys.stderr)
            crt = nanotui.screen.Screen()
            crt.Begin() #self.region.Begin()
            NodePath.root = NodePath(None,crt,[])
            crt.surface()
            warn('</crt>',file=sys.stderr)

        if self.__class__.top is RunTime.unset:
            self.__class__.top = self
            self.parent = crt
        else:
            self.parent = self.top

        self.self = self
        self.name = name
        self.event = RunTime.unset

        pos = [x, y, z, width, height, 1, 1, 1, 1,]

        NodePath.factory = self

        dlg.append( self )

        nanotui.screen.Screen.last = self.last = self.render = self.current = self

        self.layout = crt

        self.modules = [ __import__('__main__') ]

        #text = text + ' '+ repr( crt.surface() )

        try:super().__init__()
        except:nanotui.widgets.Dialog.__init__(self)
        self.setup(text=text,width=width,height=height,x=x,y=y,z=z)

        self.reparent_to(NodePath.root, pos, noauto=True )

        self.duty = 5
        self.handler = None
        self.bluelet = None


    def surface(self):
        return crt.surface()


    def __call__(self,klass,*argv,**kw):
        set=kw.setdefault

        wname = kw.pop('name','rnd%s'% str(NodePath.count) )
        wmaker = getattr( nanotui.widgets, 'W%s' % klass)

        set('x',0)
        set('y',0)
        set('z',0)
        set('width',20)
        set('height',20)
        set('padding-left',1)
        set('padding-right',1)
        set('padding-top',1)
        set('padding-bottom',1)
        pos = []
        for k in 'x y z width height padding-left padding-right padding-top padding-bottom'.split(' '):
            pos.append( kw[k] )

        wdg = wmaker()
        wdg.name = wname
        wdg.setup(**kw)

        self.by_names[wname] = wdg

        nanotui.screen.Screen.last = self.last = self.current
        self.current  = wdg

        wdg.reparent_to( self.render, pos )
        return wdg

    def __getitem__(self,key,defval=None):
        return self.by_names.get(key,defval)
        #TODO: black hole option

    def anchor(self,text,fmt='%(text)s',**kw):
        lbl = self.__call__('Label',text=text,**kw)
        a = Anchor( lbl , fmt )
        #a.w = lbl.width
        return a

    def textfill(self,text,fmt='%(text)s',**kw):
        hook = self.current
        kw.setdefault('width', hook.width-2)
        if text=='':
            text = '_'*(hook.width-3)+']'
        a = self.anchor(text,fmt=fmt,**kw)
        a.reparent_to(hook, expand=True)
        #a.w = len(text)
        return a

    def progress(self,name='txrx',text="Transfer Progress %(src)s => %(dst)s  %(size)s / %(total)s",width=90, percent=100):
        txrx_frm = window('Frame',text=text,width=width,height=-3)
        txrx = window.anchor('X'* (txrx_frm.width-2) ).reparent_to( txrx_frm, expand=True )
        return Progress(txrx_frm,txrx)


    def get_input(self):
        global crt
        key=b''
        if self.kbuf:
            key = self.kbuf[0:1]
            self.kbuf = self.kbuf[1:]
        else:
            if len(crt.keybuf):
                #this get fill if size fails read
                key = crt.keybuf.pop(0)
            else:
                if UPY or NX:
                    if not select.select([sys.stdin,],[],[],0.0)[0]:
                        return None
                else:
                    if not msvcrt.kbhit():
                        return None
                if UPY:
                    key = select.readall(sys.stdin)
                else:
                    key = os.read(0, 32)

            if key[0] != 0x1b:
                self.kbuf = key[1:]
                key = key[0:1]
        key = KEYMAP.get(key, key)

        if isinstance(key, bytes) and key.startswith(b"\x1b[M") and len(key) == 6:
            row = key[5] - 33
            col = key[4] - 33
            return [col, row]

        return key


    def step(self,tick=False):
        global BusyLoop,Pass

        inp = self.get_input()
        BusyLoop += 1
        if tick:
            Pass += 1
            if self.handler:
                self.handler(Pass)
            if self.is_dirty():
                self.redraw()

        if inp is not None:
            self.redraw()
            if isinstance(inp, list):
                res = self.handle_mouse(inp[0], inp[1])
            else:
                res = self.handle_key(inp)

            if res is not None and res is not True:
                return res
        #default return None



    def loop(self):
        global BusyLoop,Pass,ec,crt
        warn("<ui.loop>",file=sys.stderr)
        frametime = Lapse(1.0/20)
        if ec.get(self.name,Continue) is not None:
            self.redraw()
        try:
            while ec.get(self.name,Continue) is Continue:
                if frametime:
                    res = self.step(True)
                    if res is not None:
                        return res
                else:
                    Time.sleep(.001)
        finally:
            warn("</ui.loop>",file=sys.stderr)
        #non runtime error condition, do cleanup
        return -1


    def blueloop(self,sleept=0):
        frametime = Lapse(1.0/20)
        global BusyLoop,Pass,ec,crt
        warn("<ui.loop>",file=sys.stderr)
        inp = None
        if ec.get(self.name,Continue) is not None:
            self.redraw()

        while ec.get(self.name,Continue) is Continue:
            inp = self.get_input()
            if frametime:
                Pass += 1
                if self.handler:
                    self.handler(Pass)
                if self.is_dirty():
                    self.redraw()
            else:
                if sleept:
                    Time.sleep(sleept)

            if inp is not None:
                self.redraw()
                if isinstance(inp, list):
                    res = self.handle_mouse(inp[0], inp[1])
                else:
                    res = self.handle_key(inp)

            res = self.step()
            if res is not None:
                yield bluelet.end( value = res )
            else:
                yield bluelet.null()
        warn("</ui.loop>",file=sys.stderr)

    def __enter__(self):
        global crt,dlg
        return self

    def End(self,exitcode=None,error=None):
        global crt,dlg,ec
        ec[self.name]=exitcode
        if self in dlg:
            dlg.remove( self )
        if not len(dlg):
            if crt:
                crt.End(error=error)
                crt = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.End( exitcode=self.loop() )

#InitCrt = nanotui.screen.Screen


