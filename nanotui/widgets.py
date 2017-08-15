from .basewidget import *


from .editor import *
from .editorext import * # LineEditor(WEditor)
from . import symbols

import nanotui.colors

evq = []

def cn(o):return o.__class__.__name__

class Dialog(Widget):


    color = nanotui.colors.Color

    finish_on_esc = True

    def setup(self,text="Dialog", width=80, height=25, x=1, y=1, z=0,**kw):
        self.text = " %s " % text

        # On both sides
        self.border_w = 2
        self.border_h = 2
        self.focus_w = None
        self.focus_idx = -1




    def xy_add(self, x, y, widget):
        if isinstance(widget, str):
            # Convert raw string to WLabel
            widget = WLabel(widget)
        widget.set_xy(self.x + x, self.y + y)
        widget.owner = self
        return widget


    def autosize(self, extra_w=0, extra_h=0):
        return

        w = 0
        h = 0
        for np in self.np.children:
            wid = np.node
            w = max(w, wid.x - self.x + wid.width)
            h = max(h, wid.y - self.y + wid.height)
        self.width = max(self.width, w + self.border_w - 1) + extra_w
        self.height = max(self.height, h + self.border_h - 1) + extra_h


    def draw_children(self,parent,indent=''):
        for np in parent.np.children:
            child = np.node

            #print(indent, cn(parent),cn(child),file=sys.stderr)
            try:
                child.redraw()
                child.dirty=False
                self.draw_children( child, indent+'    ' )
            except Exception as e:
                warn('65:', e, self)

    def redraw(self):
        # Init some state on first redraw
        if self.focus_idx == -1:
            try:
                self.autosize()
            except Exception as e:
                print( e,self )
            self.focus_idx, self.focus_w = self.find_focusable_by_idx(0, 1)
            if self.focus_w:
                self.focus_w.focus = True

        # Redraw widgets with cursor off
        self.cursor(False)
        self.dialog_box(self.x, self.y, self.width, self.height, self.text)
        doit = False

        self.draw_children(self)

        self.dirty = False
        # Then give widget in focus a chance to enable cursor
        if self.focus_w:
            self.focus_w.set_cursor()

    def find_focusable_by_idx(self, from_idx, direction):
        sz = len(self.np.children)
        while 0 <= from_idx < sz:
            if self.np.children[from_idx].node.focusable:
                return from_idx, self.np.children[from_idx].node
            from_idx = (from_idx + direction) % sz
        return None, None

    def find_focusable_by_xy(self, x, y):
        i = 0
        for np in self.np.children:
            w= np.node
            if w.focusable and w.inside(x, y):
                return i, w
            i += 1
        return None, None

    def set_focus(self, widget):
        if widget is self.focus_w:
            return
        if self.focus_w:
            self.focus_w.focus = False
            self.focus_w.redraw()
        self.focus_w = widget
        widget.focus = True
        widget.redraw()
        widget.set_cursor()

    def move_focus(self, direction):

        prev_idx = ( (self.focus_idx or 0) + direction) % len(self.np.children)
        self.focus_idx, new_w = self.find_focusable_by_idx(prev_idx, direction)
        self.set_focus(new_w)

    def handle_key(self, key):
        if key == KEY_QUIT:
            return key
        if key == KEY_ESC and self.finish_on_esc:
            return ACTION_CANCEL
        if key == KEY_TAB:
            self.move_focus(1)
        elif key == KEY_SHIFT_TAB:
            self.move_focus(-1)
        elif self.focus_w:
            if key == KEY_ENTER:
                if self.focus_w.finish_dialog is not False:
                    return self.focus_w.finish_dialog
            res = self.focus_w.handle_key(key)
            if res == ACTION_PREV:
                self.move_focus(-1)
            elif res == ACTION_NEXT:
                self.move_focus(1)
            else:
                return res

    def handle_mouse(self, x, y):
        # Work in absolute coordinates
        if self.inside(x, y):
            self.focus_idx, w = self.find_focusable_by_xy(x, y)
#            print(w)
            if w:
                self.set_focus(w)
                return w.handle_mouse(x, y)


