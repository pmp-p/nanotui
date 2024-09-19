# -*- coding: utf-8 -*-
protect = ["RunTime"]


class RunTime:
    @classmethod
    def add(cls, entry, value):
        global protect
        setattr(builtins, entry, value)
        if not entry in protect:
            protect.append(entry)


# http://www.linusakesson.net/programming/tty/
# fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


import sys

if not "." in sys.path:
    sys.path.insert(0, ".")

try:
    import builtins

    builtins.p3bytes = bytes
except:
    import __builtin__ as builtins

    builtins.builtins = builtins

    def p3bytes(s, c):
        return str(s)

    builtins.p3bytes = p3bytes

ec = {}


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
        def setraw(*argv, **kw):
            pass

    termios = None
    try:
        import msvcrt
    except:
        pass


def Override(mname, module):
    print("Overriding", mname, module)
    setattr(builtins, mname, module)
    sys.modules[mname] = module


try:
    import select

    select.select
    import os
    import os.path
    import time

    UPY = False
except:
    UPY = True
    try:
        import utime as time
    except:
        import time
    from mpycompat import *
    import os
    import os.path

Override("os", os)
Override("Time", time)
# Override('sys',sys)


class Continue:
    pass


def boxpipe(wdg, shell, clear=False):
    lines = []
    for line in os.popen(shell).readlines():
        lines.append(line.strip())

    if clear:
        wdg.items = []
        wdg.dirty = True

    if len(lines):
        wdg.items.extend(lines)
        wdg.items_count = len(wdg.items)
        wdg.redraw()


class Lapse:
    def __init__(self, intv=1.0, oneshot=None):
        self.intv = int(intv)  # * 1000000 )
        self.next = self.intv
        self.last = time.time()
        self.count = 1
        if oneshot:
            self.shot = False
            return
        self.shot = None

    # FIXME: pause / resume(reset)

    def __bool__(self):
        if self.shot is True:
            return False

        t = clock_ticks()
        self.next -= t - self.last
        self.last = t
        if self.next <= 0:
            if self.shot is False:
                self.shot = True
            self.count += 1
            self.next = self.intv
            return True

        return False


def zfill(i, places, char="0"):
    i = str(i)
    if len(i) < places:
        i = "%s%s" % (char * (places - len(i)), i)
    return i


RunTime.add("Lapse", Lapse)
RunTime.add("zfill", zfill)
RunTime.add("boxpipe", boxpipe)


import nanotui.screen

from nanotui.widgets import *


nanotui.screen.NX = NX
nanotui.screen.tty = tty

BusyLoop = -1
Pass = -1


def clock(sep=":"):
    import time

    y, my, d, h, m, s = time.localtime(Time.time())[:6]
    return "%s%c%s%c%s" % (zfill(h, 2), sep, zfill(m, 2), sep, zfill(s, 2))


def x0y1(*argv):
    return argv


def xy(*argv):
    return argv


class Point:
    def __init__(self, dialog, fmt, width):
        self.width = width
        self.d = dialog
        self.x = dialog.cx
        self.y = dialog.cy
        self.fmt = fmt
        self.i = None

    def __call__(self, __text__=None, **kw):
        # FIXME: update self.width to just erase last output
        if __text__ is not None:
            __text__ = str(__text__)
            kw["text"] = __text__ + (self.width - len(__text__)) * " "
        if not self.i:
            self.i = nanotui.widgets.WLabel(text=self.fmt % kw)
            self.d.xy_add(self.x, self.y, self.i)
            return True
        else:
            return self.i.set_text((self.fmt % kw)[: self.width])


def tenp(v, max, coeff=10000):
    v *= coeff
    max *= coeff
    return int((max / 100 * v) / coeff / coeff)


# print( tenp( 99,255 ) )
# raise SystemExit


def fit(parent, width, height, x, y, z):
    global crt
    if parent == crt:
        pw, ph = crt.surface()
        px, py = 1, 1
    width = tenp(90, pw)
    height = tenp(90, ph)
    return width, height, x, y, z


