#
# Extended VT100 terminal text editor, etc. widgets
# Copyright (c) 2015 Paul Sokolovsky
# Distributed under MIT License
#
import sys
import os
from .screen import *
from .editor import *


# Edit single line, quit on Enter/Esc
class LineEditor(WEditor):

    def handle_cursor_keys(self, key):
        try:
            if super().handle_cursor_keys(key): #MP
                self.just_started = False
                return True
        except:
            if Editor.handle_cursor_keys(self,key):
                self.just_started = False
                return True

        return False

    def handle_key(self, key):
        if key in (KEY_ENTER, KEY_ESC):
            return key
        if self.just_started:
            # Overwrite initial string with new content
            self.set_lines([""])
            self.col = 0
            self.just_started = False

        try:return super().handle_key(key) #MP
        except:return Editor.handle_key(self,key)


    def edit(self, line):
        self.set_lines([line])
        self.col = len(line)
        self.adjust_cursor_eol()
        self.just_started = True
        key = self.loop()
        if key == KEY_ENTER:
            return self.items[0]
        return None


class Viewer(WEditor):

    def handle_key(self, key):
        if key in (KEY_ENTER, KEY_ESC):
            return key
        try:
            if super().handle_cursor_keys(key):return True #MP
        except:
            if Editor.handle_cursor_keys(self,key):return True
        return None


# Viewer with colored lines, (whole line same color)
class LineColorViewer(Viewer):

    def show_line(self, l, i):
        if self.is_dict_color:
            c = self.lines_c.get(i, self.def_c)
        else:
            try:
                c = self.lines_c[i]
            except IndexError:
                c = self.def_c
        self.attr_color(c)
        try:super().show_line(l, i)
        except:Viewer.show_line(self,l, i)
        self.attr_reset()

    def set_line_colors(self, default_color, color_list={}):
        self.def_c = default_color
        self.lines_c = color_list
        self.is_dict_color = isinstance(color_list, dict)


# Viewer with color support, (echo line may consist of spans
# of different colors)
class CharColorViewer(Viewer):

    def show_line(self, l, i):
        # TODO: handle self.margin, self.width
        length = 0
        for span in l:
            if isinstance(span, tuple):
                span, c = span
            else:
                c = self.def_c
            self.attr_color(c)
            self.wr(span)
            length += len(span)
        self.attr_color(self.def_c)
        self.clear_num_pos(self.width - length)
        self.attr_reset()

    def set_def_color(self, default_color):
        self.def_c = default_color


class EditorExt(WEditor):

    screen_width = 80

    def setup(self,text='EditorExt', width=80, height=24, x=0, y=0, z=0, **kw):
        WEditor.setup(self,text=text, width=width, height=height, x=x, y=y, z=0 , **kw  )
        # +1 assumes there's a border around editor pane
        self.status_y = y + height + 1

    def get_text(self):
        if self.choice>=0 and self.choice<self.items_count:
            return self.items[self.choice]
        return None

    def set_text(self,text=''):
        self.items[self.choice] = text
        self.dirty=True
        return self.dirty

    def line_visible(self, no):
        return self.top_line <= no < self.top_line + self.height

    # If line "no" is already on screen, just reposition cursor to it and
    # return False. Otherwise, show needed line either at the center of
    # screen or at the top, and return True.
    def goto_line(self, no, col=None, center=True):
        self.choice = no

        if self.line_visible(no):
            self.row = no - self.top_line
            if col is not None:
                self.col = col
                if self.adjust_cursor_eol():
                    self.redraw()
            self.set_cursor()
            return False

        if center:
            c = self.height // 2
            if no > c:
                self.top_line = no - c
                self.row = c
            else:
                self.top_line = 0
                self.row = no
        else:
            self.top_line = no
            self.row = 0

        if col is not None:
            self.col = col
            self.adjust_cursor_eol()
        self.redraw()
        return True

    def show_status(self, msg):
        self.cursor(False)
        self.goto(0, self.status_y)
        self.wr(msg)
        self.clear_to_eol()
        self.set_cursor()
        self.cursor(True)

    def show_cursor_status(self):
        self.cursor(False)
        self.goto(0, 31)
        self.wr("% 3d:% 3d" % (self.choice, self.col + self.margin))
        self.set_cursor()
        self.cursor(True)

    def dialog_edit_line(self, left=None, top=8, width=40, height=3, line="", title=""):
        if left is None:
            left = (self.screen_width - width) / 2
        self.dialog_box(left, top, width, height, title)
        e = LineEditor(left + 1, top + 1, width - 2, height - 2)
        return e.edit(line)

