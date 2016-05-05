
###OLD STUFF NOT USED
class Apparatus_Box():
    thigmo_options = {'grid': (1,2), 'box': 4139}
    def __init__(self, upperleft, upperright, lowerleft, lowerright, thigmotype):
        self.upperleft = upperleft
        self.upperright = upperright
        self.lowerleft = lowerleft
        self.lowerright = lowerright
        self.thigmotaxia = self.thigmo_options[thigmotype]

    def __print__(self):
        print "Apparatus Stats:", upperleft, upperright, lowerleft, lowerright

    def manualboxcoords(self, upperleft, upperright, lowerleft, lowerright):
        self.upperleft = upperleft
        self.upperright = upperright
        self.lowerleft = lowerleft
        self.lowerright = lowerright




def menu_loadfolder():

    filestr = tkFileDialog.askdirectory()
    filestrlist = os.listdir(filestr)
    for file in filestrlist:
        print file
        if file.endswith( ".avi" ):
            lb_mainlist.insert(END, (file, filestr + file))


class Thigmotaxia():
    type_dict = {'grid': (), 'box': 4139}
    def __init__(self, type, options):
        self.thigmotype = type_dict[type]




def process_file(filenumber):
    capture = cvCaptureFromAVI(filetocap[1])
    cvSetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT, 150)
    image_calibration = cvQueryFrame(capture)
    readytomoveon = False

    while readytomoveon == False:
        #zero out grabbing of ROI coords
        roirect = cvRect(x=roix1,y=roiy1,width=roix2,height=roiy2)

        #display current analysis window
        named_window = str(filetocap[0]) + " Preview; ESC-Edit Enter-Continue"
        cvSetImageROI(image_calibration, roirect)
        cvDrawRect(image_calibration, CvPoint(roi_thigmoULx,roi_thigmoULy), CvPoint(roi_thigmoLRx,roi_thigmoLRy), color_red)

        cvNamedWindow(named_window, 1) #create calibration window
        cvShowImage(named_window, image_calibration)
        cvSetMouseCallback(named_window,event_calibration0)
        keypress = cvWaitKey(0)
        cvDestroyWindow(named_window)
        print keypress

        if keypress == 27: # ESC

            #Apparatus Calibration/Set ROI/Thigmotaxia
            #named_window = str(filetocap[0]) + " Calibration"
            #cvNamedWindow(named_window, 1) #create calibration window

            #ROI Calibration
            image_calibration = cvQueryFrame(capture)
            named_window = str(filetocap[0]) + " ROI Calibration"
            cvNamedWindow(named_window, 1) #create calibration window
            cvShowImage(named_window, image_calibration)
            cvSetMouseCallback(named_window,event_calibration1)
            print "ROI CALIBRATION"
            cvWaitKey(0)
            cvDestroyWindow(named_window)

            roirect = cvRect(x=roix1,y=roiy1,width=roix2,height=roiy2)

            #Thigo Calibration
            image_calibration = cvQueryFrame(capture)
            named_window = str(filetocap[0]) + " Thigmo Calibration"
            cvSetImageROI(image_calibration, roirect)
            cvNamedWindow(named_window, 1) #create calibration window
            cvShowImage(named_window, image_calibration)
            cvSetMouseCallback(named_window,event_calibration2)
            print "Thigo CALIBRATION"
            cvWaitKey(0)
            cvDestroyWindow(named_window)

            """#ThigmoPreview
            cvSetImageROI(image_calibration, roirect)
            cvDrawRect(image_calibration, CvPoint(roi_thigmoULx,roi_thigmoULy), CvPoint(roi_thigmoLRx,roi_thigmoLRy), color_red)
            cvNamedWindow(named_window, 1) #create calibration window
            cvShowImage(named_window, image_calibration)
            print "THIGMO PREVIEW"
            cvWaitKey(1000)
            cvWaitKey(0)
            cvDestroyWindow(named_window)"""

        if keypress == 13: # Enter
            readytomoveon = 1

    cvDestroyWindow(named_window)


    





















def isinpoly(centerpoint):
    x = centerpoint.x
    y = centerpoint.y
    poly = roi_thigmo_rectpoly
    #print poly, "X", x, "Y", y
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

def setroipoints():
    global roirect
    global roirectpoly
    global roi_thigmo_rect
    global roi_thigmo_rectpoly

    roirect = cvRect(x=roix1,y=roiy1,width=roix2,height=roiy2)
    roirectpoly = [(roix1, roiy1), (roix2, roiy1), (roix2, roiy2), (roix1, roiy2)]

    roi_thigmo_rect = cvRect(roi_thigmoULx, roi_thigmoULy, roi_thigmoLRx, roi_thigmoLRy)
    roi_thigmo_rectpoly = [(roi_thigmoULx, roi_thigmoULy), (roi_thigmoLRx, roi_thigmoULy), (roi_thigmoLRx, roi_thigmoLRy), (roi_thigmoULx, roi_thigmoLRy)]

def event_calibration0(event,x,y,flag,e):
    if event == 1: #Left Mouse Button Has Fired
        print "coords:", x, ",", y

