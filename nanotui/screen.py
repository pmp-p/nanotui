# -*- coding: utf-8 -*-

import os
import sys

#assume linux by default
NX = True
import nanotui
import nanotui.colors

def C_PAIR(fg, bg):
    return (bg << 4) + fg


KEY_UP = 1
KEY_DOWN = 2
KEY_LEFT = 3
KEY_RIGHT = 4
KEY_HOME = 5
KEY_END = 6
KEY_PGUP = 7
KEY_PGDN = 8
KEY_QUIT = 9
KEY_ENTER = 10
KEY_BACKSPACE = 11
KEY_DELETE = 12
KEY_TAB = b"\t"
KEY_SHIFT_TAB = b"\x1b[Z"
KEY_ESC = 20
KEY_F1 = 30
KEY_F2 = 31
KEY_F3 = 32
KEY_F4 = 33
KEY_F5 = b'\x1b[15~'
KEY_F6 = b'\x1b[17~'
KEY_F7 = b'\x1b[18~'
KEY_F8 = b'\x1b[19~'
KEY_F9 = b'\x1b[20~'
KEY_F10 = b'\x1b[21~'

KEYMAP = {
b"\x1b[A": KEY_UP,
b"\x1b[B": KEY_DOWN,
b"\x1b[D": KEY_LEFT,
b"\x1b[C": KEY_RIGHT,
b"\x1bOH": KEY_HOME,
b"\x1bOF": KEY_END,
b"\x1b[1~": KEY_HOME,
b"\x1b[4~": KEY_END,
b"\x1b[5~": KEY_PGUP,
b"\x1b[6~": KEY_PGDN,
b"\x03": KEY_QUIT,
b"\r": KEY_ENTER,
b"\x7f": KEY_BACKSPACE,
b"\x1b[3~": KEY_DELETE,
b"\x1b": KEY_ESC,
b"\x1bOP": KEY_F1,
b"\x1bOQ": KEY_F2,
b"\x1bOR": KEY_F3,
b"\x1bOS": KEY_F4,
}

