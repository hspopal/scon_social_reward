#    ###################################NOTES##########################################
#    This script looks at social learning between learning from a computer, or a peer.
#    It was converted from Matlab Pscyhtoolbox to Psychopy in July, 2018.
#    Rewrittern for teens in 2022. 
#
#    If you have an error with COM or PORT, and the button box is not working, it may be that the scanner_coms 
#    port number has changed. Thris sometimes happens, and the MNC is usually aware of it. You will need to change
#    the port number, as of 8/2/18 it is set to port=2
#
#                                ###DOCUMENTATION###
#    As of 11/16/21, the preFixDur is set to 5 seconds, while the postFixDur is set to 5 seconds.
#    Change "COM3" for real scanner and "COM4" for mock   
#
#    
#    #################################################################################
from __future__ import absolute_import, division
from psychopy import visual, gui, core, event, useVersion
from psychopy.tools.filetools import fromFile, toFile
import numpy as np  # whole numpy lib is available, prepend 'np.'
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import pandas as pd
import os, sys, time, random, csv, unicodedata, platform
import pyglet
import glob
import subprocess as subp
import shlex
import chardet    

# MNC scanner setup
class ScannerComs(object):
    '''
    Uses pyserial to monitor serial port for messages.  To be used in the scanner,
    for the button box.  Note that the port is different for the mock scanner
    and real scanner.
    # set to 3 for the real scanner, 2 for the mock scanner
    monitoring a serial port from the scanner is instead a queue of messages.  Care needs to be taken
    not to handle old messages by accident.  Like if the subject is pressing buttons before a trial,
    they might select a response when the trial starts.
    
    '''
    def __init__(self,port=3, timeout=0.001, baudrate=19200, verbose=False):
        self.verbose=verbose
        self.alive=False
        
        try:
            # stopbits?  bytesize?
            import serial
            self._coms = serial.Serial(port, timeout=timeout, baudrate=baudrate)
            if verbose:
                print('using serial port {}'.format(self._coms.portstr))
            self._str = 'ScannerComs(port={}, timeout={}, baudrate={})'.format(port,timeout,baudrate)
            self.alive = True
        except:
            self._coms = None
            print('could not connect to serial port.  This is OK if not hooked up to a scanner.  Else check your connections,ports,settings,pyserial installed,etc...')
            self._str = 'Dummy ScannerComs instance, never connected properly'
        self._messages=[]
        
    def close(self):
        if self._coms:
            self._coms.close()
            self._coms=None
            self._str='closed ScannerComs instance'
            self.alive=False
    
    def clear(self):
        '''
        clear all incoming messages
        '''
        if self._coms:
            self._coms.flushInput()
        self._messages=[]
    
    def _read(self):
        while True:
            msg = self._coms.read()
            if not msg:
                break
            self._messages.append(msg)
    
    def wait_for_message(self,*valid_messages):
        '''
        returns whenever a valid message is encountered
        '''
        if not self._coms:
            return
        
        old_settings = self._coms.getSettingsDict()
        settings = old_settings.copy()
        settings['timeout']=None
        self._coms.applySettingsDict(settings)
        while True:
            msg = self._coms.read()
            #testing:
            if msg:
                msg=int(msg)
            '''
            try:
                msg = msg.decode()
            except AttributeError:
                pass
            '''
            if msg in valid_messages:
                self._coms.applySettingsDict(old_settings)
                return
    
    def messages(self, clear_after=True, as_set=True):
        if self._coms:
            self._read()
            ret = self._messages
            #testing:
            old=ret
            ret=[]
            for m in old:
                '''
                try:
                    m=m.decode()
                except AttributeError:
                    pass
                '''
                #testing:
                if m:
                    m=int(m)
                ret.append(m)
        else:
            ret=[]
        
        if as_set:
            ret=set(ret)
        if clear_after:
            self._messages=[]
        return ret
    
    def __bool__(self):
        return self.alive
    def __repr__(self):
        return self._str
    
    __nonzero__=__bool__
    __str__=__repr__


