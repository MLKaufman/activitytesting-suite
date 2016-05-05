#! /usr/bin/env python
import os, sys
from math import *
from ctypes_opencv import *
from Tkinter import *
from PIL import ImageTk
import PIL, tkFileDialog, tkMessageBox, time

print("Thigomatixic Analyzer Quick and Dirty: Michael Kaufman 2009")

numpixels = 0 #Number of Pixels

#output file

foutput = "thigmout.txt"
#ROI
roix1 = 110
roiy1 = 40
roix2 = 530
roiy2 = 450
roirect = cvRect(roix1,roiy1,roix2,roiy2)
roicenter = (((roix2-roix1)/2)+roix1,((roiy2-roiy1)/2)+roiy1)
print roicenter

#calc thigmotaxia
#340 pix per 100 cm
#3.4 pix per cm
#how many cm square box do you want?
thig_sq_boxcm = 85
thig_sq_box = thig_sq_boxcm * 3.4

#top left
thigx1 = roicenter[0] - (thig_sq_box/2)
thigy1 = roicenter[1] - (thig_sq_box/2)
#top right
thigx2 = roicenter[0] + (thig_sq_box/2)
thigy2 = roicenter[1] - (thig_sq_box/2)
#bottom right
thigx3 = roicenter[0] + (thig_sq_box/2)        
thigy3 = roicenter[1] + (thig_sq_box/2)
#bottom left
thigx4 = roicenter[0] - (thig_sq_box/2)
thigy4 = roicenter[1] + (thig_sq_box/2)




#MOVEMENT/DISTANCE SENSITIVTY In Pix
maxmove = 5 * 3.4
minmove = 1 * 3.4

#cvSetImageROI
capture = 0
current_frame = 0

#ThigmaRect
thigmarect = [(thigx1, thigy1), (thigx2, thigy2), (thigx3, thigy3), (thigx4, thigy4)]

#DEBUG WINDOWS
#debug_image = cvCreateImage (cvSize(600,600),8,3)
#cvZero(debug_image)
#cvNamedWindow("debug", 1)

_red = cvScalar (0, 0, 255, 0)
_green = cvScalar (0, 255, 0, 0)

def menu_saveconfig():
        pass

def menu_loadconfig():
        pass

def f_dispimage(frame):
        dispframe = frame.as_pil_image()
        ApImage = ImageTk.PhotoImage(dispframe)
        can.create_image(320,240, image=ApImage)

def f_grabframe(capture):
        inputfeed = cvQueryFrame(capture)
        #Create Image Space
        bwframe = cvCreateImage(cvGetSize(inputfeed), IPL_DEPTH_8U ,1)
        threshframe = cvCreateImage(cvGetSize(inputfeed), IPL_DEPTH_8U ,1)
        
        cvConvertImage(inputfeed, bwframe, 1) #Convert feed to BW Images

        if v_appcon.get() == 1: #white object - black background
            if v_threshold.get() == 1: #binary thresholding with scale
                cvThreshold(bwframe, threshframe, sc_threshold1.get(), 256, CV_THRESH_BINARY_INV)
            if v_threshold.get() == 2: #value thresholding
                cvThreshold(bwframe, threshframe, sc_threshold1.get(), 256, CV_THRESH_BINARY_INV)

        if v_appcon.get() == 2: #black object - white background
            if v_threshold.get() == 1: #binary thresholding with scale
                cvThreshold(bwframe, threshframe, sc_threshold1.get(), 256, CV_THRESH_BINARY)
            if v_threshold.get() == 2:#value thresholding
                cvThreshold(bwframe, threshframe, sc_threshold1.get(), 256, CV_THRESH_BINARY)
                
        return threshframe

def f_trackframe(image):
        if v_targetid.get() == 1: #Manual
                pass
        
        if v_targetid.get() == 2: #Automatic
                cvSetImageROI(image,roirect)
                cvErode(image, image,0, 10)
                cvDilate(image, image,0,10)
                storage = cvCreateMemStorage(0)
                nb_contours, contours = cvFindContours(image, storage) # mode=CV_RETR_TREE, method=CV_CHAIN_APPROX_SIMPLE)
                print "NUM CONT:", nb_contours
                try:
                        minrect = cvMinAreaRect2(contours)
                except WindowsError:
                        pass
                #print "SEQ", contours
                print minrect.center.x, minrect.center.y
                return minrect.center.x, minrect.center.y

        if v_targetid.get() == 3: #Full Auto
                pass