class WLabel(Widget):

    SIZE = [8,1,60,1]

    def setup(self, text='', width=0, height=0, **kw ):

        self.height = height or 1

        if text[-1]==']':
            self.width = len(text)
            text=text[:-1].strip()
        else:
            self.width = width or len(text)
        self.text = text


    def redraw(self):
        self.goto(self.x, self.y)
        self.wr(self.text)


class WButton(Widget):

    focusable = True

    SIZE = [4,1,16,1]


    def setup(self, text='WButton', width=0, height=1, **kw):
        self.text = text
        self.height = 1 #height
        self.width = width or len(text) + 2
        self.disabled = False
        self.focus = False

        self.finish_dialog = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.disabled:
            self.attr_color(self.color.WHITE, self.color.GRAY)
        else:
            if self.focus:
                self.attr_color(self.color.B_WHITE, self.color.GREEN)
            else:
                self.attr_color(self.color.BLACK, self.color.GREEN)
        self.wr(self.text.center(self.width))
        self.attr_reset()

    def handle_mouse(self, x, y):
        if not self.disabled:
            if self.finish_dialog is not False:
                return self.finish_dialog
            else:
                self.on_click()

    def handle_key(self, key):
        if key == KEY_UP or key == KEY_LEFT:
            return ACTION_PREV
        if key == KEY_DOWN or key == KEY_RIGHT:
            return ACTION_NEXT
        # For dialog buttons (.finish_dialog=True), KEY_ENTER won't
        # reach here.
        if key == KEY_ENTER:
            self.on_click()

    def on_click(self):
        try:
            save = builtins.window
        except:
            save= RunTime.unset

        builtins.window = NodePath.factory

        e = Event( e = ev.click, target = self, srcElement = self )
        builtins.window.event = e

        ec = e.key
        if ec in self.signals:
            for fn in self.signals[ec]:
                fn(e)
        else:
            en = 'on%s' % e.type
            for mod in NodePath.factory.modules:
                if hasattr(mod, en):
                    getattr(mod,en)(e)
                    break
            else:
                warn(self,'on_click', 'default_handler' )
        if save is RunTime.unset:
            del builtins.window
            return

        builtins.window = save
        #TODO: buble


class WFrame(Widget):

    SIZE = [16,3,0,0]

    def setup(self, text="WFrame", width=0,height=0, **kw):
        if text[-1]==']':
            self.width = len(text)
            text=text[:-1].strip()
        else:
            self.width = width
        self.height = height
        self.set_text(text)

    def redraw(self):
        self.draw_box(self.x, self.y, self.width, self.height)
        if self.text:
            pos = 1
            self.goto(self.x + pos, self.y)
            self.wr(" %s " % self.text)


class WCheckbox(Widget):

    focusable = True

    def setup(self, text='checkbox', state=False):
        self.text = text
        self.height = 1
        self.width = 4 + len(text)
        self.state = state
        self.focus = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(self.color.B_BLUE, None)
        self.wr("[x] " if self.state else "[ ] ")
        self.wr(self.text)
        self.attr_reset()

    def flip(self):
        self.state = not self.state
        self.redraw()
        self.signal("changed")

    def handle_mouse(self, x, y):
        self.flip()

    def handle_key(self, key):
        if key == KEY_UP:
            return ACTION_PREV
        if key == KEY_DOWN:
            return ACTION_NEXT
        if key == b" ":
            self.flip()


class WRadioButton(Widget):

    focusable = True

    def __init__(self, items=[]):
        self.items = items
        self.choice = 0
        self.height = len(items)
        self.width = 4 + self.longest(items)
        self.focus = False

    def redraw(self):
        i = 0
        if self.focus:
            self.attr_color(self.color.B_BLUE, None)
        for t in self.items:
            self.goto(self.x, self.y + i)
            self.wr("(*) " if self.choice == i else "( ) ")
            self.wr(t)
            i += 1
        self.attr_reset()

    def handle_mouse(self, x, y):
        self.choice = y - self.y
        self.redraw()

    def handle_key(self, key):
        if key == KEY_UP:
            return ACTION_PREV
        if key == KEY_DOWN:
            return ACTION_NEXT


