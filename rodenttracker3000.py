#! /usr/bin/env python
import sys
from math import *
from ctypes_opencv import *
from Tkinter import *
from PIL import ImageTk
import PIL, tkFileDialog, tkMessageBox, time

numpixels = 0 #Number of Pixels

#cvSetImageROI
capture = 0
current_frame = 0

#cvThreshold(bwframe, threshframe, 70, 256, CV_THRESH_BINARY)#OLD
#can.create_image(176,144, image=ApImage) #display image on canvas

### FUNCTIONS
def thresh(inputfeed):
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

def tracking(image):
        if v_targetid.get() == 1: #Manual
                roirect = cvRect(118,36,400,400)
                cvSetImageROI(image,roirect)
                cvErode(image, image,0, 10)
                cvDilate(image, image,0,10)
                storage = cvCreateMemStorage(0)
                nb_contours, contours = cvFindContours(image, storage)
                print "NUM CONT:", nb_contours
                try:
                        rectangle = cvMinEnclosingCircle(contours)
                except WindowsError:
                        pass
                return rectangle            
                
        if v_targetid.get() == 2: #Automatic
                roirect = cvRect(118,36,400,400)
                cvSetImageROI(image,roirect)
                cvErode(image, image,0, 10)
                cvDilate(image, image,0,10)
                storage = cvCreateMemStorage(0)
                nb_contours, contours = cvFindContours(image, storage, mode=CV_RETR_TREE, method=CV_CHAIN_APPROX_SIMPLE)
                print "NUM CONT:", nb_contours
                try:
                        rectangle = cvMinEnclosingCircle(contours)
                except WindowsError:
                        pass
                print "SEQ", contours
                return rectangle   

        if v_targetid.get() == 3: #Full Auto
                roirect = cvRect(113,33,400,400)
                cvSetImageROI(image,roirect)
                #erroded = cvCreateImage(cvGetSize(image), IPL_DEPTH_8U ,1)
                cvErode(image, image,0, 10)
                cvDilate(image, image,0,10)
                storage = cvCreateMemStorage(0)
                nb_contours, contours = cvFindContours(image, storage) #mode=CV_RETR_CCOMP, method=CV_CHAIN_APPROX_SIMPLE)
                
                #statereader = cvStartFindContours(image, storage)
                #thiscontour = cvFindNextContour(statereader)
                #print "THISCONTOUR", thiscontour
                #point = cvGetSeqElem(thiscontour,0)
                #print "POINT",point
                print "RECT",cvBoundingRect(cvApproxPoly (contours, sizeof(CvContour), storage, CV_POLY_APPROX_DP, 3, 1))
                rectangle = cvMinAreaRect2(contours)
                print "RECT2=", rectangle
                print "REc Box=", cvBoxPoints(rectangle)
        return rectangle        
        
def canvas_click(event): # MOUSE 1 (LEFT-CLICK) PLACE POINT
        global initial_xy
        messagestr = "X=" + str(event.x) + " Y=" + str(event.y)
        tkMessageBox.showinfo("Selection  Points:", messagestr)
        #can.create_oval(event.x, event.y, event.x+1, event.y+1, fill="black")
        
def bf_play_video():
    global play_stop
    global capture
    global ApImage
    global frame
    global current_frame
    
    play_stop = 0
    num = 0

    savedcontours = 0
    print num_frames
    while current_frame <= int(num_frames)-1:
        current_frame = cvGetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES) #get current frame number
        print "CURRENT FRAME=", current_frame
        print "HAHAHAHHHAHAHAhAHAHAHAHAHAHAHAHAH"
        frame = cvQueryFrame(capture)
        if frame == None: break

        #THRESHOLDING
        threshed_frame = thresh(frame)
        print "SPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAM"

        #TRACKING
        rectangle = tracking(threshed_frame)
        print "MMMMMWMMMMMMMWMMMMMMWMMMMMMMWMMMMMMM"
        
        dispframe = frame.as_pil_image()
        ApImage = ImageTk.PhotoImage(dispframe)
        can.create_image(320,240, image=ApImage)
        vid_length = (cvGetCaptureProperty(capture, CV_CAP_PROP_POS_MSEC)/float(1000))
        l_video_length2.config(text=vid_length)
        rectangle.x = rectangle.x + 118
        rectangle.y = rectangle.y + 36
        can.create_oval(rectangle.x, rectangle.y, rectangle.x+10, rectangle.y+10, fill="RED")


def bf_play_stop():
        global play_stop
        play_stop = 1

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
        frame = cvQueryFrame(capture)
        dispframe = frame.as_pil_image()
        ApImage = ImageTk.PhotoImage(dispframe)
        can.create_image(320,240, image=ApImage)
        print "XXXXXXXXXXXXXXXXXXXXXXX"

def bf_skipforward():
        global play_stop
        global capture
        global ApImage
        global frame
        frame = cvQueryFrame(capture)
        dispframe = frame.as_pil_image()
        ApImage = ImageTk.PhotoImage(dispframe)
        can.create_image(320,240, image=ApImage)

def bf_skipback():
        global capture
        global filestr
        capture = cvCaptureFromAVI(filestr)
   
def old_bf_load_video():
    global capture
    global num_frames
    del_cap()
    filestr = tkFileDialog.askopenfilename(title='Please select avi:', filetypes = [('avi files', '.avi')])
    capture = cvCaptureFromAVI(filestr)
    num_frames = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT)
    print "NUMBER OF FRAMES =", num_frames