debug = 0 # debug = 0 MNC; debug = 1 local debug mode
mock = 0 # mock = 0 real scanner; mock = 1 mock scanner  

########
#Set directory:
cwd = os.path.dirname(__file__)
#Determine Monitor Resolution:
if platform.system() == "Windows":
    from win32api import GetSystemMetrics
    width, height = GetSystemMetrics(0), GetSystemMetrics(1)
elif platform.system() == "Darwin":
    p = subp.Popen(shlex.split("system_profiler SPDisplaysDataType"), stdout=subp.PIPE)		
    output = subp.check_output(('grep', 'Resolution'), stdin=p.stdout).decode("utf-8")
    if "Retina" in output:
          width = 1024
          height = 800
         # width = 4096
         # height = 2304
    else:
        width, height = [int(x.strip(' ')) for x in output.split(':')[-1].split(' x ')]


expName = "SocialReward"

# Define inputs

expInfo = {'Participant ID':'', 'Run':''}
dateStr = time.strftime("%b_%d_%Y", time.localtime())#add the current date
timeStr = time.strftime("%I:%M%p", time.localtime())#add the current time



# present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title= '', fixed=['date'], order=['Participant ID','Run'])



# re-name those long variables and make them strings
subID = str(expInfo['Participant ID'])
run = str(expInfo['Run'])
if subID == "":
    raise ValueError ("Enter'SocialReward_[subID]'. For example, SR_111.")
if run == "":
    raise ValueError ("Enter the run number. This should be 1, 2, 3, or 4.")




if dlg.OK == False:
    core.quit()#the user hit cancel so exit
# Define some file paths.
# if platform.system() == "Windows":
    #DataDir = os.path.join(cwd + "\Data_SC\\")
    #StimDir = os.path.join(cwd + "\Stimuli_SC\\")
# platform.system() == "Darwin":
# DataDir = os.path.join(cwd,"Data_SC")
StimDir = os.path.join(cwd ,"Stimuli_SocialReward")

os.chdir(cwd)
### If this is run 1, generate a new set of stimuli.##
tmp = "SR_exp_stimuli" + "_" + subID + ".csv"
out_csv = os.path.join(StimDir, "Stimuli", tmp)

