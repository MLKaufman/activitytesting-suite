#! /usr/bin/python
#AVI2POINTS program Grabbing Data from Video for future analysis

from Tkinter import *
import tkFileDialog
import os, thread, datetime, string
from ctypes_opencv import *
from math import *
from a2p_bfuncs import *
import tkMessageBox

#Colors
color_red = cvScalar (0, 0, 255, 0)
color_green = cvScalar (0, 255, 0, 0)
color_blue = cvScalar (255,0,0,0)

#Default SavePath
#savepath = str(os.getcwd()) + "\\"
savepath = "C:\Users\Jack\Desktop"


manual_approix = cvPoint(120,32)
manual_approiy = cvPoint(534,445)

def menu_loadvideo():
    filestr = tkFileDialog.askopenfilenames(title='Choose a file', filetypes = [('avi files', '.avi')])
    filestrtemplist = filestr.split(' {')
    print filestrtemplist
    for each in filestrtemplist:
        each = each.strip('{')
        each = each.strip('}')
        splittemp = each.rsplit('/', 1)
        filename = splittemp[1]
        lb_mainlist.insert(END, (filename, each))

    if lb_mainlist.size() > 0:
        lb_mainlist.selection_set(0)

def del_lbitem(self):

	lbitemtemp = lb_mainlist.curselection()
	itemtodelete = int(lbitemtemp[0])
	lb_mainlist.delete(itemtodelete)

def debug_viewimage(name, img):
    cvNamedWindow(name, 1)
    cvShowImage(name,img)
    cvWaitKey(1)
    cvDestroyWindow(name)

def bf_savepath():
    global savepath
    filestr = tkFileDialog.askdirectory()
    savepath = filestr + "/"
    l_cwd.config(text=savepath)

def f_cap_properties(capfile):
        capture = cvCaptureFromAVI(capfile)
        #capture video properties
        vidprop_numframes = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT)
        vidprop_fps = cvGetCaptureProperty(capture, CV_CAP_PROP_FPS)
        vidprop_width = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_WIDTH)
        vidprop_height = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_HEIGHT)

        del(capture)
        return vidprop_numframes, vidprop_fps, vidprop_width, vidprop_height

def f_detect_apparatus(videofile):
    capture = cvCaptureFromAVI(videofile)
    cvSetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES, 150) #Set Apparatus Image Capture Location
    detectapp_image = cvQueryFrame(capture)

    #Detect Possible Apparatus
    squares = findsquares(detectapp_image, thresh)
    i=0
    sqr_arr = squares.asarray(CvPoint)
    square_list = []
    while i<squares.total:
        # read 4 vertices + Create list of rectangles
        square_list.append(cvRect(sqr_arr[i].x,sqr_arr[i].y,sqr_arr[i+2].x,sqr_arr[i+2].y))
        i+=4
        
    working_square_list = list(square_list)
    print "Number of Options = ", len(working_square_list)
    print "Working List = ", working_square_list

    #Apparatus classifier
    
    #while len(working_square_list)>1:
    for pos_apparatus in working_square_list:
        # check for squares that are as big as image
        if (pos_apparatus.width * pos_apparatus.height) > (detectapp_image.width * detectapp_image.height) - (.025 * (detectapp_image.width * detectapp_image.height)):
            working_square_list.remove(pos_apparatus) #remove square thats almost as large as the image itself

    print "SQ2 Elimation Round 1 Complete, Remaining Contestants: ", working_square_list

    #check if square is actually square and not a rectangle
    for pos_apparatus in working_square_list:
        if abs(pos_apparatus.width - pos_apparatus.height) > 25:
            working_square_list.remove(pos_apparatus)
    print "SQ2 Elimation Round 2 Complete, Remaining Contestants: ", working_square_list

    #rule out minimum size
    for pos_apparatus in working_square_list:
        if (pos_apparatus.width * pos_apparatus.height) < 500:
            working_square_list.remove(pos_apparatus)
    print "SQ2 Elimation Round 3 Complete, Remaining Contestants: ", working_square_list

    #check x y offset
    for pos_apparatus in working_square_list:
        if pos_apparatus.x > 350:
            working_square_list.remove(pos_apparatus)
        if pos_apparatus.y > 350:
            working_square_list.remove(pos_apparatus)
    print "SQ2 Elimation Round 4 Complete, Remaining Contestants: ", working_square_list

    #detect if any points of the apparatus box are outside bounds of the image
    #TODO
    
    #compare remaining possibilities
    current_area = 0
    for pos_apparatus in working_square_list:
        if (pos_apparatus.width * pos_apparatus.height) > current_area:
            current_area = (pos_apparatus.width * pos_apparatus.height)
            current_choice = pos_apparatus

    del(capture) #delete capture stream
    try:
        current_choice.x = current_choice.x + 7
        current_choice.y = current_choice.y + 1
        current_choice.width = current_choice.width - 3
        current_choice.height = current_choice.height - 3
    except UnboundLocalError:
        working_square_list = list(square_list)
        current_choice = working_square_list[0]
    return current_choice