class VisualPage(nanotui.widgets.Dialog):
    def __init__(self, name, text="Nanotui app", width=-1, height=-1, x=1, y=1, z=0):
        self.name = name
        self.ini = text
        self.pos = [width, height, x, y, z]

    def late_init(self):
        global crt
        width, height, x, y, z = fit(crt, *self.pos)
        try:
            super().__init__(self.ini, width, height, x, y)
        except:
            nanotui.widgets.Dialog.__init__(self, self.ini, width, height, x, y, z)
        # self.name = name
        self.cx = x + 1
        self.cy = y + 0

        self.duty = 5
        self.handler = None

    def surface(self):
        return crt.surface()

    def frame(self, txt, x=0, y=0, dx=0, dy=0, width=0, height=3):
        x, y = xy(x, y)

        x = (x or self.cx) + dx
        y = (y or self.cy) + dy

        width = width or len(txt.replace("\n", "")) + 2
        height += txt.count("\n")

        wf = nanotui.widgets.WFrame(text=txt.strip(), width=width, height=height)
        self.xy_add(x, y, wf)

        self.cy += 1 + dy
        self.cx = x + 1
        return wf

    def __call__(self, wname, klass, *argv, **kw):
        set = kw.setdefault
        wmaker = getattr(nanotui.widgets, "W%s" % klass)

        set("x", self.cx)
        set("y", self.cy)
        self.cx = kw.pop("x")
        self.cy = kw.pop("y")
        if "items" in kw:
            wdg = wmaker(items=kw.pop("items"), **kw)
        else:
            wdg = wmaker(kw.pop("text"), **kw)
        wdg.name = wname
        self.xy_add(self.cx, self.cy, wdg)
        self.cy += wdg.y + 1
        self.cx += wdg.width + 1
        if self.cx > self.width:
            self.cx = 1
        return wdg

    def update(self, point, text):
        self.add(point.x, point.y, text)

    def anchor(self, text="", fmt="%(text)s", **kw):

        dx = len(text.replace("\n", ""))
        dy = text.count("\n")

        p = Point(self, fmt=fmt, width=dx)

        if text.strip():
            kw.setdefault("text", text.strip())
            p(**kw)

        # write
        if not dy:
            self.cx += dx
        self.cy += dy
        return p

    def get_input(self):
        global crt
        key = b""
        if self.kbuf:
            key = self.kbuf[0:1]
            self.kbuf = self.kbuf[1:]
        else:
            if len(crt.keybuf):
                # this get fill if size fails read
                key = crt.keybuf.pop(0)
            else:
                if UPY or NX:
                    if not select.select(
                        [
                            sys.stdin,
                        ],
                        [],
                        [],
                        0.0,
                    )[0]:
                        return None
                else:
                    if not msvcrt.kbhit():
                        return None
                if UPY:
                    key = select.readall(sys.stdin)
                else:
                    try:
                        key = os.read(0, 32)
                    except:
                        return key
            if not key:
                return key
            if key[0] != 0x1B:
                self.kbuf = key[1:]
                key = key[0:1]
        key = KEYMAP.get(key, key)

        if isinstance(key, bytes) and key.startswith(b"\x1b[M") and len(key) == 6:
            row = key[5] - 33
            col = key[4] - 33
            return [col, row]

        return key

    def step(self):
        global BusyLoop, Pass
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
        global BusyLoop, Pass, ec, crt

        inp = None
        if ec.get(self.name, Continue) is not None:
            self.redraw()

        while ec.get(self.name, Continue) is Continue:
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

        # non runtime error condition, do cleanup
        return -1

    def __enter__(self):
        global crt, dlg
        if crt is None:
            crt = nanotui.screen.Screen()
            crt.Begin()  # self.region.Begin()
        self.late_init()
        dlg.append(self)
        return self

    def End(self, exitcode=None, error=None):
        global crt, dlg, ec
        ec[self.name] = exitcode
        if self in dlg:
            dlg.remove(self)
        if not len(dlg):
            crt.End(error=error)
            crt = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.End(exitcode=self.loop())


# InitCrt = nanotui.screen.Screen