def event_calibration1(event,x,y,flag,e):
    global roix1
    global roiy1
    global roix2
    global roiy2
    global roi_needupperleft
    global roi_needlowerright

    if event == 1: #Left Mouse Button Has Fired
        if roi_needupperleft == 0:
            roix1 = x
            roiy1 = y
            print "UL", x, ",", y
            roi_needupperleft = 1

        else:
            if roi_needlowerright == 0:
                roix2 = x - roix1
                roiy2 = y - roiy1
                print "LR", x, ",", y
                roi_needlowerright = 1

def event_calibration2(event,x,y,flag,e):
    global roi_thigmoULx
    global roi_thigmoULy
    global roi_thigmoLRx
    global roi_thigmoLRy
    global roi_thigmoUL
    global roi_thigmoLR

    if event == 1: #Left Mouse Button Has Fired
        if roi_thigmoUL == 0:
            roi_thigmoULx = x + (thigmo_distance * pixtocm_ratio)
            roi_thigmoULy = y + (thigmo_distance * pixtocm_ratio)
            print "roi_thigmoUL", x, ",", y
            roi_thigmoUL = 1
        else:
            if roi_thigmoLR == 0:
                roi_thigmoLRx = x - (thigmo_distance * pixtocm_ratio)
                roi_thigmoLRy = y - (thigmo_distance * pixtocm_ratio)
                print "roi_thigmoLR", x, ",", y
                roi_thigmoLR = 1

def preview_analysis_window(filetocap):
    global roi_needupperleft
    global roi_needlowerright
    global roi_thigmoUL
    global roi_thigmoLR
    global roi_thigmoULx
    global roi_thigmoULy
    global roi_thigmoLRx
    global roi_thigmoLRy

    capture = cvCaptureFromAVI(filetocap[1])
    cvSetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT, 150)
    image_calibration = cvQueryFrame(capture)
    readytomoveon = False

    while readytomoveon == False:
        #zero out grabbing of ROI coords
        roi_needupperleft = 0
        roi_needlowerright = 0
        roi_thigmoUL = 0
        roi_thigmoLR = 0

        roirect = cvRect(x=roix1,y=roiy1,width=roix2,height=roiy2)

        #display current analysis window
        named_window = str(filetocap[0]) + " Preview; ESC-Edit Enter-Continue"
        cvSetImageROI(image_calibration, roirect)
        cvDrawRect(image_calibration, CvPoint(roi_thigmoULx,roi_thigmoULy), CvPoint(roi_thigmoLRx,roi_thigmoLRy), color_red)

        cvNamedWindow(named_window, 1) #create calibration window
        cvShowImage(named_window, image_calibration)
        cvSetMouseCallback(named_window,event_calibration0)
        keypress = cvWaitKey(0)
        cvDestroyWindow(named_window)
        print keypress

        if keypress == 27: # ESC

            #Apparatus Calibration/Set ROI/Thigmotaxia
            #named_window = str(filetocap[0]) + " Calibration"
            #cvNamedWindow(named_window, 1) #create calibration window

            #ROI Calibration
            image_calibration = cvQueryFrame(capture)
            named_window = str(filetocap[0]) + " ROI Calibration"
            cvNamedWindow(named_window, 1) #create calibration window
            cvShowImage(named_window, image_calibration)
            cvSetMouseCallback(named_window,event_calibration1)
            print "ROI CALIBRATION"
            cvWaitKey(0)
            cvDestroyWindow(named_window)

            roirect = cvRect(x=roix1,y=roiy1,width=roix2,height=roiy2)

            #Thigo Calibration
            image_calibration = cvQueryFrame(capture)
            named_window = str(filetocap[0]) + " Thigmo Calibration"
            cvSetImageROI(image_calibration, roirect)
            cvNamedWindow(named_window, 1) #create calibration window
            cvShowImage(named_window, image_calibration)
            cvSetMouseCallback(named_window,event_calibration2)
            print "Thigo CALIBRATION"
            cvWaitKey(0)
            cvDestroyWindow(named_window)

            """#ThigmoPreview
            cvSetImageROI(image_calibration, roirect)
            cvDrawRect(image_calibration, CvPoint(roi_thigmoULx,roi_thigmoULy), CvPoint(roi_thigmoLRx,roi_thigmoLRy), color_red)
            cvNamedWindow(named_window, 1) #create calibration window
            cvShowImage(named_window, image_calibration)
            print "THIGMO PREVIEW"
            cvWaitKey(1000)
            cvWaitKey(0)
            cvDestroyWindow(named_window)"""

        if keypress == 13: # Enter
            readytomoveon = 1

    cvDestroyWindow(named_window)

def bf_beginanalysis():
    global num_filestoprocess
    global currentfile

    num_filestoprocess = lb_mainlist.size()
    print "Total Files to Process: " , num_filestoprocess
    currentfile = 1
    max_frames = 1800
    for each in range(num_filestoprocess):
        itemtemp = lb_mainlist.get(currentfile-1)
        preview_analysis_window(itemtemp)
        processnext(currentfile-1, num_filestoprocess, max_frames)
        currentfile += 1