def event_calibration(event,x,y,flag,e):
    global manual_approix
    global manual_approiy
    
    if event == CV_EVENT_LBUTTONDOWN:
        manual_approix = cvPoint(x,y)
        
    if event == CV_EVENT_RBUTTONDOWN:
        manual_approiy = cvPoint(x,y)

def f_manual_detect_apparatus(videofile):
    global manual_approix
    global manual_approiy
    
    capture = cvCaptureFromAVI(videofile)
    cvSetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES, 150) #Set Apparatus Image Capture Location
    detectapp_image = cvQueryFrame(capture)
    preview_image = cvCreateImage(cvGetSize(detectapp_image),8,3)

    acquired_apparatus = False

    while acquired_apparatus == False:
        cvCopy(detectapp_image, preview_image)
        
        cvNamedWindow(videofile, 1)
        cvDrawRect(preview_image, manual_approix, manual_approiy, color_red)
        cvShowImage(videofile, preview_image)
        keypress = cvWaitKey(0)
        cvDestroyWindow(videofile)

        if keypress == 27: #ESC Need to grab points
            cvCopy(detectapp_image, preview_image)
            
            cvNamedWindow(videofile, 1)
            cvShowImage(videofile, preview_image)
            cvSetMouseCallback(videofile, event_calibration)
            cvWaitKey(0)
            cvDestroyWindow(videofile)

        if keypress == 13: #Enter
            acquired_apparatus = True

    return cvRect(manual_approix.x, manual_approix.y, manual_approiy.x, manual_approiy.y)

def f_grabframe(inputfeed):
    
    #Create Image Space
    bwframe = cvCreateImage(cvGetSize(inputfeed), IPL_DEPTH_8U ,1)
    threshframe = cvCreateImage(cvGetSize(inputfeed), IPL_DEPTH_8U ,1)

    cvConvertImage(inputfeed, bwframe, 0) #Convert feed to BW Images

    if v_appcon.get() == 1: #white object - black background
            cvThreshold(bwframe, threshframe, sc_threshold1.get(), 256, CV_THRESH_BINARY)

    if v_appcon.get() == 2: #black object - white background
            cvThreshold(bwframe, threshframe, sc_threshold1.get(), 256, CV_THRESH_BINARY_INV)

    return threshframe

