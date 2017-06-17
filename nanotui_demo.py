#!python3 -u -B
import sys
import nanotui
import nanotui.events as events
import time



with nanotui.VisualPage( 'demo' ,"nanotui demo",80, 25) as add:
    try:
        def stepper(*argv,**kw):
            y,my,d,h,m,s = time.localtime( Time.time() )[:6]
            clk = '%s%c%s%c%s'  % ( zfill(h,2),':',zfill(m,2),':',zfill(s,2) )
            Time.sleep(.1)
            status(clk)
            choice.set_text( '%-4s : "%s"' % ( str(lb.choice),lb.get_text() ) )



        last=add('lbl','Label', text=" ---------- Label --------------")

        status =add.anchor(" ----------- Label -------------",dy=-3)


        last=add(None,'Label',text='Size:',x=4)
        p1 = add('p1','InputField',text='4096',y=last.y-1) #,x=4)

        choice =add('choice','Label',text=" selection : %s",x=2)#,y=status.y+2 )

        last= lb =  add('units','ListBox',items="1 2 3 4".split(' '),width=51,height=6,x=3,y=last.y+last.height+4 )
        add(None,'Frame',text="Listbox Frame :",x=last.x-2,y=last.y-2,width=last.width+2,height=last.height+4)


        last = add('cancel','Button', text="Abort", width=8,x=60,y=22)
        last.finish_dialog = events.ACTION_CANCEL


        add.handler = stepper


    except Exception as e:
        add.End(error=e)

print('dlg code =', nanotui.ec['demo'] )