def f_getlocation(x,y):
        poly = thigmarect
        print poly, "X", x, "Y", y
        n = len(poly)
        inside =False
        p1x,p1y = poly[0]
        for i in range(n+1):
                p2x,p2y = poly[i % n]
                if y > min(p1y,p2y):
                        if y <= max(p1y,p2y):
                                if x <= max(p1x,p2x):
                                        if p1y != p2y:
                                                xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                                        if p1x == p2x or x <= xinters:
                                                inside = not inside
                p1x,p1y = p2x,p2y
        return inside

def f_getframetime(frame_num):
        #Get Amount of time since last Frame
        pass
    
def canvas_click(event): # MOUSE 1 (LEFT-CLICK) PLACE POINT
        global initial_xy
        messagestr = "X=" + str(event.x) + " Y=" + str(event.y)
        tkMessageBox.showinfo("Selection  Points:", messagestr)
        #can.create_oval(event.x, event.y, event.x+1, event.y+1, fill="black")
        
def bf_play_video():
        pass

def bf_play_stop():
        pass

def bf_load_video():
        global capture
        global num_frames
        global ApImage
        global filestr
        del_cap()
        filestr = tkFileDialog.askopenfilename(title='Please select avi:', filetypes = [('avi files', '.avi')])
        capture = cvCaptureFromAVI(filestr)
        num_frames = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT)
        vid_fps = cvGetCaptureProperty(capture, CV_CAP_PROP_FPS)
        vid_length = cvGetCaptureProperty(capture, CV_CAP_PROP_POS_MSEC)
        #vid_length = round((num_frames/float(vid_fps))/float(60),3)
        print "NUMBER OF FRAMES =", num_frames
        filestrsplit = filestr.rsplit('/', 1)
        l_video_name2.config(text=filestrsplit[1])
        l_video_length2.config(text=vid_length)
        l_video_frames2.config(text=num_frames)

        #cvSetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES, 1)
        frame = f_grabframe(capture)
        dispframe = frame.as_pil_image()
        ApImage = ImageTk.PhotoImage(dispframe)
        can.create_image(320,240, image=ApImage)
        print "XXXXXXXXXXXXXXXXXXXXXXX"
        can.create_rectangle(roix1, roiy1, roix2, roiy2, outline='red') #DRAW ROI
        can.create_text(roicenter[0], roicenter[1], text='X', fill='red') #DRAW CENTER
        can.create_rectangle(thigx1,thigy1,thigx3,thigy3, outline='yellow') #DRAW THIGMOTAXIC AREA
        
def bf_skipforward():
        pass
                
def bf_skipback():
        pass

def bf_previewthreshold():
        pass

def bf_previewtarget():
        pass

def del_cap():
        global capture
        del capture

