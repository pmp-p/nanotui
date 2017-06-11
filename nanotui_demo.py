#!python3 -u -B
import sys
import nanotui
import nanotui.events as events
import time


def zfill(i,places,char='0'):
    i=str(i)
    if len(i)<places:  i = '%s%s' % (  char * ( places-len(i) ) , i )
    return i

with nanotui.VisualPage( 'demo' ,"nanotui demo",80, 25) as add:
    try:
        def stepper(*argv,**kw):
            y,my,d,h,m,s = time.localtime( Time.time() )[:6]
            clk = '%s%c%s%c%s'  % ( zfill(h,2),':',zfill(m,2),':',zfill(s,2) )
            Time.sleep(.1)
            status(clk)



        last=add('lbl','Label', text=" ---------- Label --------------")

        status =add.anchor(" ----------- Label -------------",dy=-3)

        last= add('units','ListBox',items="1 2 3 4".split(' '),width=51,height=6,x=3,y=last.y+last.height+4 )
        add(None,'Frame',text="Listbox Frame :",x=last.x-2,y=last.y-2,width=last.width+2,height=last.height+4)


        last = add('cancel','Button', text="Abort", width=8,x=60,y=22)
        last.finish_dialog = events.ACTION_CANCEL


        add.handler = stepper


    except Exception as e:
        add.End(error=e)

print('dlg code =', nanotui.ec['demo'] )