class Screen():

    color = nanotui.colors.Color

    keybuf = []
    surf = None

    x=0
    y=0
    width=80
    height=25

    last = None


    def __init__(self, clear=True, mouse=True):
        self.clear = clear
        self.mouse = mouse
        self.cx = 0
        self.cy = 0
        self.row_height = 1

    @staticmethod
    def wr(s):
        # TODO: When Python is 3.5, update this to use only bytes
        if isinstance(s, str):
            s = p3bytes(s, "utf-8")
        os.write(1, s)

    @staticmethod
    def wr_fixedw(s, width):
        # Write string in a fixed-width field
        s = s[:width]
        Screen.wr(s)
        Screen.wr(" " * (width - len(s)))
        # Doesn't work here, as it doesn't advance cursor
        #Screen.clear_num_pos(width - len(s))

    @staticmethod
    def cls():
        Screen.wr(b"\x1b[2J")

    @staticmethod
    def goto(x, y):
        # TODO: When Python is 3.5, update this to use bytes
        Screen.wr("\x1b[%d;%dH" % (y + 1, x + 1))

    @staticmethod
    def clear_to_eol():
        Screen.wr(b"\x1b[0K")

    # Clear specified number of positions
    @staticmethod
    def clear_num_pos(num):
        if num > 0:
            Screen.wr("\x1b[%dX" % num)

    @staticmethod
    def attr_color(fg, bg=-1):
        if bg == -1:
            bg = fg >> 4
            fg &= 0xf
        # TODO: Switch to b"%d" % foo when py3.5 is everywhere
        if bg is None:
            if (fg > 8):
                Screen.wr("\x1b[%d;1m" % (fg + 30 - 8))
            else:
                Screen.wr("\x1b[%dm" % (fg + 30))
        else:
            assert bg <= 8
            if (fg > 8):
                Screen.wr("\x1b[%d;%d;1m" % (fg + 30 - 8, bg + 40))
            else:
                Screen.wr("\x1b[0;%d;%dm" % (fg + 30, bg + 40))

    @staticmethod
    def attr_reset():
        Screen.wr(b"\x1b[0m")

    #@classmethod
    def cursor(self,onoff):
        if onoff:
            Screen.wr(b"\x1b[?25h")
        else:
            Screen.wr(b"\x1b[?25l")


    def draw_box(self, left, top, width, height):
        # Use http://www.utf8-chartable.de/unicode-utf8-table.pl
        # for utf-8 pseudographic reference
        bottom = top + height - 1
        self.goto(left, top)
        # "┌"
        self.wr(b"\xe2\x94\x8c")
        # "─"
        hor = b"\xe2\x94\x80" * (width - 2)
        self.wr(hor)
        # "┐"
        self.wr(b"\xe2\x94\x90")

        self.goto(left, bottom)
        # "└"
        self.wr(b"\xe2\x94\x94")
        self.wr(hor)
        # "┘"
        self.wr(b"\xe2\x94\x98")

        top += 1
        while top < bottom:
            # "│"
            self.goto(left, top)
            self.wr(b"\xe2\x94\x82")
            self.goto(left + width - 1, top)
            self.wr(b"\xe2\x94\x82")
            top += 1

    def clear_box(self, left, top, width, height):
        # doesn't work
        #self.wr("\x1b[%s;%s;%s;%s$z" % (top + 1, left + 1, top + height, left + width))
        s = b" " * width
        bottom = top + height
        while top < bottom:
            self.goto(left, top)
            self.wr(s)
            top += 1

    def dialog_box(self, left, top, width, height, title=""):
        self.clear_box(left + 1, top + 1, width - 2, height - 2)
        self.draw_box(left, top, width, height)
        if title:
            #pos = (width - len(title)) / 2
            pos = 1
            self.goto(left + pos, top)
            self.wr(title)

    @classmethod
    def init_tty(cls):
        if NX:
            import termios
            cls.org_termios = termios.tcgetattr(0)
        tty.setraw(0)

    @classmethod
    def deinit_tty(cls):
        if NX:
            import termios
            termios.tcsetattr(0, termios.TCSANOW, cls.org_termios)

    @classmethod
    def enable_mouse(cls):
        # Mouse reporting - X10 compatibility mode
        cls.wr(b"\x1b[?9h")

    @classmethod
    def disable_mouse(cls):
        # Mouse reporting - X10 compatibility mode
        cls.wr(b"\x1b[?9l")

    @classmethod
    def surface(cls):
        if cls.surf is None:
            cls.wr(b"\x1b[18t")
            #NO resizing term will lock output!
            #res = select.select([0], [], [], 0.2)[0]
            buf = b''
            try:
                #if res:
                buf = os.read(0, 32)
                assert buf.startswith(b"\x1b[8;") and buf[-1:] == b"t"
                vals = buf[:-1].split(b";")
                cls.surf= (int(vals[2]), int(vals[1]))
                return cls.surf
            except:
                cls.keybuf.append( buf )
            return (80,24)
        cls.width , cls.height = cls.surf
        return cls.surf

    # Set function to redraw an entire (client) screen
    # This is called to restore original screen, as we don't save it.
    @classmethod
    def set_screen_redraw(cls, handler):
        cls.screen_redraw = handler


    def Begin(self):
        self.ec = -1
        self.init_tty()

        if self.mouse:
            self.enable_mouse()

        self.attr_color(self.color.WHITE, self.color.BLUE)
        if self.cls:
            self.cls()

        self.attr_reset()
        return self

    def End(self,error=None):
        self.goto(0, 50)
        self.cursor(True)
        if self.mouse:
            Screen.disable_mouse()
        self.deinit_tty()
        if error is not None:
            et, ei, tb = sys.exc_info()
            try:
                sys.stdout = sys.__stdout__
                raise ei.with_traceback(tb)
            except:
                raise error




    def __enter__(self):
        return self.Begin()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.End()

