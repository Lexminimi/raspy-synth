import sys
import os
import math
import time
import RPi.GPIO as IO
from queue import Queue 
from threading import Thread 

import pygame as pg
import pygame.midi

IO.setwarnings(False)           
IO.setmode (IO.BCM)         
IO.setup(19,IO.OUT)

_sentinel=object()

def print_device_info():
    pygame.midi.init()
    _print_device_info()
    pygame.midi.quit()

def _print_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print(
            "%2i: interface :%s:, name :%s:, opened :%s:  %s"
            % (i, interf, name, opened, in_out)
        )

def modulate_freq(out_q):
    print("modulalo++++++")
    #p.ChangeFrequency(out_q.get())
    data=out_q.get()
    count=0
    freq_new=data
    dutyc=data # A jelenlegi kitoltesi tenyezo
    x=0
    while True:
        #print("Queaban: ",data)
        new_dutyc=math.sin(x)*45+50
        p.ChangeDutyCycle(new_dutyc)
        print("Duty Cycle: ---------- ",new_dutyc ," %")
        time.sleep(0.0005)
        if x>362:
            x=0
        else:
            x=x+1
       # if not(out_q.empty()):
        #    dutyc=out_q.get()


def input_main(device_id, in_q):
    
    pg.init()
    pg.fastevent.init()
    #print("MAIN elkezdodott!!!")
    event_get = pg.fastevent.get
    event_post = pg.fastevent.post

    pygame.midi.init()
    _print_device_info()

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id

    #print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    pg.display.set_mode((1, 1))
    
    lastkey=0;
    going = True
    while going:
        events = event_get()
        
        for e in events:
        
            if e.type in [pg.QUIT]:
                going = False
            if e.type in [pg.KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:
     #           print(pygame.midi.midi_to_ansi_note(e.data1))
                freq=pygame.midi.midi_to_frequency(e.data1)
                p.ChangeFrequency(freq)
                if e.data2!=0:
                    p.start(50)
                    in_q.put(freq)
                 #p.start(50)
                    
               # if e.data2==0:
                    
                #    p.stop()
                
                
        if i.poll():
            midi_events = i.read(10)
            # convert them into pygame events.
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post(m_e)
                #print(m_e.event_name())
                if m_e.data2==0:
                    p.stop()
                    in_q.put(0)
                    
                    

                   # modulate_thread.join()    

    del i
    pygame.midi.quit()
q = Queue()
p = IO.PWM(19,440)
main_thread=Thread(target=input_main, args=(3,q, ))
modulate_thread=Thread(target=modulate_freq, args=(q, ))
print("main inditad elott....")
main_thread.start()
modulate_thread.start()
