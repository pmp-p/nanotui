import sys
sys.path.insert(0,'.')
import builtins

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
    print('Overriding',mname,module)
    setattr( builtins , mname , module )
    sys.modules[mname]= module

try:
    import select
    select.select
    import os
    import os.path
    import time
    UPY=False
except:
    UPY=True
    try:
        import utime as time
    except:
        import time
    from mpycompat import *
    import os
    import os.path

Override('os',os)
Override('Time',time)
#Override('sys',sys)

class Continue:pass



import nanotui.screen

from nanotui.widgets import *


nanotui.screen.NX = NX
nanotui.screen.tty = tty

BusyLoop = -1
Pass = -1


def x0y1(*argv):
    return argv

def xy(*argv):
    return argv



class Point:
    def __init__(self,dialog,fmt,width):
        self.width = width
        self.d = dialog
        self.x = dialog.cx
        self.y = dialog.cy
        self.fmt =fmt
        self.i = None

    def __call__(self,__text__=None,**kw):
        #FIXME: update self.width to just erase last output
        if __text__ is not None:
            __text__=str(__text__)
            kw['text']=__text__ + ( self.width - len(__text__)) * ' '
        if not self.i:
            self.i  = nanotui.widgets.WLabel(text= self.fmt % kw )
            self.d.xy_add( self.x, self.y , self.i )
            return True
        else:
            return self.i.set_text(  (self.fmt % kw)[:self.width] )



class VisualPage(nanotui.widgets.Dialog):
    def __init__(self,name,text='Nanotui app',width=80,height=25,x=1,y=1):
        nanotui.widgets.Dialog.__init__(self,text,width,height,x,y)
        self.name = name
        self.cx = x+1
        self.cy = y+0

        self.duty = 5
        self.handler = None



    def frame(self,txt,x=0,y=0,dx=0,dy=0,width=0,height=3):
        x,y = xy( x,y )

        x = ( x or self.cx ) + dx
        y = ( y or self.cy ) + dy

        width = width or len(txt.replace('\n',''))+2
        height += txt.count('\n')

        wf = nanotui.widgets.WFrame(text=txt.strip(),width=width,height=height )
        self.xy_add(x,y, wf  )

        self.cy += 1+dy
        self.cx = x + 1
        return wf


    def __call__(self,wname,klass,*argv,**kw):
        set=kw.setdefault
        wmaker = getattr( nanotui.widgets, 'W%s' % klass)


        set('x',self.cx)
        set('y',self.cy)
        self.cx = kw.pop('x')
        self.cy = kw.pop('y')
        if 'items' in kw:
            wdg = wmaker(items=kw.pop('items'),**kw)
        else:
            wdg = wmaker(kw.pop('text'),**kw)
        wdg.name = wname
        self.xy_add(self.cx,self.cy, wdg)
        self.cy+= wdg.y+1
        self.cx+= wdg.width+1
        if self.cx > self.width:
            self.cx=1
        return wdg


    def update(self,point,text):
        self.add( point.x , point.y , text)


    def anchor(self,text='',fmt='%(text)s',**kw):

        dx = len(text.replace('\n','') )
        dy = text.count('\n')

        p = Point(self,fmt=fmt,width=dx)

        if text.strip():
            kw.setdefault('text',text.strip())
            p(**kw)

        #write
        if not dy:
            self.cx += dx
        self.cy += dy
        return p

    def get_input(self):
        global keybuffer
        key=b''
        if self.kbuf:
            key = self.kbuf[0:1]
            self.kbuf = self.kbuf[1:]
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


    def step(self):
        global BusyLoop,Pass
        inp = None


        inp = self.get_input()
        BusyLoop += 1
        if not BusyLoop % self.duty:
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


    def loop(self):
        global BusyLoop,Pass,ec,crt

        inp = None
        if ec.get(self.name,Continue) is not None:
            self.redraw()

        while ec.get(self.name,Continue) is Continue:
            inp = self.get_input()
            BusyLoop += 1
            if not BusyLoop % self.duty:
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

        #non runtime error condition, do cleanup
        return -1

    def __enter__(self):
        global crt,dlg
        if crt is None:
            crt = nanotui.screen.Screen()
            crt.Begin() #self.region.Begin()
        dlg.append( self )
        return self

    def End(self,exitcode=None,error=None):
        global crt,dlg,ec
        ec[self.name]=exitcode
        dlg.remove( self )
        if not len(dlg):
            crt.End(error=error)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.End( exitcode=self.loop() )

#InitCrt = nanotui.screen.Screen


