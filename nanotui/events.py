# Standard widget result actions (as return from .loop())
ACTION_OK = 1000
ACTION_CANCEL = 1001
ACTION_NEXT = 1002
ACTION_PREV = 1003

#ACTION_events = 2000

#order matters eg: mouseover / mouseout , mousedown mouseup
class ev:
    @classmethod
    def _from_code(cls,evcode):
        for key in dir(ev):
            if key[0]!='_':
                tev = getattr(ev,key)
                if tev[0]==evcode:
                    return tev
    @classmethod
    def _from_name(cls,evname):
        evname = evname.lower()
        for key in dir(ev):
            if key[0]!='_':
                tev = getattr(ev,key)
                if tev[1]==evname:
                    return tev

    click = [2100,'click']




class Event:
    def __init__(self,e=None,ec=None,en=None,**kw):
        if e is None:
            if ec:
                e = ev._from_code(ec)
            if en:
                e = ev._from_code(en)
        self.key, self.type = e
        for key in list(kw):
            setattr(self,key,kw.pop(key))