if run == "1":
    cnt_pos = 0
    cnt_neg = 0
    # cnt_cond = np.random.randint(3, size=6) # to start from either like or don't like
    cnt_cond = np.zeros(6) # track #trial per condition 
    cnt_cond_pos = np.zeros(12) # track pos/neg items for each condition
    r = random.uniform(0, 1)
    if r > 0.5:
        peerName = ["Shiloh","Computer","Charlie"]
    else:
        peerName = ["Charlie","Computer","Shiloh"]
    pp = np.random.permutation(range(4)) # randomize 4 runs
    AnswerSheet = pd.read_csv(os.path.join(StimDir, "Answers", "%s_answer.csv" %(subID)))
    rawdata = open(os.path.join(StimDir, "SocialConnection_Master.csv"), 'rb').read()
    result = chardet.detect(rawdata)
    charenc = result['encoding']
    # print(charenc)
    MasterSheet = pd.read_csv(os.path.join(StimDir, "SocialConnection_Master.csv"),encoding = charenc)
    # print(MasterSheet)
    OrderSheet = pd.read_csv(os.path.join(StimDir, "SocialConnection_order.csv")) 
    # 1 = C-neg; 2 = C-pos; 3 = PeerDis-neg; 4 = PeerDis-Pos; 5 = PeerSim-neg 6 = PeerSim-Pos
    order = []
    
    for j in range(4):
        order = np.append(order,OrderSheet.iloc[:,pp[j]])
    # print(order)
    # order = np.append(order,OrderSheet.iloc[:,4]) # fifth run always stays the last run 
    out = pd.DataFrame(columns = ["ItemNumber", "ItemText", "Reward", "Value","ITI","ISI","Order","peerName(dis/comp/sim)"])
    out['ISI'] = MasterSheet['ISI']
    out['ITI'] = MasterSheet['ITI']
    for j in range(0,len(order)):
        if cnt_cond[int(order[j])-1]%3<2:
            pos = 1
        else:
            pos = 0
            # print(cnt_cond[int(order[j])-1])
            # out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_pos,'pos_item']
            # if out.loc[j,'ItemNumber'] > 0: 
                #out.loc[j,"ItemText"] = MasterSheet.loc[out.loc[j,'ItemNumber']-1,"Item_pos"]
            #else:
                #out.loc[j,"ItemText"] = MasterSheet.loc[-out.loc[j,'ItemNumber']-1,"Item_neg"] # when not enough positive trials and have to use negative trials
            # cnt_pos += 1
        # else:
            #out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_neg,'neg_item'] 
            #if out.loc[j,'ItemNumber'] > 0: 
                #out.loc[j,"ItemText"] = MasterSheet.loc[out.loc[j,'ItemNumber']-1,"Item_neg"] 
            #else:
                #out.loc[j,"ItemText"] = MasterSheet.loc[-out.loc[j,'ItemNumber']-1,"Item_pos"] # when not enough negative trials and have to use positive trials
            #cnt_neg += 1
        cnt_cond[int(order[j])-1]+=1
        if order[j] == 6:
            out.loc[j,"TrialType"] = "HighReward_SimPeer" #PS-Pos 6
            out.loc[j,"Condition"] = "5"
            out.loc[j,"Reward"] = 1
            out.loc[j,"Value"] = 2
            if pos:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[0],'agree_pos_sim'] # similar peer argre pos item
                cnt_cond_pos[0] += 1
            else:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[1],'agree_neg_sim'] # sim peer argre neg item
                cnt_cond_pos[1] += 1
        elif order[j] == 5:
            out.loc[j,"TrialType"]= "LowReward_SimPeer" # PS-neg 5
            out.loc[j,"Condition"]= "2"
            out.loc[j,"Reward"] = 0
            out.loc[j,"Value"] = 2
            if pos:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[2],'disagree_pos_sim']
                cnt_cond_pos[2] += 1
            else:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[3],'disagree_neg_sim']
                cnt_cond_pos[3] += 1
        elif order[j] == 4:
            out.loc[j,"TrialType"] = "HighReward_DisPeer" #PD-Pos 4
            out.loc[j,"Condition"]= "3"
            out.loc[j,"Reward"] = 1
            out.loc[j,"Value"] = 0
            if pos:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[4],'agree_pos_dis']
                cnt_cond_pos[4] += 1
            else:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[5],'agree_neg_dis']
                cnt_cond_pos[5] += 1 
        elif order[j] == 3:
            out.loc[j,"TrialType"]= "LowReward_DisPeer" # PD-neg 3
            out.loc[j,"Condition"]= "0"
            out.loc[j,"Reward"] = 0
            out.loc[j,"Value"] = 0
            if pos:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[6],'disagree_pos_dis']
                cnt_cond_pos[6] += 1
            else:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[7],'disagree_neg_dis']
                cnt_cond_pos[7] += 1         
        elif order[j] == 2:
            out.loc[j,"TrialType"]= "HighReward_Computer" #C-Pos 2
            out.loc[j,"Condition"]= "4"
            out.loc[j,"Reward"] = 1
            out.loc[j,"Value"] = 1
            if pos:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[8],'agree_pos_comp'] # similar peer argre pos item
                cnt_cond_pos[8] += 1
            else:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[9],'agree_neg_comp'] # sim peer argre neg item
                cnt_cond_pos[9] += 1
        elif order[j] == 1:
            out.loc[j,"TrialType"] = "LowReward_Computer" # C-neg 1
            out.loc[j,"Condition"] = "1"
            out.loc[j,"Reward"] = 0
            out.loc[j,"Value"] = 1
            if pos:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[10],'disagree_pos_comp']
                cnt_cond_pos[10] += 1
            else:
                out.loc[j,'ItemNumber'] = AnswerSheet.loc[cnt_cond_pos[11],'disagree_neg_comp']
                cnt_cond_pos[11] += 1
        if pos:
            out.loc[j,"ItemText"] = MasterSheet.loc[out.loc[j,'ItemNumber']-1,"Item_pos"]
        else:
            out.loc[j,"ItemText"] = MasterSheet.loc[out.loc[j,'ItemNumber']-1,"Item_neg"]
        string = out.loc[j,"ItemText"]
        out.loc[j,"ItemText"] = string[1].upper() + string[2:]
    out.loc[0,"Order"] = np.array2string(pp)
    out.loc[0:2,"peerName(dis/comp/sim)"] = peerName
    out.to_csv(out_csv, index=False, encoding = charenc) ## 