def f_trackobject(image, apparatus):
    print "Original Apparatus Rect:", apparatus

    roirect = cvRect(apparatus.x, apparatus.y, abs(apparatus.width-apparatus.x), abs(apparatus.height-apparatus.y))
    print "Rect for ROI:", roirect
    
    #debug_viewimage("Track pre-ROI", image)
    cvSetImageROI(image,roirect)

    #erode/dilate image to get rid of erroneous pixels
    cvErode(image, image,0, 1)
    cvDilate(image, image,0,1)
    
    #debug_viewimage("Track Post-ROI", image)

    storage = cvCreateMemStorage(0)#create storage space for contours

    #intial FindContours, get num-contours
    contours_num, b = cvFindContours(image, storage)
    print "Contours Found: ", contours_num

    #Start Contour Scanner (image, storage, header, mode, method, offset)
    contour_scanner = cvStartFindContours(image, storage)#, mode=CV_RETR_EXTERNAL)
    contour_stillpresent = 1

    #Keep Track of Largest Contour
    contour_largest = (0, 0)

    #main Contour Scanner Loop
    while contour_stillpresent == 1:
        contour_sequence = cvFindNextContour(contour_scanner)

        if contour_sequence == None:
            contour_stillpresent = 0
            #cvEndFindContours(contour_scanner)
            break

        else:
            #Get Area of Contour
            contour_area = abs(cvContourArea(contour_sequence))
                #Compare to current Largest contour
            if contour_area > contour_largest[1]:
                contour_largest = (contour_sequence, contour_area)
            else:
                pass


    if contour_largest[1] == 0:
        return cvPoint(0, 0), 0
    else:
        #Track Objects
        #TODOCalculate Area Points for Overlap with Thigmotaxic Area
        print "AREA", contour_largest[1]

        #Calculate Center of Mass for Distanced Traveled Activity
        contour_minarearect = cvMinAreaRect2(contour_largest[0])
        print "AREA MIN RECT:", contour_minarearect
        print "Total", contour_largest[0].total

        return cvPoint(contour_minarearect.center.x, contour_minarearect.center.y), contour_largest[0]


def bf_preview_settings():
    itemtemp = lb_mainlist.get(lb_mainlist.curselection())

    apparatus_coords = f_detect_apparatus(itemtemp[1]) #get apparatus coords

    capture = cvCaptureFromAVI(itemtemp[1])
    cvSetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES, 1349) #advance 150 frames
    detectapp_image = cvQueryFrame(capture) #grab image frame for detecting apparatus

    #cvSetImageROI(detectapp_image, current_choice)
    
    #create storage image frames
    frame_bw = cvCreateImage(cvGetSize(detectapp_image), IPL_DEPTH_8U ,1)
    frame_threshed = cvCreateImage(cvGetSize(detectapp_image), IPL_DEPTH_8U ,1)
    frame_threshed_color = cvCreateImage(cvGetSize(detectapp_image), IPL_DEPTH_8U ,3)

    cvConvertImage(detectapp_image, frame_bw, 0) #convert raw input frame to black and white
    cvThreshold(frame_bw, frame_threshed, sc_threshold1.get(), 256, CV_THRESH_BINARY) #threshold frame

    cvConvertImage(frame_threshed, frame_threshed_color, 0)

    #Tracking and Object Selectio: detect coords and return contour
    try:
        obj_coords, obj_contour = f_trackobject(frame_threshed, apparatus_coords)
        print "OBJECT COORDS:", obj_coords
    except:
        tkMessageBox.showinfo("Error", "COULD NOT TRACK OBJECT")
 
    #Create Output, Convert back to color image
    image_output = cvCreateImage(cvGetSize(frame_threshed_color),IPL_DEPTH_8U,3)
    cvConvertImage(frame_threshed_color, image_output, 0)

    cvNamedWindow(itemtemp[0], 1)
    pointvector1 = cvPoint(apparatus_coords.x, apparatus_coords.y)
    pointvector2 = cvPoint(apparatus_coords.width, apparatus_coords.height)
    cvRectangle(image_output, pointvector1, pointvector2, color_red, 3)

    #Object Poly
    #cvDrawPoly(image_output, obj_contour, color_blue, 3)
    #cvDrawContours(image_output, obj_contour, color_blue, color_green, 100)
    obj_appadj = cvPoint(obj_coords.x+apparatus_coords.x, obj_coords.y+apparatus_coords.y)
    cvCircle(image_output, obj_appadj, 17, color_blue, 2)
    #disabling drawing contour, no way to draw the contour with offset
    #cvDrawContours(image_output, obj_contour, color_blue , color_red, 100, 2, 1)

    del(capture)
    cvShowImage(itemtemp[0],image_output)
    cvWaitKey(0)
    cvDestroyWindow(itemtemp[0])

def dc_preview_settings(self): #preview of settings via double clicking
    bf_preview_settings()

def bf_preview_all():
    currentfile = 0
    
    num_filestoprocess = lb_mainlist.size()
    for each in range(num_filestoprocess):
        lb_mainlist.selection_clear(0, lb_mainlist.size())
        lb_mainlist.selection_set(currentfile)
        bf_preview_settings()
        currentfile+=1
        
