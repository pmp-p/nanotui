#
# Simple VT100 terminal text editor widget
# Copyright (c) 2015 Paul Sokolovsky
# Distributed under MIT License
#

from .screen import *
from .basewidget import Widget


class WEditor(Widget):

    def setup(self,text="Dialog", width=80, height=25, x=1, y=1, z=0,**kw):
        self.top_line = 0
        self.choice = 0
        self.row = 0
        self.col = 0
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.margin = 0

    def set_cursor(self):
        self.goto(self.col + self.x, self.row + self.y)
        self.cursor(True)

    def adjust_cursor_eol(self):
        # Returns True if entire window needs redraw
        val = 0
        if self.items:
            val = self.col + self.margin
            val = min(val, len(self.items[self.choice]))
        if val > self.width - 1:
            self.margin = val - (self.width - 1)
            self.col = self.width - 1
            return True
        else:
            self.col = val - self.margin
            return False

    def set_lines(self, lines):
        self.items = lines
        self.items_count = len(lines)

    def redraw(self):
        self.cursor(False)
        i = self.top_line
        r = self.y
        for c in range(self.height):
            self.goto(self.x, r)
            if i == self.items_count:
                self.show_line("", -1)
            else:
                self.show_line(self.items[i], i)
                i += 1
            r += 1
        self.set_cursor()

    def update_line(self):
        self.cursor(False)
        self.goto(self.x, self.row + self.y)
        self.show_line(self.items[self.choice], self.choice)
        self.set_cursor()

    def show_line(self, l, i):
        l = l[self.margin:]
        l = l[:self.width]
        self.wr(l)
        self.clear_num_pos(self.width - len(l))

    def next_line(self):
        if self.row + 1 == self.height:
            self.top_line += 1
            return True
            self.redraw()
        else:
            self.row += 1
            return False
            self.set_cursor()

    def handle_cursor_keys(self, key):
        if not self.items_count:
            return
        if key == KEY_DOWN:
            if self.choice + 1 != self.items_count:
                self.choice += 1
                redraw = self.adjust_cursor_eol()
                if self.next_line() or redraw:
                    self.redraw()
                else:
                    self.set_cursor()
        elif key == KEY_UP:
            if self.choice > 0:
                self.choice -= 1
                redraw = self.adjust_cursor_eol()
                if self.row == 0:
                    if self.top_line > 0:
                        self.top_line -= 1
                        self.redraw()
                else:
                    self.row -= 1
                    if redraw:
                        self.redraw()
                    else:
                        self.set_cursor()
        elif key == KEY_LEFT:
            if self.col > 0:
                self.col -= 1
                self.set_cursor()
            elif self.margin > 0:
                self.margin -= 1
                self.redraw()
        elif key == KEY_RIGHT:
            self.col += 1
            if self.adjust_cursor_eol():
                self.redraw()
            else:
                self.set_cursor()
        elif key == KEY_HOME:
            self.col = 0
            if self.margin > 0:
                self.margin = 0
                self.redraw()
            else:
                self.set_cursor()
        elif key == KEY_END:
            self.col = len(self.items[self.choice])
            if self.adjust_cursor_eol():
                self.redraw()
            else:
                self.set_cursor()
        elif key == KEY_PGUP:
            self.choice -= self.height
            self.top_line -= self.height
            if self.top_line < 0:
                self.top_line = 0
                self.choice = 0
                self.row = 0
            elif self.choice < 0:
                self.choice = 0
                self.row = 0
            self.adjust_cursor_eol()
            self.redraw()
        elif key == KEY_PGDN:
            self.choice += self.height
            self.top_line += self.height
            if self.choice >= self.items_count:
                self.top_line = self.items_count - self.height
                self.choice = self.items_count - 1
                if self.top_line >= 0:
                    self.row = self.height - 1
                else:
                    self.top_line = 0
                    self.row = self.choice
            self.adjust_cursor_eol()
            self.redraw()
        else:
            return False
        return True

    def handle_mouse(self, col, row):
        row -= self.y
        col -= self.x
        if 0 <= row < self.height and 0 <= col < self.width:
            choice = self.top_line + row
            if choice < self.items_count:
                self.row = row
                self.col = col
                self.choice = choice
                self.adjust_cursor_eol()
                self.set_cursor()
                return True

    def handle_key(self, key):
        if key == KEY_QUIT:
            return key
        if self.handle_cursor_keys(key):
            return
        return self.handle_edit_key(key)

    def handle_edit_key(self, key):
            l = self.items[self.choice]
            if key == KEY_ENTER:
                self.items[self.choice] = l[:self.col + self.margin]
                self.choice += 1
                self.items[self.choice:self.choice] = [l[self.col + self.margin:]]
                self.items_count += 1
                self.col = 0
                self.margin = 0
                self.next_line()
                self.redraw()
            elif key == KEY_BACKSPACE:
                if self.col + self.margin:
                    if self.col:
                        self.col -= 1
                    else:
                        self.margin -= 1
                    l = l[:self.col + self.margin] + l[self.col + self.margin + 1:]
                    self.items[self.choice] = l
                    self.update_line()
            elif key == KEY_DELETE:
                l = l[:self.col + self.margin] + l[self.col + self.margin + 1:]
                self.items[self.choice] = l
                self.update_line()
            else:
                try:
                    l = l[:self.col + self.margin] + str(key, "utf-8") + l[self.col + self.margin:]
                except:
                    l = 'error'
                self.items[self.choice] = l
                self.col += 1
                self.adjust_cursor_eol()
                self.update_line()