##############################
##############################
"""
Now define an output file, etc. for THIS run.
"""
os.chdir(cwd)

# Output Directory
fileLocation = os.path.join(cwd, expName + '_data')
fileName = "SR_%s_Run%s.csv" %(subID, run)


# Make the folders and files if they don't already exist. Check for duplicates.
#if not os.path.exists(DataDir):
    #os.makedirs(DataDir)
# os.chdir(DataDir)

if not os.path.exists(fileLocation):
    os.makedirs(fileLocation)
outfile = os.path.join(fileLocation, fileName)

# print(outfile)

if os.path.isfile(outfile):
    check = pd.read_csv(outfile)
    # print("yes")
    if len(check) < 24:
        print("make sure all previous runs are finished")# os.remove(outfile)
    else:
        print("Overwriting existing log file?") 
        raise ValueError ("A log file already exists for this run")
        

# throw an error if you try to run a run out of order
# if run in ["2","3"] and len(glob.glob(os.path.join(fileLocation,"*csv"))) != 1:
    #raise ValueError("Make sure the previous run occurred")
# if run in ["3"] and len(glob.glob(os.path.join(fileLocation,"*csv"))) != 2:
    #raise ValueError("Make sure the previous run occured")


 # Read in the stimuli file that's used in the experiment.
os.chdir(cwd)
stim_df = pd.read_csv(out_csv, nrows = 96)

# Make list and Panda File Header of output file for this run
run_param_list = []
header = ["ParticipantID","Run","Condition","ConditionName","Question","QuestionNumber","peerName","left_or_right","FirstButtonPressTime","CorrectButtonPressTime",
"ParticipantsFirstAnswer","First_RT","Correct_RT","ItemStart","ItemEnd","FeedbackStart","FeedbackEnd","ItemDur","FeedbackDur","Real_ITI","Real_ISI","TrialStart","TrialEnd","TrialEnd_Length","FixStart","FixDur","FixEnd"]
##############################################VARIABLES############################################



# Pre and Post Fixation duration
preFixDur = 5
postFixDur = 5
questionReadingDurDur = 1.5 # 1.5sec to read the questions
buttonDur = 2 # 2sec to press buttons 
reward_feedbackDur = 2 #2sec to show thumbsup or thumbsdown

# Set up the Window
win = visual.Window(size=(width, height), fullscr=True, allowGUI=False, color = 'black', units = "norm",
    monitor='testMonitor', colorSpace='rgb', name='win')

# Make the mouse invisible
event.Mouse(visible = False, win = win)
# fixation cross specs
fixation = visual.TextStim(win = win, text = "+", height = 0.15, pos = (0,0), color="White")
dotdot = visual.TextStim(win = win, text = "...", height = 0.15, pos = (0,0), color="White")

#######################################

# DECLAIR PROMPT

