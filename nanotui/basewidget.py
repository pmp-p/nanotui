#import os

from .events import *

from .screen import *

class Widget(Screen):

    focusable = False
    # If set to non-False, pressing Enter on this widget finishes
    # dialog, with Dialog.loop() return value being this value.
    finish_dialog = False

    def __init__(self):
        self.kbuf = b""
        self.signals = {}
        self.parent = None
        self.children = []


    def is_dirty(self):
        try:
            if self.dirty:
                dirty = True
        except:
            self.dirty = True
        dirty=self.dirty
        if self.dirty:
            return True

        for w in self.children:
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

    def signal(self, sig):
        if sig in self.signals:
            self.signals[sig](self)

    def on(self, sig, handler):
        self.signals[sig] = handler

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