def bf_analyzer():
        global ApImage
        
        filepathlist = []
        filestr = tkFileDialog.askdirectory()
        print filestr
        masterfilelist = os.listdir(filestr)
        print masterfilelist


        for each in masterfilelist:
                filepathlist.append(filestr + '/' + each)
        print filepathlist
    
        for filepath in filepathlist:
                print filepath
                f = open(foutput, 'a')
                #TODO get video information: num frames, fps, time, length, etc
                capture = cvCaptureFromAVI(filepath)
                print "FILE:", filepath
                filepath2 = str(filepath)
                tmpwrite_buffer = str(filepath.rsplit('/', 1)) + ", "
                write_buffer = tmpwrite_buffer[1]
                print write_buffer
                f.write(write_buffer)
                num_frames = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT)
                print "NUM Frames:", num_frames
                vid_fps = cvGetCaptureProperty(capture, CV_CAP_PROP_FPS)
                print "FPS:", vid_fps
                #vid_length = cvGetCaptureProperty(capture, CV_CAP_PROP_POS_MSEC)
                vid_length = round((num_frames/float(vid_fps)),3)
                print "Video Length:", vid_length
                print "JGAKJGDKAJHSGDKJASHGDKASJHGDKASHDGKASHGDAKHSGKJGSAHDKASH"        
                frame_num = 0 #reset to zero
                time_in_center = 0
                distancetraveled = 0
                thisx = 0
                thisy = 0
                lastx = 0
                lasty = 0
                firstrun = 0

                
                frames_to_analyze = 1800 #two minutes

                #Display Apparatus
                frame = f_grabframe(capture)
                dispframe = frame.as_pil_image()
                ApImage = ImageTk.PhotoImage(dispframe)
                can.create_image(320,240, image=ApImage)
                print "XXXXXXXXXXXXXXXXXXXXXXX"
                can.create_rectangle(roix1, roiy1, roix2, roiy2, outline='red') #DRAW ROI
                can.create_text(roicenter[0], roicenter[1], text='X', fill='red') #DRAW CENTER
                can.create_rectangle(thigx1,thigy1,thigx3,thigy3, outline='yellow') #DRAW THIGMOTAXIC AREA
                
                while frame_num <= frames_to_analyze:
                        threshframe = f_grabframe(capture) #Grab Frame and Threshold it

                        #Update Display
                        dispframe = threshframe.as_pil_image()
                        ApImage = ImageTk.PhotoImage(dispframe)
                        can.create_image(320,240, image=ApImage)
                        can.create_rectangle(roix1, roiy1, roix2, roiy2, outline='red') #DRAW ROI
                        can.create_text(roicenter[0], roicenter[1], text='X', fill='red') #DRAW CENTER
                        can.create_rectangle(thigx1,thigy1,thigx3,thigy3, outline='yellow') #DRAW THIGMOTAXIC AREA
                        
                        #track object, return x,y coords  (mindful of ROI)
                        minx, miny = f_trackframe(threshframe)
                        
                        #adjust coords for ROI OFFSET
                        minx += roix1
                        miny += roiy1

                        #Draw Location
                        can.create_text(minx, miny, text='X', fill='blue')

                        #Thigmotaxia
                        isinside = f_getlocation(minx,miny) #Check if Location is inside Thigma

                        print "INSIDE: ", isinside
                        if isinside == True:
                                time_in_center += .0666666
                                
                        #Distance Traveled
                        thisx = minx
                        thisy = miny
                        xpoints = thisx - lastx
                        ypoints = thisy - lasty

                        if firstrun == 0:
                                print "First run!"
                                firstrun = 1
                        else:
                                thisdistance = sqrt(pow(xpoints,2)+pow(ypoints,2))
                                if thisdistance > 500 or thisdistance < 0:
                                        thisx = lastx
                                        thisy = lasty
                                elif thisx < roix1 or thisx > roix2 or thisy < roiy1 or thisy > roiy2:
                                        thisx = lastx
                                        thisy = lasty
                                else:
                                        distancetraveled += thisdistance

                        
                        frame_num = cvGetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES)
                        print "Processing Frame", frame_num , " of " , frames_to_analyze
                        
                print "TIME IN CENTER:", time_in_center, "DISTANCE TRAVELED:", distancetraveled
                write_buffer = str(time_in_center) + ", " + str(distancetraveled) + "\n"
                f.write(write_buffer)
                f.close()
        
def menu_load_video():
        pass

############ ROOT WINDOW GUI #############
rootwindow = Tk()
rootwindow.title("Rodent Tracker 3000 alpha")
rootwindow.geometry("1000x600+200+0")

### CANVAS WINDOW
can = Canvas(rootwindow, width = '640', height = '480')
can.configure(cursor="crosshair")
can.place(x = 0, y = 0)
can.bind("<Button-1>", canvas_click)

### GRAB VIDEO


###GUI FEATURES
menubar = Menu(rootwindow)
### Apparatus Conditions
l_appcon = Label(rootwindow, text="Apparatus Conditions:")
v_appcon = IntVar()

rb_appcon1 = Radiobutton(rootwindow, text="Light Foreground / Dark Background", variable=v_appcon, value=1)
rb_appcon2 = Radiobutton(rootwindow, text="Dark Foreground / Light Background", variable=v_appcon, value=2)

v_appcon.set(1)

### Thresholding
l_threshold = Label(rootwindow, text="Thresholding:") 
v_threshold = IntVar()