#Timers:
timer = core.Clock() # Timer for each trial
RunTimer = core.Clock() # cumulative timer running throughout whole run
responseTimer = core.Clock() # Timer that yields the participant's response time.
#---------------------------------------------
###  Starting the experiment ###


# declare prompts
#instructions1
message2 = visual.TextStim(win, pos=[0,0], color='white', units = 'norm',wrapWidth = 900, name='instructionsText', height = 0.1)
#item message
message5 = visual.TextStim(win, pos=[0,0], color='white', units = 'norm', wrapWidth = 800, name='item', height = 0.15)
#top-of-screen message--instructions
message6 = visual.TextStim(win, pos=[0,.3], color='white', units = 'norm', wrapWidth = 800, name='topText', height = 0.15)

#bottom-of-screen message--instructions
message7 = visual.TextStim(win, pos=[0,0.1], color='white', units = 'norm', wrapWidth = 800, name='bottomText', height = 0.1)
message71 = visual.TextStim(win, pos=[0,-.05], color='white', units = 'norm', wrapWidth = 800, name='bottomText', height = 0.1)
message72 = visual.TextStim(win, pos=[0,-.2], color='white', units = 'norm', wrapWidth = 800, name='bottomText', height = 0.1)
message73 = visual.TextStim(win, pos=[0,-.35], color='white', units = 'norm', wrapWidth = 800, name='bottomText', height = 0.1)
# Name
message8 = visual.TextStim(win, pos=[0,.4], units = 'norm', wrapWidth = 800, name='Partner_Name', height = 0.15)
rect = visual.Rect(win, height=0.17, width = 0.5, lineWidth=3, fillColor=None, pos=[0,0.4], ori=0.0)
#left answer
leftAnswer = visual.TextStim(win, pos=[-.2,-.4], color='white', units = 'norm', wrapWidth = 800,  name='leftAnswer', height = 0.1)
leftCircle = visual.Circle(win, radius=0.5, lineWidth=3, lineColor=[1, 0, 0], fillColor=None, pos=[-.2,-.4], size=0.6, ori=0.0)
#right answer
rightAnswer = visual.TextStim(win, pos=[.2,-.4], color='white', units = 'norm', wrapWidth = 800, name='rightAnswer',  height = 0.1)
rightCircle = visual.Circle(win, radius=0.5, lineWidth=3, lineColor=[1, 0, 0], fillColor=None, pos=[.2,-.4], size=0.6, ori=0.0)

# No data
message3 = visual.TextStim(win, pos=[0,0], units = 'norm', wrapWidth = 800, name='topText', height = 0.3)
# not me / me too
message_not_me = visual.TextStim(win, pos=[0,-0.2], units = 'norm', wrapWidth = 800, name='NotMe', height = 0.15)

Thumbsup = visual.ImageStim(win, image = os.path.join(StimDir, "thumbsup.png"), units = "norm", pos = (0,0.1), size = [0.2,0.4])
Thumbsdown = visual.ImageStim(win, image = os.path.join(StimDir,"thumbsdown.png"), units = "norm", pos = (0,0.1), size = [0.2,0.4])
ComputerX = visual.ImageStim(win, image = os.path.join(StimDir, "computerX.png"), units = "norm", pos = (0,0.1), size = [0.25,0.5])
ComputerCHECK = visual.ImageStim(win, image = os.path.join(StimDir, "computerCHECK.png"), units = "norm", pos = (0,0.1), size = [0.25,0.5])


#bottom-of-screen message--end of task
# message76 = visual.TextStim(win, pos=[0,-.53], color='white', units = 'norm', wrapWidth = 800, name='bottomText', height = 0.1)
# message77 = visual.TextStim(win, pos=[0,-.78], color='white', units = 'norm', wrapWidth = 800, name='bottomText', height = 0.1)