class WListBox(EditorExt):

    focusable = True

    def setup(self, items=[],width=0,height=0,**kw):
        EditorExt.setup(self, width=width,height=height,**kw)
        self.set_items( items )
        self.choice = 0
        self.width = width or max( map(len,items) )
        self.height = height or len(items)
        self.set_lines(items)
        self.focus = False

    def render_line(self, l):
        # Default identity implementation is suitable for
        # items being list of strings.
        return l

    def show_line(self, l, i):
        hlite = self.choice == i
        if hlite:
            if self.focus:
                self.attr_color(self.color.B_WHITE, self.color.GREEN)
            else:
                self.attr_color(self.color.BLACK, self.color.GREEN)
        if i != -1:
            l = self.render_line(l)[:self.width]
            self.wr(l)
        self.clear_num_pos(self.width - len(l))
        if hlite:
            self.attr_reset()

    def handle_mouse(self, x, y):
        try:res = super().handle_mouse(x, y)
        except:res = EditorExt.handle_mouse(self,x, y)
        self.redraw()
        return res

    def handle_key(self, key):
        try:res = super().handle_key(key)
        except:res = EditorExt.handle_key(self,key)
        self.redraw()
        return res

    def handle_edit_key(self, key):
        pass

    def set_cursor(self):
        Widget.set_cursor(self)

    def cursor(self, state):
        # Force off
        try:super().cursor(False)
        except:EditorExt.cursor(self,False)

    def set_text(text='',idx=-1):
        if idx <0 :
            idx = self.choice
        if text!=self.items[self.choice]:
            self.items[idx]= text
            self.dirty
            return True

    def clear(self):
        self.items = []
        self.items_count = 0
        self.choice = None
        self.dirty=True

    #TODO: preselection
    def set_items(self,items):
        self.items = items
        self.items_count = len( self.items )
        self.choice=0
        self.dirty = True
        return self.dirty



class WPopupList(Dialog):

    class OneShotList(WListBox):

        def handle_key(self, key):
            if key == KEY_ENTER:
                return ACTION_OK
            if key == KEY_ESC:
                return ACTION_CANCEL
            try:return super().handle_key(key) #MP
            except:return WListBox.handle_key(self,key)

        def handle_mouse(self, x, y):
            try:
                if super().handle_mouse(x, y) == True:return ACTION_OK #MP
            except:
                if WListBox.handle_mouse(self,x,y):return ACTION_OK

    def __init__(self, x, y, width, height, items):
        try:super().__init__(x, y, width, height)
        except:Dialog.__init__(self,x, y, width, height)
        self.list = self.OneShotList(width - 2, height - 2, items)
        self.add(1, 1, self.list)

    def handle_mouse(self, x, y):
        if not self.inside(x, y):
            return ACTION_CANCEL
        try:return super().handle_mouse(x, y)
        except:return Dialog.handle_mouse(self,x, y)

    def get_choice(self):
        return self.list.choice

    def get_selected_value(self):
        if not self.list.content:
            return None
        return self.list.content[self.list.choice]


class WDropDown(Widget):

    focusable = True

    def __init__(self, items=[],width=8):
        self.items = items
        self.choice = 0
        self.height = 1
        self.width = width
        self.focus = False

    def redraw(self):
        self.goto(self.x, self.y)
        if self.focus:
            self.attr_color(self.color.B_WHITE, self.color.CYAN)
        else:
            self.attr_color(self.color.BLACK, self.color.CYAN)
        self.wr_fixedw(self.items[self.choice], self.width - 2)
        self.wr(" v")
        self.attr_reset()

    def handle_mouse(self, x, y):
        popup = WPopupList(self.x, self.y + 1, self.width, 5, self.items)
        res = popup.loop()
        if res == ACTION_OK:
            self.choice = popup.get_choice()
        self.owner.redraw()

    def handle_key(self, key):
        self.handle_mouse(0, 0)