def processnext(filetoprocess, numberoffiles, max_frames):
    itemtemp = lb_mainlist.get(filetoprocess)
    print "Processing File#: ", filetoprocess+1, "/", numberoffiles
    print itemtemp[1]
    capture = cvCaptureFromAVI(itemtemp[1])

    max_frames = 1800 #Max Frames to Analyze @ 15 FPS

    #Get Number of Frames
    num_frames = cvGetCaptureProperty(capture, CV_CAP_PROP_FRAME_COUNT)
    print "Num Frames", num_frames
    #Frame Increment
    frame_increment = 1

    #Create Memory Storage
    storage = cvCreateMemStorage(0)

    #Set ROI points
    setroipoints()

    #initialize tracking
    object_distancetraveled = 0
    time_in_center = 0
    isinside = False
    thisx = 0
    thisy = 0
    lastx = 0
    lasty = 0
    firstrun = 0

    while frame_increment <= max_frames:
        print "Frame: ", frame_increment, "/", num_frames
        frame_raw = cvQueryFrame(capture)

        #set ROI on raw frame
        cvSetImageROI(frame_raw, roirect)
        print "ROI RECT:", roirect
        #Create Image Spaces
        frame_bw = cvCreateImage(cvGetSize(frame_raw), IPL_DEPTH_8U ,1)
        frame_threshed = cvCreateImage(cvGetSize(frame_raw), IPL_DEPTH_8U ,1)

        cvConvertImage(frame_raw, frame_bw, 0) #convert raw input frame to black and white
        cvThreshold(frame_bw, frame_threshed, 55, 256, CV_THRESH_BINARY) #threshold frame

        #Create Output
        image_output = cvCreateImage(cvGetSize(frame_raw),8,3)
        cvNamedWindow("Trial Output:", 1)

        #intial FindContours, get num-contours
        contours_num, b = cvFindContours(frame_threshed, storage)

        print "Contours Found: ", contours_num

        #Start Contour Scanner (image, storage, header, mode, method, offset)
        contour_scanner = cvStartFindContours(frame_threshed, storage, mode=CV_RETR_EXTERNAL)
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

        #Track Objects
        #Calculate Area Points for Overlap with Thigmotaxic Area
        print "AREA", cvContourArea(contour_largest[0])

        #Calculate Center of Mass for Distanced Traveled Activity
        contour_minarearect = cvMinAreaRect2(contour_largest[0])
        print contour_minarearect
        print "Total", contour_largest[0].total

        minx = contour_minarearect.center.x
        miny = contour_minarearect.center.y

        #Distance Traveled
        thisx = minx
        thisy = miny
        xpoints = thisx - lastx
        ypoints = thisy - lasty
        print thisx
        print lastx
        #cvWaitKey(0)
        if firstrun == 0:
            print "First run!"
            firstrun = 1
        else:
            print "XPOINTS", xpoints, "YPOINTS", ypoints
            thisdistance = sqrt(pow(xpoints,2)+pow(ypoints,2))
            print thisdistance
            if thisdistance > 500 or thisdistance <= 0:
                thisx = lastx
                thisy = lasty
            #elif thisx < roix1 or thisx > roix2 or thisy < roiy1 or thisy > roiy2:
             #   thisx = lastx
              #  thisy = lasty
            else:
                object_distancetraveled += thisdistance
                lastx = thisx
                lasty = thisy
                #Thigmotaxia
                isinside = isinpoly(contour_minarearect.center) #Check if Location is inside Thigma

                print "INSIDE: ", isinside
                if isinside == True:
                                time_in_center += .066666666
        #Draw Objects and Frame
        cvWaitKey(1000)
        cvCopy(frame_raw, image_output)
        cvDrawContours(image_output, contour_largest[0], color_blue , color_red, 100, 2, 1) #offset=cvPoint(roix1,roiy1)
        #cvRectangle(image_output, cvPoint(100,100), cvPoint(200,200), cvScalar(255,0,0), 1)
        if isinside == False:
            cvCircle(image_output, cvPoint(contour_minarearect.center.x,contour_minarearect.center.y), 2, color_red, 7)
        if isinside == True:
            cvCircle(image_output, cvPoint(contour_minarearect.center.x,contour_minarearect.center.y), 2, color_green, 7)
        cvDrawRect(image_output, CvPoint(roi_thigmoULx,roi_thigmoULy), CvPoint(roi_thigmoLRx,roi_thigmoLRy), color_red)
        cvShowImage("Trial Output", image_output)
        cvWaitKey(1000)
        frame_increment += 1
    print "DISTANCE TRAVELED", object_distancetraveled/3.43, " cm"
    print "Time in Center", time_in_center, " seconds"
    write_buffer = str(itemtemp[0]) + " Distance Traveled: " + str(object_distancetraveled)+ " Time in Center: "+ str(time_in_center) +"\n"
    f = open(foutput, 'a')
    f.write(write_buffer)
    f.close()