message3.setText("No data")
message6.setText("Learn about your peers!") 
message7.setText("Your peer's name will appear at the top.")
message71.setText("Press the LEFT or RIGHT button")
message72.setText("to see your peer's or computer's answers.")
message73.setText("You will first be reminded of your answers.")
#message74.setText("Press <6> when ready (debug mode)")

#######################################
message6.draw()
message7.draw()
message71.draw()
message72.draw()
message73.draw()
win.flip()

## Button interface
if mock:
    scanner_coms = ScannerComs(port='COM4', timeout=0.001, baudrate=19200) # real
else:
    scanner_coms = ScannerComs(port='COM3', timeout=0.001, baudrate=19200) # mock

## The scanner starts when the "trigger button" is pressed. The trigger box has a "trigger button" and in the JKpsycho, the trigger button in # 6.
## So, in our experiment, the experiment will be initiated by the trigger button.
## This "6" is NOT a keyboard six button.
if debug:
    while '6' not in event.getKeys(): # change to keyboard 6 for piloting
        message6.setAutoDraw(True)
        message7.setAutoDraw(True)
        message71.setAutoDraw(True)
        message72.setAutoDraw(True)
        message73.setAutoDraw(True)
#        message74.setAutoDraw(True)
        if event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
else:
    message6.setAutoDraw(True)
    message7.setAutoDraw(True)
    message71.setAutoDraw(True)
    message72.setAutoDraw(True)
    message73.setAutoDraw(True)
    scanner_coms.wait_for_message(6)
    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()

            

message6.setAutoDraw(False)
message7.setAutoDraw(False)
message71.setAutoDraw(False)
message72.setAutoDraw(False)
message73.setAutoDraw(False)



win.flip()
# Start the cumulative timer that will go throughout the run
RunTimer.reset()
############################



# check for quit (the Esc key)
if event.getKeys(keyList=["escape"]):
    win.close()
    core.quit()
    
# define some variables
peerName = stim_df["peerName(dis/comp/sim)"]
# Determine which portion of the TrialsList will be presented during this run.
if run == "1":
    list_start = 0
    list_end = 24
elif run =="2":
    list_start = 24
    list_end = 48
elif run == "3":
    list_start = 48
    list_end = 72 ## 
elif run == "4":
    list_start = 72
    list_end = 96 ## 
# if debug:
#    list_start = 0
#    list_end = 6

C = np.matrix([[220,50,32],
[255,255,255],
[140,50,204]]) # salmon, grey, purple
# [93,58,155]]
C = C.astype(np.float)/255
if peerName[0] == "Charlie":
    C[[0,2],:] = C[[2,0],:]


# present the fixation cross for the pre-run duration
fixation.draw()
win.flip()
FixStart = RunTimer.getTime()
core.wait(preFixDur)
FixEnd = RunTimer.getTime()
FixDur = FixEnd - FixStart

# check for quit (the Esc key)
if event.getKeys(keyList=["escape"]):
    win.close()
    core.quit()
# Begin Trial:

