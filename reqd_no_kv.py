#!/usr/bin/python3
from kivy.app import App

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

import re
import subprocess

def write_params(text):
    params = ""
    for line in text:
        if line != "":
            params += line+','
    fh = open('my_curl.txt', 'r')
    curlcmd = fh.readline()
    fh.close()
    replace_params= "\\1" + params[:-1] + "\\2"    
    curlnew = re.sub(r'(.*B_PARAMS=)\S+( -H.*)', replace_params ,curlcmd)
    fh = open('params.txt', 'w')
    fh.write(curlnew)
    fh.close()

def buildParams(t1,t2,t3,t4):
    write_params([t1,t2,t3,t4])
    btn3=Button(text='Request Build!')
    pop=Popup(content=btn3, title='Confirm Request Build!')
    pop.open()
    btn3.bind(on_press=pop.dismiss)

    # Dispatch curl command
    fh = open('params.txt', 'r')
    curlcmd = fh.readline()
    fh.close()

    #try:
    print(' ', curlcmd)
    #subprocess.run([curlcmd], shell=True, check=True)

    #except subprocess.CalledProcessError as err:
    #print('Error: ',err)
    #    return err


class BuildUserApp(App):
        
    def cancel(self,t1,t2,t3,t4): # restore defaults
        self.txt1.text = t1
        self.txt2.text = t2        
        self.txt3.text = t3
        self.txt4.txt = t4
    def build(self):
        root_widget = BoxLayout(orientation = "vertical")

        root_widget.rows=5
        root_widget.cancelled = False
        # -- Create labels
        v1="PRODUCT="
        v2="MODE="
        v3="TAG_FW="
        v4="BRANCH_FW="
        lbl1 = Label(text=v1, italic=True, bold=True)
        lbl2 = Label(text=v2, italic=True, bold=True)
        lbl3 = Label(text=v3, italic=True, bold=True)
        lbl4 = Label(text=v4, italic=True, bold=True)        
        # -- Here we are creating text inputs
        self.t1 = "P_007_x"
        self.t2 = '2'
        self.t3 = 'tag_fw'
        self.t4 = 'mybranch'        
        self.txt1 = TextInput(multiline=False, font_size=20, text= self.t1)
        self.txt2 = TextInput(multiline=False, font_size=20, text= self.t2)
        self.txt3 = TextInput(multiline=False, font_size=20, text = self.t3)
        self.txt4 = TextInput(multiline=False, font_size=20, text = self.t4)
        # -- Here we create buttons and their bindings
        btn1 = Button(text="BuildIt", bold=True)
        btn2 = Button(text="Cancel", bold=True)
        btn1.bind(on_press=lambda *a:buildParams(
            v1+self.txt1.text,v2+self.txt2.text,v3+self.txt3.text,v4+self.txt4.text))
        btn2.bind(on_press=lambda *a:self.cancel(self.t1,self.t2,self.t3,self.t4))
        # Here we add it to root_widget tree.  If you skip this step,
        # you'll never see your precious widget.
        root_widget.add_widget(lbl1)
        root_widget.add_widget(self.txt1)        
        root_widget.add_widget(lbl2)
        root_widget.add_widget(self.txt2)
        root_widget.add_widget(lbl3)
        root_widget.add_widget(self.txt3)        
        root_widget.add_widget(lbl4)
        root_widget.add_widget(self.txt4)        
        
        root_widget.add_widget(btn1)
        root_widget.add_widget(btn2)                        
            
        return root_widget

BuildUserApp().run()
