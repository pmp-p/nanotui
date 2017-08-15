#import os

from .events import *

from .screen import *



class NodePath:
    root  = None
    count = 0
    factory = None

    def __init__(self,parent,node,pos=[]):
        if parent:
            assert  isinstance(parent,NodePath)
        self.parent = parent
        self.node = node
        self.pos = pos

        self.children = []

        self.__class__.count += 1
        if parent: # and self.root!=parent:
            if not self in parent.children:
                parent.children.append( self )
            return

        #print("198: orphan",node)



def tenp(v,max,coeff = 10000):
    v*=coeff
    max*=coeff
    return int(  (max/100 * v) / coeff / coeff )

#  w=80%  or  x=[10,-10]

def fit(parent,x,y,z,width,height,pad_left,pad_right,pad_top,pad_bottom):
    global crt
    cx,cy=0,0
    if parent==NodePath.root:
        pw,ph = NodePath.root.node.surface()
        px,py = 0,0
    else:
        pw,ph = parent.node.width, parent.node.height
        px,py = parent.node.x, parent.node.y
#        if hasattr(parent.node, 'layout'):
#            px+=parent.node.layout.cx
#            py+=parent.node.layout.cy


    if isinstance(x,(list,tuple) ):
        width = 100 - x[0] + x[1]
        x= px +  tenp( x[0], pw )
    elif x<0:
        x = px+abs(x)
    else:
        x = px

    if isinstance(y,(list,tuple) ):
        height = 100 - y[0] + y[1]
        y= py + tenp( y[0], ph )
    elif y<0:
        y = py+abs(y)
    else:
        y = py

    if width<0:
        width = abs(width)
    else:
        width = tenp( width or 90 , pw )

    if height<0:
        height = abs(height)
    else:
        height = tenp( height or 90 , ph )

    return width,height,x,y,z


#PX=0
#PY=PX+1
#PZ=PY+1
#PW=PZ+1
#PH=PW+1
#Ppl=PH+1
#Ppr=Ppl+1
#Ppt=Ppr+1
#Ppb=Ppt+1
#
#FLOW = 0

class Widget(Screen):

    focusable = False
    # If set to non-False, pressing Enter on this widget finishes
    # dialog, with Dialog.loop() return value being this value.
    finish_dialog = False

    def __init__(self):
        self.kbuf = b""
        self.signals = {}
        self.np = None
        self.text=''
        self.items_count = 0


    def reparent_to(self, parent, pos=None, expand=False, noauto=False):
        if not isinstance(parent,NodePath):
            parent = parent.np

        if self.np is None:
            self.np = NodePath(parent, self, pos)

# FIXME: focus is doomed like redraw was, need scenegraph tree walk
        else:
            #self.np.parent.children.remove(self.np)
            parent.children.append( self.np )
            self.np.parent = parent


        if pos is None:
            pos = self.np.pos

        self.width, self.height, self.x, self.y, self.z = fit(parent, *pos)

        print( self.__class__.__name__, '[',self.width, self.height, '] (', self.x,',', self.y,')', self.text , file=sys.stderr )

        parent = parent.node


        self.dirty = True


        if noauto:
            return self


        if hasattr(self,'SIZE'):
            if self.width < self.SIZE[0]:
                self.width = self.SIZE[0]
            if self.height < self.SIZE[1]:
                self.height = self.SIZE[1]
            if self.SIZE[2] and (self.width > self.SIZE[2]):
                self.width = self.SIZE[2]
            if self.SIZE[3] and (self.height > self.SIZE[3]):
                self.height = self.SIZE[3]

#        if hasattr(parent,'PAD'):
        paddingX = 1
        paddingY = 1


        if hasattr(parent,'layout'):
            if parent.layout.cx + self.width > parent.layout.width:
                parent.layout.cx = parent.layout.x + paddingX
                parent.layout.cy += parent.layout.row_height
                parent.layout.row_height = 1

            self.x += parent.layout.cx + paddingX
            self.y += parent.layout.cy + paddingY
            parent.layout.cx += self.width + paddingX

        else:
        #else no layout is inclusion
            self.x = parent.x+paddingX
            self.y = parent.y+paddingY

            paddingX *=2
            paddingY *=2



            if self.width > parent.width - paddingX:
                self.width = parent.width - paddingX

            if self.height > parent.height - paddingY:
                self.height = parent.height - paddingY

        if expand:
            self.width = parent.width - paddingX
            if self.width < 4:
                self.width = 4
            self.height = parent.height - paddingY
            if self.height<0:
                self.height=1


        if hasattr(parent,'layout') and len(parent.np.children)>2:
            parent.layout.row_height = max( parent.layout.row_height , self.height)
            if parent.layout.row_height>20:
                parent.layout.row_height=20

        print( self.__class__.__name__, '[',self.width, self.height, '] (', self.x,',', self.y,')', self.text , file=sys.stderr )
        print( '' , file=sys.stderr )

        return self

    def halign(self,src=None, delta=0, pad=None):
        if src is None:
            src = Screen.last
        self.y  = src.y + delta
        if pad is not None:
            self.x = src.x+src.width + pad
        return self

    def valign(self,src=None, delta=0, pad=None):
        if src is None:
            src = Screen.last
        self.x  = src.x + delta
        if pad is not None:
            self.y = src.y+src.height + pad
        return self


    def get_rx(self):
        return self.x - self.np.parent.node.x

    def get_ry(self):
        return self.y - self.np.parent.node.y

    def crlf(self,pady=1,padx=1):
        parent = self
        parent.layout.cx = padx
        parent.layout.cy += parent.layout.row_height  + pady
        parent.layout.row_height = 1

    def setup(self,**kw):
        pass

    def is_dirty(self):
        try:
            if self.dirty:
                dirty = True
        except:
            self.dirty = True
        dirty=self.dirty
        if self.dirty:
            return True

        for np in self.np.children:
            w=np.node
            try:
                if w.dirty:
                    dirty = True
                    break
            except:
                w.dirty = True
                break
        return dirty

    def set_text(self,text):
        try:
            if self.text == text:
                return False
        except:
            pass
        self.text = text
        self.dirty = True
        return self.dirty


    def get_text(self):
        return self.text

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def inside(self, x, y):
        return self.y <= y < self.y + self.height and self.x <= x < self.x + self.width


    def addEventListener(self,evname,evfunc):
        e = Event( e = ev._from_name(evname) )
        self.on( e.key , evfunc )


    def signal(self, sig,kw):
        if sig in self.signals:
            self.signals[sig](self,**kw)

    def on(self, sig, handler):
        self.signals.setdefault(sig,[])
        if not handler in self.signals[sig]:
            self.signals[sig].append( handler )

    @staticmethod
    def longest(items):
        if not items:
            return 0
        return max((len(t) for t in items))

    def set_cursor(self):
        # By default, a widget doesn't use text cursor, so disables it
        self.cursor(False)

    def handle_input(self, inp):
        if isinstance(inp, list):
            res = self.handle_mouse(inp[0], inp[1])
        else:
            res = self.handle_key(inp)
        return res

    def loop(self):
        self.redraw()
        while True:
            key = self.get_input()
            res = self.handle_input(key)

            if res is not None and res is not True:
                return res


    def __repr__(self):
        return "(%s)%s" % ( self.__class__.__name__ , self.name )

    __str__ = __repr__