## MAIN EXPERIMENT 
for i in range(list_start,list_end):
    timer.reset()
    event.clearEvents(eventType = "keyboard")
    if i != list_start:
        FixStart = 'N/A'
        FixEnd = 'N/A'
        FixDur = 'N/A'
    # set up parameters particular to this trial
    ITI = stim_df["ITI"][i]
    ISI = stim_df["ISI"][i]
    reward = stim_df["Reward"][i]
    value = stim_df["Value"][i]
    condition = stim_df["Condition"][i]
    ConditionName = stim_df["TrialType"][i]
    # Fixation ITI
    fixation.draw()
    win.flip()
    ITI_Start = timer.getTime()
    if i != list_start and (button_flag==0):
        core.wait(ITI+buttonDur-Answer_correctRT-0.25) 
    elif i == list_start:
        core.wait(ITI)
    elif button_flag==1:
        core.wait(ITI-0.25)
    ITI_End = timer.getTime()
    trialStart = RunTimer.getTime() # TrialStart is when name first appears
    message8.setText(peerName[value])
    message8.setColor(np.asarray(C[value]).flatten())
    rect.setLineColor(np.asarray(C[value]).flatten())
    message8.draw()
    rect.draw()
    win.flip()  # "waiting for" to question
    core.wait(0.5)
    # present question and wait for 2sec
    message5.setText("You: " + stim_df["ItemText"][i])    
    message8.draw()
    rect.draw()
    message5.draw()
    ItemStart = RunTimer.getTime() # Item shows up
    win.flip()  # "waiting for" to question
    core.wait(questionReadingDurDur)
    r = random.uniform(0, 1)
    # print(r)
    if r > 0.5:
        leftAnswer.setText("Press L \n Learn about " + peerName[value])
        left_or_right = "L"
        leftAnswer.draw()
    else:
        rightAnswer.setText("Press R \n Learn about " + peerName[value])
        left_or_right = "R"
        rightAnswer.draw() 
    
    message8.draw()
    rect.draw()
    message5.draw()
    win.flip()  # "waiting for" to question
    responseTimer.reset()
    FirstKey = "N/A"  # ecord just the first key pressed
    Answer_correctRT = "N/A"  # record the response time of the correct keypress too.
    Answer_firstRT = "N/A"  # record the response time of the first keypress too.
    firstbuttonPressTime = "N/A"
    correctbuttonPressTime = "N/A"  # also record the time of the first keypress relative to the cumulative clock.
    ChildFirstResponse = "N/A"
    button_flag = 1 # make a flag to only record the first button press
    # record answer during entire period while question is shown
    while (responseTimer.getTime() < buttonDur) & button_flag:
        if debug:
            answer = [x for x in event.getKeys() if x in ["1","2"]]
        else:
            answer = [x for x in scanner_coms.messages(as_set = False) if x in [1,2]] 
        if event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
        if FirstKey=="N/A" and len(answer) > 0 and responseTimer.getTime() > 0.3:  # first keypress and make sure it happens after the answer
            # print("first answer" + answer[0])
            FirstKey = answer[0]  # record just the first key pressed
            if debug:
                FirstKey = int(FirstKey)
            Answer_firstRT = responseTimer.getTime()  # record the response time of the first button press.
            firstbuttonPressTime = RunTimer.getTime()  # record the time of the first keypress relative to the cumulative clock.
            if FirstKey == 1 and left_or_right == "L":
                Answer_correctRT = Answer_firstRT  # correct RT = first RT
                correctbuttonPressTime = firstbuttonPressTime
                ChildFirstResponse = "L"  # Participant answered left
                leftAnswer.draw()
                leftCircle.draw()
                button_flag = 0;
            elif FirstKey == 2 and left_or_right == "R":
                Answer_correctRT = Answer_firstRT  # correct RT = first RT
                correctbuttonPressTime = firstbuttonPressTime
                ChildFirstResponse = "R"  # Participant answered right
                rightAnswer.draw()
                rightCircle.draw()
                button_flag = 0;
        elif FirstKey !="N/A" and len(answer) > 0:  # if the first button press is wrong, record the second
            if int(answer[0]) == 1 and left_or_right == "L":
                Answer_correctRT = responseTimer.getTime()
                correctbuttonPressTime = RunTimer.getTime()  
                leftAnswer.draw()
                leftCircle.draw()
                button_flag = 0;
            elif answer[0] == 2 and left_or_right == "R":
                Answer_correctRT = responseTimer.getTime()
                correctbuttonPressTime = RunTimer.getTime()  
                rightAnswer.draw()
                rightCircle.draw()
                button_flag = 0;
    #message5.setText("You: " + stim_df["ItemText"][i])    
    #message8.setText(peerName[value])
    message8.draw()
    message5.draw()
    rect.draw()
    win.flip() 
    core.wait(0.25)
    # check for quit (the Esc key)
    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()

    # Fixation ISI    
    dotdot.draw()
    win.flip()  # question to ISI fix
    ItemEnd = RunTimer.getTime()
    ISI_Start = timer.getTime()
    core.wait(ISI)        