def bf_startanalysisthread():
    thread.start_new_thread(testbf_beginanalysis, ("Analysis Thread",1))
    
def testbf_beginanalysis(name, number):
    global savepath
    #Define Analysis Process #Error Checking
    
    #Grab Number of Files to Process
    num_filestoprocess = lb_mainlist.size()

    #Disable analysis button
    b_beginanalysis.configure(state=DISABLED)

    #Establish Output Folder
    str_datetime = string.replace(str(datetime.datetime.now()),':','-') #get date time
    output_folder = str(savepath) + "Trial Data " + str_datetime + "/"
    os.mkdir(output_folder)
    savepath = output_folder
    
    currentfile = 0
    for each in range(num_filestoprocess):
        itemtemp = lb_mainlist.get(currentfile) #select file in lb
        lb_mainlist.selection_clear(0,lb_mainlist.size())
        lb_mainlist.selection_set(currentfile)

        if v_appselection.get() == 1:
            apparatus_coords = f_detect_apparatus(itemtemp[1])
        elif v_appselection.get() == 2:
            pass
        elif v_appselection.get() == 3: #MANUAL SELECTION
            apparatus_coords = f_manual_detect_apparatus(itemtemp[1])

        #capture and return Capture Properties of Video sFile
        vidprop_numframes, vidprop_fps, vidprop_width, vidprop_height = f_cap_properties(itemtemp[1])

        #For real this time
        savefilenameandpath = str(savepath) + str(string.replace(itemtemp[0],'.avi','.a2p'))
        f = open(savefilenameandpath, 'w')         #create Save File
        #Save Video stats to File
        #AviLocation/Name,FPS,width,height,length,apparatusroi
        roioffset = "(" + str(apparatus_coords.x) + "," + str(apparatus_coords.y) + "," + str(apparatus_coords.width) + "," + str(apparatus_coords.height) + ")"

        #vidprop_statstring = str(itemtemp[1]) + "," + savepath + "," + roioffset + "," + str(vidprop_numframes) + "," + str(vidprop_fps) +"\n"
        vidprop_statstring = str(itemtemp[1]) + "," + str(vidprop_numframes) + "," + str(vidprop_fps) + "," + str(vidprop_width) + "," + str(vidprop_height) + "," + str(vidprop_numframes/vidprop_fps) + "," + roioffset + "\n"
        print "Writing to File:", vidprop_statstring
        f.write(vidprop_statstring)

        current_frame = 0

        #initiate tracking
        capture = cvCaptureFromAVI(itemtemp[1])
        print "Processing File: ", itemtemp[0]

        l_progress.config(background ="green", text="Progress:  " + str(currentfile+1) + "/" + str(lb_mainlist.size()) +"    " + "0%")

        while current_frame < vidprop_numframes:
            current_frame+=1
            print "Processing Frame #", current_frame, " of ", vidprop_numframes
            image_grab = cvQueryFrame(capture)
            image_frame = f_grabframe(image_grab)
            #debug_viewimage("Image Frame", image_frame)
            try:
                obj_point, obj_contour = f_trackobject(image_frame, apparatus_coords)
                if obj_contour == 0:
                    obj_point = lastknown_obj_point
                    obj_contour = lastknown_obj_contour
                else:
                    lastknown_obj_point = obj_point
                    lastknown_obj_contour = obj_contour
                    
            except WindowsError:
                print "exception thrown bad frame"
                obj_point = cvPoint(0,0)
                del(capture)
                capture = cvCaptureFromAVI(itemtemp[1])
                cvSetCaptureProperty(capture, CV_CAP_PROP_POS_FRAMES, current_frame)
                
            obj_pointstr = str(current_frame) + "," + str(obj_point.x) + "," + str(obj_point.y) + "\n"
            f.write(obj_pointstr) #write x,y to file
            l_progress.config(background ="green", text="Progress:  " + str(currentfile+1) + "/" + str(lb_mainlist.size()) +"    " + str(round(current_frame/vidprop_numframes*100)) + "%")

        #display run image
        del(capture)
        cvSaveImage(str(savepath) + str(string.replace(itemtemp[0],".avi",".jpg")), image_grab)
        currentfile += 1
        f.close()
        b_beginanalysis.configure(state=NORMAL)