def bf_previewthreshold():
        global frame
        global ApImage
        threshed_frame = thresh(frame)
        print "SPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAM"
        dispframe = threshed_frame.as_pil_image()
        ApImage = ImageTk.PhotoImage(dispframe)
        can.create_image(320,240, image=ApImage)
        
def bf_previewtarget():
        pass

def del_cap():
        global capture
        del capture

def bf_analyzer():
        global capture
        global ApImage
        global frame
        global current_frame
    
        num = 0
        savedcontours = 0
        
        print num_frames
        thisx = 0
        thisy = 0
        firstrun = 0
        distancetraveled = 0
        while current_frame <= int(num_frames)-1:

                current_frame = cvGetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES) #get current frame number
                print "CURRENT FRAME=", current_frame
                #print "HAHAHAHHHAHAHAhAHAHAHAHAHAHAHAHAH"
                frame = cvQueryFrame(capture)
                if frame == None: break

                #THRESHOLDING
                threshed_frame = thresh(frame)
                #print "SPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAM"

                #TRACKING
                minrect = tracking(threshed_frame)
                #print "MMMMMWMMMMMMMWMMMMMMWMMMMMMMWMMMMMMM"
                
                vid_length = (cvGetCaptureProperty(capture, CV_CAP_PROP_POS_MSEC)/float(60))
                l_video_length2.config(text=vid_length)
                print minrect
                rectanglex = minrect[1].x
                rectangley = minrect[1].y
                rectanglex = rectanglex + 118
                rectangley = rectangley + 36
                lastx = thisx
                lasty = thisy

                thisx = rectanglex
                thisy = rectangley
                xpoints = thisx - lastx
                ypoints = thisy - lasty
                if firstrun == 0:
                        print "First run!"
                        firstrun = 1
                else:
                        thisdistance = sqrt(pow(xpoints,2)+pow(ypoints,2))
                        if thisdistance > 33 or thisdistance < 6:
                                thisx = lastx
                                thisy = lasty
                        else:
                                distancetraveled += thisdistance
                                can.create_oval(rectanglex, rectangley, rectanglex+10, rectangley+10, fill="RED")
                        print "DIST:", distancetraveled
                
        messagestr = "The distance traveled is:" + str(distancetraveled)
        tkMessageBox.showinfo("Distance Traveled:", messagestr)
                
def bf_analyzer2():
        numpixels = 0
        global capture
        global current_frame
        
        #delete capture or start capture from begining
        del capture
        capture = cvCaptureFromAVI(filestr)
        #acquire image from video frame
        frame = cvQueryFrame(capture)
        #threshold
        threshframe = thresh(frame)
        #apply ROI
        
        #initialization (user click)
        
        #background subtraction -> establish background frame

        #analyzer loop - for each frame in video
        while current_frame <= int(num_frames)-1:
                current_frame = cvGetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES) #get current frame number
                print "CURRENT FRAME=", current_frame
                print "HAHAHAHHHAHAHAhAHAHAHAHAHAHAHAHAH"
                frame = cvQueryFrame(capture)
                if frame == None: break

                #threshold
                threshed_frame = thresh(frame)
                print "SPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAMSPAM"

                #
                #tracking(threshed_frame)
                print "MMMMMWMMMMMMMWMMMMMMWMMMMMMMWMMMMMMM"
        


                #threshold
                #background subtract
                #use sensitivity radius
                #detect object
                #find center (x,y) -> store
                #find displacement (pix) -> store
                #recalculate radius
                
                #display original frame with overlay
                dispframe = threshed_frame.as_pil_image()
                ApImage = ImageTk.PhotoImage(dispframe)
                can.create_image(320,240, image=ApImage)

        
def menu_load_video():
        global capture
        global num_frames
        global ApImage
        global filestr
        del_cap()
        filestr = tkFileDialog.askopenfilename(title='Please select avi:', filetypes = [('avi files', '.avi')])
        capture = cvCaptureFromAVI(filestr)
        num_frames = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT)
        vid_fps = cvGetCaptureProperty(capture, CV_CAP_PROP_FPS)
        vid_length = round((num_frames/float(vid_fps))/float(60),3)
        print "NUMBER OF FRAMES =", num_frames
        filestrsplit = filestr.rsplit('/', 1)
        l_video_name2.config(text=filestrsplit[1])
        l_video_length2.config(text=vid_length)
        l_video_frames2.config(text=num_frames)

        cvSetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES, 1)
        frame = cvQueryFrame(capture)
        dispframe = frame.as_pil_image()
        ApImage = ImageTk.PhotoImage(dispframe)
        can.create_image(320,240, image=ApImage)
        print "XXXXXXXXXXXXXXXXXXXXXXX"

def menu_saveconfig():
        pass

def menu_loadconfig():
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
sc_threshold1 = Scale(rootwindow, from_=0, to=256, orient=HORIZONTAL, resolution=1, showvalue = YES)
sc_threshold1.set(53)
rb_threshold2 = Radiobutton(rootwindow, text="Value Thresholding", variable=v_threshold, value=2)

v_threshold.set(1)

b_prevthreshold = Button(rootwindow, text="Preview Threshold", command=bf_previewthreshold)

### Target Identification
l_targetid = Label(rootwindow, text="Target Identification:")
v_targetid = IntVar()

rb_targetid1 = Radiobutton(rootwindow, text="Manual", variable=v_targetid, value=1)
rb_targetid2 = Radiobutton(rootwindow, text="Automatic", variable=v_targetid, value=2)
rb_targetid3 = Radiobutton(rootwindow, text="Full Auto(Experimental)", variable=v_targetid, value=3)

v_targetid.set(1)

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