class WInputField(EditorExt):

    focusable = True

    SIZE = [8,1,60,1]


    def setup(self, text='InputField',width=8, height=0,**kw):
        EditorExt.setup(self,text='InputField',width=width, height=height, **kw)
        self.height = height or self.SIZE[1]
        self.width = width or self.SIZE[0]
        self.focus = False
        self.set_text(text)
        self.adjust_cursor_eol()
        self.just_started = True
        self.evq = evq

    def set_text(self, text):
        self.text = text
        self.set_lines([text])
        self.col = len(text)
        self.dirty = True


    def handle_cursor_keys(self, key):
        try:cond=super().handle_cursor_keys(key)#MP
        except:cond=EditorExt.handle_cursor_keys(self, key)
        if cond:
            if self.just_started:
                self.just_started = False
                self.redraw()
            return True
        return False

    def handle_edit_key(self, key):
        if key == KEY_ENTER:
            # Don't treat as editing key
            self.evq.append( self.get_text() )
            return True
        if self.just_started:
            if key != KEY_BACKSPACE:
                # Overwrite initial string with new content
                self.set_lines([""])
                self.col = 0
            self.just_started = False

        try:return super().handle_edit_key(key) #MP
        except:EditorExt.handle_edit_key(self, key)

    def handle_mouse(self, x, y):
        if self.just_started:
            self.just_started = False
            self.redraw()
        try:super().handle_mouse(x, y) #MP
        except:EditorExt.handle_mouse(self, x, y)

    def show_line(self, l, i):
        if self.just_started:
            fg = self.color.WHITE
        else:
            fg = self.color.BLACK
        self.attr_color(fg, self.color.CYAN)
        try:super().show_line(l, i)
        except:EditorExt.show_line(self, l, i)
        self.attr_reset()


class WMultiEntry(EditorExt):

    focusable = True

    def setup(self,items='MultiEntry',width=0,height=0, **kw):
        try:super().__init__(width=width, height=height)
        except:EditorExt.__init__(self,width=width, height=height)
        self.height = height
        self.width = width
        self.focus = False
        self.set_lines(items)
        self.choice = 0

    def show_line(self, l, i):
        self.attr_color(self.color.BLACK, self.color.CYAN)
        try:super().show_line(l, i)
        except:EditorExt.show_line(self, l, i)
        self.attr_reset()


class WComboBox(WInputField):

    popup_class = WPopupList
    popup_h = 5

    def setup(self, text='ComboBox', items=[],width=0,**kw):
        # w - 1 width goes to Editor widget
        # We have full requested width, will show arrow symbol as last char
        self.width = width
        self.items = items

    def redraw(self):
        self.goto(self.x + self.width - 1, self.y)
        self.wr(symbols.DOWN_ARROW)
        try:super().redraw()
        except:WInputField.redraw(self)

    def get_choices(self, substr):
        return self.items

    def show_popup(self):
        choices = self.get_choices(self.get_text())
        popup = self.popup_class(self.x, self.y + 1, self.longest(choices) + 2, self.popup_h, choices)
        popup.main_widget = self
        res = popup.loop()
        if res == ACTION_OK:
            val = popup.get_selected_value()
            if val is not None:
                self.set_lines([val])
                self.col = sys.maxsize
                self.adjust_cursor_eol()
                self.just_started = False
        self.owner.redraw()

    def handle_key(self, key):
        if key == KEY_DOWN:
            self.show_popup()
        else:
            try:return super().handle_key(key)
            except:return WInputField.handle_key(self, key)

    def handle_mouse(self, x, y):
        if x == self.x + self.width - 1:
            self.show_popup()
        else:
            try:super().handle_mouse(x, y)
            except:WInputField.handle_mouse(self, x, y)


class WCompletionList(WPopupList):

    def __init__(self, x, y, w, h, items):
        Dialog.__init__(self, x, y, w, h)
        self.list = self.OneShotList(w - 2, h - 2, items)
        self.add(1, 1, self.list)
        chk = WCheckbox("Prefix")
        def is_prefix_changed(wid):
            main = self.main_widget
            choices = main.get_choices(main.get_text(), wid.state)
            self.list.set_lines(choices)
            self.list.top_line = 0
            self.list.choice = 0
            self.list.row = 0
            self.list.redraw()
        chk.on("changed", is_prefix_changed)
        self.add(1, h - 1, chk)


class WAutoComplete(WComboBox):

    popup_class = WCompletionList

    def get_choices(self, substr, only_prefix=False):
        substr = substr.lower()
        if only_prefix:
            choices = list(filter(lambda x: x.lower().startswith(substr), self.items))
        else:
            choices = list(filter(lambda x: substr in x.lower(), self.items))
        return choices




#