rb_threshold1 = Radiobutton(rootwindow, text="Binary Thresholding", variable=v_threshold, value=1)
sc_threshold1 = Scale(rootwindow, from_=1, to=256, orient=HORIZONTAL, resolution=1, showvalue = YES)
sc_threshold1.set(70)
rb_threshold2 = Radiobutton(rootwindow, text="Value Thresholding", variable=v_threshold, value=2)

v_threshold.set(1)

b_prevthreshold = Button(rootwindow, text="Preview Threshold", command=bf_previewthreshold)

### Target Identification
l_targetid = Label(rootwindow, text="Target Identification:")
v_targetid = IntVar()

rb_targetid1 = Radiobutton(rootwindow, text="Manual", variable=v_targetid, value=1)
rb_targetid2 = Radiobutton(rootwindow, text="Automatic", variable=v_targetid, value=2)
rb_targetid3 = Radiobutton(rootwindow, text="Full Auto(Experimental)", variable=v_targetid, value=3)

v_targetid.set(2)

b_prevtarget = Button(rootwindow, text="Preview Target", command=bf_previewtarget)
### Targeting Radius
l_targetrad = Label(rootwindow, text="Targeting Sensitivity Radius:")
e_targetrad = Entry(rootwindow, width = 3)
e_targetrad.insert(0,15)
### Data Generation
l_datagen = Label(rootwindow, text="Data Generation:")

### Batch Processing

### Video Buttons
b_vbload = Button(rootwindow, text="Load", command=bf_load_video)
b_vbplay = Button(rootwindow, text="Play", command=bf_play_video)
b_vbplay_stop = Button(rootwindow, text="Stop", command=bf_play_stop)
b_vbskipforward = Button(rootwindow, text="Skip>", command=bf_skipforward)
b_vbskipback = Button(rootwindow, text="<Skip", command=bf_skipback)

### Video Information
l_video_info = Label(rootwindow, text="Video Information:")
l_video_name = Label(rootwindow, text="Name=")
l_video_name2 = Label(rootwindow, text="x")
l_video_length = Label(rootwindow, text="Length=")
l_video_length2 = Label(rootwindow, text="")
l_video_frames = Label(rootwindow, text="Frames=")
l_video_frames2 = Label(rootwindow, text="")

### Analyze
b_analyzer = Button(rootwindow, text=">>ANALYZE!<<", command=bf_analyzer)
#MAIN WINDOW CANVAS

### WIDGET PLACEMENT ###

### Apparatus Conditions
l_appcon.place(x=645, y=0)
rb_appcon1.place(x=700 , y=20) 
rb_appcon2.place(x=700 , y=40)
### Thresholding
l_threshold.place(x=645, y=100)
rb_threshold1.place(x=700, y=120)
sc_threshold1.place(x=850, y=120)
rb_threshold2.place(x=700, y=160)
b_prevthreshold.place(x=750, y=190)
### Target Identification
l_targetid.place(x=645,y=240)
rb_targetid1.place(x=700, y=260)
rb_targetid2.place(x=700, y=280)
rb_targetid3.place(x=700, y=300)
b_prevtarget.place(x=750,y=320)
### Targeting Radius
l_targetrad.place(x=645, y=380)
e_targetrad.place(x=700, y=400)
### Data Generation
l_datagen.place(x=645, y=480)
### Video Buttons
b_vbload.place(x=0,y=480)
b_vbplay.place(x=40, y=480)
b_vbplay_stop.place(x=80, y=480)
b_vbskipback.place(x=120, y=480)
b_vbskipforward.place(x=160, y=480)

### Video Information
l_video_info.place(x=0, y=520)
l_video_name.place(x=20, y=540)
l_video_name2.place(x=80, y=540)
l_video_length.place(x=20, y=560)
l_video_length2.place(x=80, y=560)
l_video_frames.place(x=20, y=580)
l_video_frames2.place(x=80, y=580)

### Analyze
b_analyzer.place(x=400, y=560)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Load Video File", command=menu_load_video)
filemenu.add_separator()
filemenu.add_command(label="Save Zone Data", command=menu_saveconfig)
filemenu.add_command(label="Load Zone Data", command=menu_loadconfig)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=rootwindow.quit)
menubar.add_cascade(label="File", menu=filemenu)

# display the menu
rootwindow.config(menu=menubar)
rootwindow.mainloop()