#    # check for quit (the Esc key)         
    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()

    # define the feedback
    if Answer_correctRT != "N/A":
        if condition == 5 or condition==3:
           Thumbsup.draw()
           message_not_me.setText('Me too')
           message_not_me.draw()            
        elif condition == 2 or condition==0:
           Thumbsdown.draw()
           message_not_me.setText('Not me')
           message_not_me.draw()            
        elif condition == 4:
            ComputerCHECK.draw()
            message_not_me.setText('Match')
            message_not_me.draw()            
        elif condition == 1:
            ComputerX.draw()
            message_not_me.setText('No match')
            message_not_me.draw()            
    else:
        message3.draw() # if no feedback don't show response

    # present the reward
    rect.draw()
    message8.draw()
    win.flip()   # ISI fix to Feedback 
    ISI_End = timer.getTime()  # ####Aiste moved here from above
    feedbackStart = RunTimer.getTime()
    core.wait(reward_feedbackDur)
    feedbackEnd = RunTimer.getTime()

    

    # check for quit (the Esc key)
    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()
        
    trialEnd_length  = timer.getTime()
    trialEnd = RunTimer.getTime()
    
    # End-of-run fixation
    if i == (list_end-1):
        fixation.draw()
        win.flip()
        FixStart = RunTimer.getTime()
        core.wait(postFixDur)
        FixEnd = RunTimer.getTime()
        FixDur = FixEnd - FixStart

    

    

    

    # do a few calculations

    # waitingDur = ItemStart - StimuliStart # From appearing of the name to button press

    ItemDur = ItemEnd - ItemStart
    feedbackDur = feedbackEnd - feedbackStart
    real_ITI = ITI_End - ITI_Start
    real_ISI = ISI_End - ISI_Start       

    # Panda Output File
    # run_param_list.append([subID, run, stim_df["block"][i], stim_df["Condition"][i], stim_df["ConditionNumber"][i], stim_df["ItemText"][i],
    # stim_df["ItemNumber"][i], buttonPressTime, ChildFirstResponse, Answer_RT, partnerResponse, waitingStart, waitingStop, questionStart, questionEnd, feedbackStart,
    # feedbackEnd, waitingDur, questionDur, feedbackDur, real_ITI, real_ISI, trialStart, trialEnd, trialEnd_length, FixStart, FixDur, FixEnd])
    run_param_list.append([subID, run, condition, ConditionName, stim_df["ItemText"][i],
    stim_df["ItemNumber"][i], peerName[value],left_or_right,firstbuttonPressTime,correctbuttonPressTime, ChildFirstResponse, Answer_firstRT,Answer_correctRT, ItemStart, ItemEnd, feedbackStart,
    feedbackEnd, ItemDur, feedbackDur, real_ITI, real_ISI, trialStart, trialEnd, trialEnd_length, FixStart, FixDur, FixEnd])









    fid = pd.DataFrame(run_param_list, columns = header)
    fid.to_csv(outfile, header = True)
    os.chdir(cwd)

        

    # check for quit (the Esc key)

    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()


# Choose which ending text to display based on what the run number was.
if run == "1":
    endingText = "Take a short break."
elif run == "2":
    endingText = "Take a short break."
elif run == "3":
    endingText = "Take a short break."    
elif run == "4":
    endingText = "Take a short break."
message7.setText(endingText)

# -------Start Routine "done"-------
message7.draw()
win.flip()
core.wait(1)
win.close()
core.quit()




# press escape or space to exit

while True:
    theseKeys = event.getKeys()
    if "escape" in theseKeys:
        core.quit()
    if "space" in theseKeys:
        break