############ ROOT WINDOW GUI #############
rootwindow = Tk()
rootwindow.title("Activity 2 Points Video Analyzer v.9 - Michael Kaufman 2010")
rootwindow.geometry("400x410+300+100")
#rootwindow.wm_iconbitmap('rat.ico')

###GUI FEATURES
menubar = Menu(rootwindow)
#create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Load Video Files", command=menu_loadvideo)
#filemenu.add_command(label="Load Video Folder", command=menu_loadfolder)
filemenu.add_separator()
filemenu.add_command(label="Save Config Data", command=menu_saveconfig)
filemenu.add_command(label="Load Config Data", command=menu_loadconfig)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=rootwindow.quit)
menubar.add_cascade(label="File", menu=filemenu)

#Options


#FileList #listbox
l_filestoprocess = Label(text = "Files to Process:")
l_filestoprocess.place(x = 0, y = 0)
lb_mainlist = Listbox(rootwindow, height=20, width=25)
lb_mainlist.bind("<BackSpace>", del_lbitem)
lb_mainlist.bind("<Double-Button-1>", dc_preview_settings)
lb_mainlist.bind("<Return>", dc_preview_settings)
lb_mainlist.place(x = 0, y = 20)

#Zone Scroll Bar
sb_listscroll = Scrollbar(rootwindow)
sb_listscroll.place(x = 160, y = 50)
lb_mainlist.config(yscrollcommand=sb_listscroll.set)
sb_listscroll.config(command=lb_mainlist.yview)

#Options
#1 Apparatus Selection
l_appselection = Label(rootwindow, text = "(1) Apparatus Selection:")
l_appselection.place(x = 200, y = 10)
v_appselection = IntVar()

rb_appselection1 = Radiobutton(rootwindow, text="Auto - Box", variable=v_appselection, value=1)
rb_appselection1.place(x = 220,y=30)
rb_appselection2 = Radiobutton(rootwindow, text="Auto - Water Maze", variable=v_appselection, value=2)
rb_appselection2.place(x = 220,y=50)
rb_appselection3 = Radiobutton(rootwindow, text="Manual Selection", variable=v_appselection, value=3)
rb_appselection3.place(x = 220,y=70)

v_appselection.set(1)

#2 Thresholding
l_thresholding = Label(rootwindow, text = "(2) Thresholding:")
v_appcon = IntVar()
rb_appcon1 = Radiobutton(rootwindow, text="Light Object", variable=v_appcon, value=1)
rb_appcon2 = Radiobutton(rootwindow, text="Dark Object", variable=v_appcon, value=2)
v_appcon.set(1)
l_thresholding.place(x = 200, y = 110)
rb_appcon1.place(x=220 , y=130)
rb_appcon2.place(x=220 , y=150)
sc_threshold1 = Scale(rootwindow, from_=1, to=256, orient=HORIZONTAL, resolution=1, showvalue = YES)
sc_threshold1.set(45)
sc_threshold1.place(x=220,y=175)#25

#3 Output Options
l_output = Label(rootwindow, text = "(3) Output Options:")
l_output.place(x = 200, y = 230)#180
b_savepath = Button(rootwindow, text = "SET SAVE PATH", command=bf_savepath)
b_savepath.place(x=230, y = 250)#200
l_pathlabel = Label(rootwindow, text="Current Save Directory:")
l_pathlabel.place(x=0, y=370)
l_cwd = Label(rootwindow,  font=("Helvetica",7), text = os.getcwd())
l_cwd.place(x=0, y=390)


#Buttons
b_preview = Button(text="Preview", command=bf_preview_settings)
b_preview.place(x=190,y=320)
b_preview = Button(text="Preview ALL", command=bf_preview_all)
b_preview.place(x=260,y=320)
b_beginanalysis = Button(text="ANALYZE!", command=bf_startanalysisthread)
b_beginanalysis.place(x = 235, y = 350)

#Progress Bar
l_progress = Label(rootwindow, text = " ")
l_progress.place(x=0,y=345)

rootwindow.config(menu=menubar)# display the menu
rootwindow.mainloop()
