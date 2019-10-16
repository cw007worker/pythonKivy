from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.lang import Builder
import re
import subprocess
from sys import platform
import datetime
Builder.load_file('k.kv')
def write_params(params):
    fh = open('my_curl.txt', 'r')
    curlcmd = fh.readline()
    fh.close()
    replace_params= "\\1" + params + "\\2"    
    curlnew = re.sub(r'(.*B_PARAMS=)\S+( -H.*)', replace_params ,curlcmd)
    fh = open('params.txt', 'w')
    fh.write(curlnew)
    fh.close()
    
def buildDispatch(product,params):
    vars = ["MODE=","TAG_FW=","BRANCH_FW=","TAG_DT=","BRANCH_DT="]    
    paramsText = 'PRODUCT='+product
    buttonText = paramsText
    for textInput in params: #index the corresponding vars
        paramsText += ','+ vars[params.index(textInput)]+textInput.text
        buttonText += ',\n' + vars[params.index(textInput)]+textInput.text
    write_params(paramsText)
    btnParams= Button(text=buttonText)
    btnParams.textsize = (50,30)
    pop=Popup(content=btnParams, title='Dispatching Build!')
    pop.open()
    btnParams.bind(on_press=pop.dismiss)
    # Dispatch curl command
    fh = open('params.txt', 'r')
    curlcmd = fh.readline().rstrip() #remove trailing newline
    fh.close()
    curlList = curlcmd.split(' ')
    try:# for Ubuntu send the curlcmd string not the curlList which is for DOS
        if platform == "linux" or platform == "linux2":
            subprocess.run(curlcmd, shell=True, check=True)
        elif platform == "win32":
            subprocess.run(curlList, shell=True, check=True)
    except subprocess.CalledProcessError as err:
        print('Error: ',err)
        return err


class BuildRequester(BoxLayout):
    chkref = {}
    def on_checkbox_active(self,chkbox,value):
        if value:
            self.ids.label2.text = 'Selected ' + self.chkref[chkbox]
            self.product = self.chkref[chkbox]
        else:
            self.ids.label2.text = 'Not Selected'
            self.product = None
    def cancel(self):
        for ckey in self.chkref:
            ckey.active = False
        self.ids.label2.text = 'Not Selected'            
    def buildParams(self):
        pinpts=[self.ids.mode_inpt,
                self.ids.fw_tag_inpt,
                self.ids.fw_branch_inpt,
                self.ids.dt_tag_inpt,
                self.ids.dt_branch_inpt]
            
        for ckey in self.chkref:
            if ckey.active:
                self.ids.label2.text = 'Build Mode'+self.ids.mode_inpt.text

                buildDispatch(self.product,pinpts)
                return
        self.ids.label2.text = 'Select Product !!!'
    def set_textinputs(self):
        today=datetime.datetime.today().strftime('%Y_%m_%d')
        dt_today='dt_'+today
        fw_today='fw_'+today
        self.ids.mode_inpt.text = '1'
        self.ids.fw_tag_inpt.text = fw_today
        self.ids.fw_branch_inpt.text = 'master'
        self.ids.dt_tag_inpt.text = dt_today
        self.ids.dt_branch_inpt.text = 'master'
        
    def __init__(self, **kwargs):
        super(BuildRequester,self).__init__(**kwargs)

        right = GridLayout(cols = 2)

        prods = [ 'P_200','P_008_z','P_007_y','P_003_x']
        texts = ['2','fw_2018_02_05','mybranch','dt_2018_02_08','mybranch']
        self.txts = []
        for t in texts:
            self.txts.append(TextInput(multiline=False, font_size=10, text=t))
        self.set_textinputs()
        for i in range(len(prods)):
            right.add_widget(Label(text=prods[i],italic=True,bold=True,color=[0,1,1,4]))
            chkbox = CheckBox(group='1',color=[0.5,5,0,4])
            chkbox.bind(active=self.on_checkbox_active)
            right.add_widget( chkbox)
            self.chkref[chkbox]= prods[i]
        self.add_widget(right)

class MainApp(App):
    def build(self):
        self.title = 'Build Requester'
        root = BuildRequester()
        return root

if __name__ == '__main__':
    app = MainApp()
    app.run()
