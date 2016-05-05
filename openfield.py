#! /usr/bin/env python
from Tkinter import *
from math import *
import sys
import os, thread, datetime, string
import PIL
from PIL import Image, ImageTk
#from ctypes_opencv import *
import os
import tkFileDialog
#import tkMessageBox

print("Open Field Analyzer - Michael Kaufman 2010")

numpixels = 0 #Number of Pixels

#calc thigmotaxia
#340 pix per 100 cm
#3.4 pix per cm
#how many cm square box do you want?
thig_sq_boxcm = 85
thig_sq_box = thig_sq_boxcm * 3.4

#MOVEMENT/DISTANCE SENSITIVTY In Pix
maxmove = 5 * 3.4
minmove = 1 * 3.4

capture = 0
current_frame = 0

def menu_saveconfig():
    pass

def menu_loadconfig():
    pass

def menu_load_files():
    bf_load_files()

def bf_mansetrect():
    global grabbing_points
    global got_firstpoint
    grabbing_points = True
    got_firstpoint = False
    
    
def bf_mansetcircle():
    pass

def refresh_canvas():
    global can
    #load image -> send to canvas -> view
    #load trial properties
    #draw roi/apparatus image

    itemtemp = lb_mainlist.get(lb_mainlist.curselection())
    f = open(itemtemp[1], 'r')
    infoline = f.readline()
    infolist = infoline.split(',')
    f.close
    print itemtemp
    print itemtemp[1].replace('.a2p','.jpg')
    print infolist
    #0-avifile location 1-frames 2-fps 3-imagewidth 4-imageheight 5-length in seconds 6-apparatus roi coords

    resolution = infolist[3] + "x" + infolist[4]
    l_trial_name2.config(text=resolution)
    l_trial_fps2.config(text=infolist[2])
    l_trial_length2.config(text=infolist[5])

    #Load image and display
    imagefile = itemtemp[1].replace('.a2p','.jpg')
    image = Image.open(imagefile)
    photo = ImageTk.PhotoImage(image)
    can.create_image(320, 240, image=photo)
    can.image=photo
    
def bf_preview_settings1():
    print lb_mainlist.curselection()
    
    #CLEAR CANVAS AND REDRAW IMAGE
    try: item = lb_mainlist.get(lb_mainlist.curselection())

    except TclError:
        item = lb_mainlist.get(0)
        lb_mainlist.selection_set(0)

    refresh_canvas()    #CLEAR CANVAS AND REDRAW IMAGE
    
    #get roi
    f = open(item[1], 'r')
    #load file, settings, xy points
    infoline = f.readline()
    infolist = infoline.split(',')
    infolist[6] = infolist[6].strip('(')
    infolist[9] = infolist[9].strip(')\n')


    #print rectx, recty, rectx2, recty2
    print infolist[6]
    #convert to int
    rectx = int(infolist[6]) - 7
    recty = int(infolist[7]) - 1
    rectx2 = int(infolist[8]) + 3
    recty2 = int(infolist[9]) + 3
    
    #rectx2 = rectx2 - rectx #convert to rectangle
    #recty2 = recty2 - recty
    
    print rectx, recty, rectx2, recty2
    can.create_rectangle(rectx,recty,rectx2,recty2, outline='red')

    #calculate center
    xcenter = (rectx + rectx2)/2
    ycenter = (recty + recty2)/2

    can.create_oval(xcenter, ycenter, xcenter+3, ycenter+3, fill="yellow")

    if checkbox_boxsize.get() == 1:
        print "Box Size is checked"
        boxsize = en_boxsize.get()
        boxpixsize = float(boxsize) * 3.4
        topleftx = xcenter - boxpixsize *.5
        toplefty = ycenter - boxpixsize *.5
        botrightx = xcenter + boxpixsize *.5
        botrighty = ycenter + boxpixsize *.5

        can.create_rectangle(topleftx, toplefty, botrightx, botrighty, outline='blue')
        
    if checkbox_grid.get() == 1:
        print "Grid is selected"
        en_grid.get()
        
    if checkbox_manual.get() == 1:
        can.create_rectangle(manual_firstx, manual_firsty, manual_lastx, manual_lasty, outline="purple")

def bf_preview_settings():
    print lb_mainlist.curselection()
    time_to_analyze = en_seconds_to_analyze.get()
    #CLEAR CANVAS AND REDRAW IMAGE
    try: item = lb_mainlist.get(lb_mainlist.curselection())

    except TclError:
        item = lb_mainlist.get(0)
        lb_mainlist.selection_set(0)

    refresh_canvas()    #CLEAR CANVAS AND REDRAW IMAGE
    
    #get roi
    f = open(item[1], 'r')
    #load file, settings, xy points
    infoline = f.readline()
    infolist = infoline.split(',')
    infolist[6] = infolist[6].strip('(')
    infolist[9] = infolist[9].strip(')\n')

    print "INFOLIST", infolist
    #save trial name to file
    trialname = infolist[0].split('/')
    run_filename = trialname.pop()

    #get FPS, calculate frames to analyze
    frames_to_analyze = int(time_to_analyze) * int(round(float(infolist[2])))
    print "FRAMES TO ANALYZE: ", frames_to_analyze, "  ",  int(round(float(infolist[2])))

    #get ROI from info list
    #roi_apparatus = eval(infolist[6])
    xypoints = f.readlines() #create xy point coords to analyze
    f.close()
    

    first_run = True
    lastx = 0
    lasty = 0
    distancetraveled = 0

    #print rectx, recty, rectx2, recty2
    print infolist[6]
    #convert to int
    rectx = int(infolist[6]) - 7
    recty = int(infolist[7]) - 1
    rectx2 = int(infolist[8]) + 3
    recty2 = int(infolist[9]) + 3
    
    #rectx2 = rectx2 - rectx #convert to rectangle
    #recty2 = recty2 - recty
    
    print rectx, recty, rectx2, recty2
    can.create_rectangle(rectx,recty,rectx2,recty2, outline='red')

    #calculate center
    xcenter = (rectx + rectx2)/2
    ycenter = (recty + recty2)/2

    can.create_oval(xcenter, ycenter, xcenter+3, ycenter+3, fill="yellow")
    can.create_text(320,10, text=run_filename, fill="green")
    
    if checkbox_boxsize.get() == 1:
        print "Box Size is checked"
        boxsize = en_boxsize.get()
        boxpixsize = float(boxsize) * 3.4
        topleftx = xcenter - boxpixsize *.5
        toplefty = ycenter - boxpixsize *.5
        botrightx = xcenter + boxpixsize *.5
        botrighty = ycenter + boxpixsize *.5

        can.create_rectangle(topleftx, toplefty, botrightx, botrighty, outline='blue')
        
    if checkbox_grid.get() == 1:
        print "Grid is selected"
        en_grid.get()
        
    if checkbox_manual.get() == 1:
        can.create_rectangle(manual_firstx, manual_firsty, manual_lastx, manual_lasty, outline="purple")

        first_run = True
        lastx = 0
        lasty = 0
        distancetraveled = 0
        
        #calculate distance traveled
        
    for each in xypoints:
        frame_xypoints = []
        
        frame_xypoints_unformated = each.split(',')
        for item in frame_xypoints_unformated:
            frame_xypoints.append(int(item.strip("\n")))
                                  
        print "FRAME XY POINTS", frame_xypoints
        if frame_xypoints[0] > frames_to_analyze:
            break #end analysis
        
        if first_run == True:
            print "FIRST RUN"
            first_run = False # First point recieved
            lastx = frame_xypoints[1] + rectx
            lasty = frame_xypoints[2] + recty
            
        else:
            thisx = frame_xypoints[1] + rectx
            thisy = frame_xypoints[2] + recty
            xpoints = abs(thisx - lastx)
            ypoints = abs(thisy - lasty)
            
            thisdistance = sqrt(pow(xpoints, 2) + pow(ypoints, 2))
            print "THIS DISTANCE: ", thisdistance
            
            if thisdistance > 30 or thisdistance < 5:
                thisx = lastx #do nothing
                thisy = lasty
                print "Doing nothing"
                
##                elif thisx < roix1 or thisx > roix2 or thisy < roiy1 or thisy > roiy2:
##                    thisx = lastx
##                    thisy = lasty
                
            else:
                print "ELSE FIRED!!!!"
                distancetraveled += thisdistance
                print "DISTANCE SO FAR: ", distancetraveled
                lastx = thisx
                lasty = thisy
                can.create_oval(thisx, thisy, thisx+1, thisy+1, fill="red")
        
def bf_load_files():
    filestr = tkFileDialog.askopenfilenames(title='Choose a file', filetypes = [('a2p files', '.a2p')])
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

        itemtemp = lb_mainlist.get(lb_mainlist.curselection())        
        imagefile = itemtemp[1].replace('.a2p','.jpg')
        image = Image.open(imagefile)
        photo = ImageTk.PhotoImage(image)
        can.create_image(320, 240, image=photo)
        can.image=photo
        

def bf_analyzer_threadstarter():
    thread.start_new_thread(bf_analyzer, ("Analysis Thread",1))

def f_output_writer(savefile_str, run_database):
    f = open(savefile_str, 'w') #create save file
    print run_database

    reporttitle = "MLK OpenField Analyzer Report"
    writebuffer = "<HTML>\n<TITLE>" + reporttitle + "</TITLE>\n"
    f.write(writebuffer)
    
    writebuffer = "<h1>" + "OpenField Analyzer Results on " + str(datetime.datetime.now()) + "\n" + "</h1>\n\n"
    f.write(writebuffer)
    #writebuffer = "This file has been auto-generated using the Maze Track Analyzer Program on " #+ str(time.ctime()) + "\n"
    #f.write(writebuffer)
    f.write("<center>")
    write_buffer = "\nSettings Used:\n"
    f.write(write_buffer)
    write_buffer = "Time Analyzed (secs): " + en_seconds_to_analyze.get() + "\n"
    f.write(write_buffer)
    
    if checkbox_boxsize.get() == 1:
        write_buffer = "Thigmotaxia Box(cm2): " + en_boxsize.get() + "\n"
        f.write(write_buffer)
    if checkbox_grid.get() == 1:
        write_buffer = "Grid (Selection): " + en.grid.get() + "\n"
        f.write(write_buffer)
    if checkbox_manual.get() == 1:
        write_buffer = "Manual Zone(cm2): " + "User Defined" + "\n"
        f.write(write_buffer)

    write_buffer = "\n"
    f.write(write_buffer)
    

    writebuffer = "\n<H1>Trial Summary:</H1>\n"
    f.write(writebuffer)
    
    writebuffer = '<table border="1"> \n <tr>'	#Start of table
    f.write(writebuffer)
    
    #Column Headings
    f.write("<td></td>")
    f.write("<td><B>Distance Traveled (cm)</B></td>")
    f.write("<td><B>Thigmotaxia Entries (#)</B></td>")
    f.write("<td><B>Thigmotaxia Exits (#)</B></td>")
    f.write("<td><B>Thigmotaxia Crosses (#)</B></td>")
    f.write("<td><B>Thigmotaxia Time Within (s)</B></td>")
    f.write("<td><B>Thigmotaxia Time Outside (s)</B></td>")
    f.write("<td><B>Grid Crosses (#)</B></td>")
    f.write("<td><B>User Entries (#)</B></td>")
    f.write("<td><B>User Exits (#)</B></td>")
    f.write("<td><B>User Crosses (#)</B></td>")
    f.write("<td><B>User Time Within (s)</B></td>")
    f.write("<td><B>User Time Outside (s)</B></td></tr>")

    for trial_run in run_database:
        #trial_run = run_database.pop(0)
        print trial_run
        f.write("<tr>") #Start New Row

        writebuffer = "<td><b><center>" + str(trial_run[0]) + "</center></b></td>" #Trial
        f.write(writebuffer)
        
        writebuffer = "<td><b><center>" + str(trial_run[1]) + "</center></b></td>" #dist traveled
        f.write(writebuffer)
        
        writebuffer = "<td><b><center>" + str(trial_run[2]) + "</center></b></td>" #thig ents
        f.write(writebuffer)

        writebuffer = "<td><b><center>" + str(trial_run[3]) + "</center></b></td>" #thig exits
        f.write(writebuffer)
        
        writebuffer = "<td><b><center>" + str(trial_run[4]) + "</center></b></td>" #thig crosses
        f.write(writebuffer)
       
        writebuffer = "<td><b><center>" + str(trial_run[5]) + "</center></b></td>" #thig timein
        f.write(writebuffer)
        
        writebuffer = "<td><b><center>" + str(trial_run[6]) + "</center></b></td>" #thig timemout
        f.write(writebuffer)

        writebuffer = "<td><b><center>" + str(trial_run[7]) + "</center></b></td>" #grid crosses
        f.write(writebuffer)
        
        writebuffer = "<td><b><center>" + str(trial_run[8]) + "</center></b></td>" #man ents
        f.write(writebuffer)

        writebuffer = "<td><b><center>" + str(trial_run[9]) + "</center></b></td>" #man exits
        f.write(writebuffer)
        
        writebuffer = "<td><b><center>" + str(trial_run[10]) + "</center></b></td>" #man crosses
        f.write(writebuffer)

        writebuffer = "<td><b><center>" + str(trial_run[11]) + "</center></b></td>" #man time in
        f.write(writebuffer)
        
        writebuffer = "<td><b><center>" + str(trial_run[12]) + "</center></b></td>" #man time out
        f.write(writebuffer)
        
    f.write("</table>\n") #End of table   
    f.write("</center></HTML>")
    f.close()
    
def bf_analyzer():
    
    savefile_str = tkFileDialog.asksaveasfilename(title='Name Save File', filetypes = [('html file', '.htm')], defaultextension=".htm")
    items_to_process = lb_mainlist.get(0, END)
    time_to_analyze = en_seconds_to_analyze.get()
    print "TIME to ANALYZE: ", time_to_analyze
    processing_filenum = 0
    run_database = [] #initialize run database for storing of run variables
    
    
    for item in items_to_process: #process each file
        run_filename = 0
        dist_traveled = 0
        thig_ents = 0
        thig_exits = 0
        thig_crosses = 0
        thig_timein = 0
        thig_timeout = 0
        grid_crosses = 0
        man_ents = 0
        man_exits = 0
        man_crosses = 0
        man_timein = 0
        man_timeout = 0
        
        processing_filenum+=1
        l_progress.config(text="Processing: File " + str(processing_filenum) + " / " + str(lb_mainlist.size()), background="yellow")
        f = open(item[1], 'r')
        #load file, settings, xy points
        infoline = f.readline()
        infolist = infoline.split(',')
        print "INFOLIST", infolist
        #save trial name to file
        trialname = infolist[0].split('/')
        run_filename = trialname.pop()
        infolist[6] = infolist[6].strip('(')
        infolist[9] = infolist[9].strip(')\n')


        rectx = int(infolist[6]) - 7
        recty = int(infolist[7]) - 1
        rectx2 = int(infolist[8]) + 3
        recty2 = int(infolist[9]) + 3
    
        #get FPS, calculate frames to analyze
        frames_to_analyze = int(time_to_analyze) * int(round(float(infolist[2])))
        print "FRAMES TO ANALYZE: ", frames_to_analyze, "  ",  int(round(float(infolist[2])))

        #get ROI from info list
        #roi_apparatus = eval(infolist[6])
        xypoints = f.readlines() #create xy point coords to analyze
        f.close()
        

        first_run = True
        lastx = 0
        lasty = 0
        distancetraveled = 0
        
        #calculate distance traveled
        for each in xypoints:
            frame_xypoints = []
            
            frame_xypoints_unformated = each.split(',')
            for item in frame_xypoints_unformated:
                frame_xypoints.append(int(item.strip("\n")))
                                      
            print "FRAME XY POINTS", frame_xypoints
            if frame_xypoints[0] > frames_to_analyze:
                break #end analysis
            
            if first_run == True:
                print "FIRST RUN"
                first_run = False # First point recieved
                lastx = frame_xypoints[1] + rectx
                lasty = frame_xypoints[2] + recty
                
            else:
                thisx = frame_xypoints[1] + rectx
                thisy = frame_xypoints[2] + recty
                xpoints = abs(thisx - lastx)
                ypoints = abs(thisy - lasty)
                
                thisdistance = sqrt(pow(xpoints, 2) + pow(ypoints, 2))
                print "THIS DISTANCE: ", thisdistance
                
                if thisdistance > 30 or thisdistance < 5:
                    thisx = lastx #do nothing
                    thisy = lasty
                    print "Doing nothing"
                    
##                elif thisx < roix1 or thisx > roix2 or thisy < roiy1 or thisy > roiy2:
##                    thisx = lastx
##                    thisy = lasty
                    
                else:
                    print "ELSE FIRED!!!!"
                    distancetraveled += thisdistance
                    print "DISTANCE SO FAR: ", distancetraveled
                    lastx = thisx
                    lasty = thisy
                    
        dist_traveled = str(distancetraveled/3.4)

        if checkbox_boxsize.get() == 1:
            boxsize = en_boxsize.get()

            infolist[6] = infolist[6].strip('(')
            infolist[9] = infolist[9].strip(')\n')

            #convert to int
            rectx = int(infolist[6]) #- 7
            recty = int(infolist[7]) #- 1
            rectx2 = int(infolist[8]) #+ 3
            recty2 = int(infolist[9]) #+ 3

            #calculate center
            xcenter = (rectx + rectx2)/2
            ycenter = (recty + recty2)/2

            boxsize = en_boxsize.get()
            boxpixsize = float(boxsize) * 3.4
            topleftx = xcenter - boxpixsize *.5
            toplefty = ycenter - boxpixsize *.5
            botrightx = xcenter + boxpixsize *.5
            botrighty = ycenter + boxpixsize *.5

            toprightx = botrightx
            toprighty = toplefty
            botleftx = topleftx
            botlefty = botrighty
            
            #convert to format for polytest
            box_poly = [(topleftx, toplefty), (toprightx, toprighty), (botrightx, botrighty), (botleftx, botlefty)]
            print "BOX POLY", box_poly
            
            counter_entries = 0
            counter_exits = 0
            #counter_timespent_within = 0
            counter_frames_within = 0
            #counter_timespent_outside = 0
            counter_frames_outside = 0
            status_locationlast = False
            status_locationcurrent = True
            
            for each in xypoints:
                split_each = each.split(',')
                split_each[0] = int(split_each[0])
                split_each[1] = int(split_each[1]) + rectx
                split_each[2] = split_each[2].strip("\n")
                split_each[2] = int(split_each[2]) + recty
                print "SPLIT EACH", split_each

                if split_each[0] > frames_to_analyze: #if reached end of analysis
                    break #end analysis

                if first_run == True:
                    print "FIRST RUN"
                    first_run = False # First point recieved
                    lastx = split_each[1] + rectx
                    lasty = split_each[2] + recty

                else:
                    thisx = split_each[1] + rectx
                    thisy = split_each[2] + recty
                    xpoints = abs(thisx - lastx)
                    ypoints = abs(thisy - lasty)

                    #check if x,y point is within box
                    status_locationcurrent = f_getlocation(split_each[1], split_each[2], box_poly)
                    print "STATS_LOCATIONCURRENT", status_locationcurrent

                    #### FIX HERE CHECK FOR DISTANCE TRAVELED

                    if status_locationcurrent == True and status_locationlast == True:
                    #within box continuing
                        counter_frames_within += 1

                    if status_locationcurrent == True and status_locationlast == False:
                    #just entered box
                        counter_frames_within += 1
                        counter_entries += 1
                        status_locationlast = True #make true for next round

                    if status_locationcurrent == False and status_locationlast == True:
                    #just left box
                        counter_frames_outside += 1
                        counter_exits += 1
                        status_locationlast = False #make true for next round

                    if status_locationcurrent == False and status_locationlast == False:
                    #outside box continuing
                        counter_frames_outside += 1
                
            thig_ents = str(counter_entries)
            thig_exits = str(counter_exits)
            thig_crosses = str(counter_entries+counter_exits)
            time_within = counter_frames_within / float(infolist[2])
            thig_timein = str(time_within)
            time_outside = counter_frames_outside / float(infolist[2])
            thig_timeout = str(time_outside)
                
        if checkbox_grid.get() == 1:
            print "Grid is selected"
            en_grid.get()
            
        if checkbox_manual.get() == 1:
            print "Manual mode"
            global manual_firstx
            global manual_firsty
            global manual_lastx
            global manual_lasty

            topleftx = manual_firstx
            toplefty = manual_firsty
            botrightx = manual_lastx
            botrighty = manual_lasty

            toprightx = botrightx
            toprighty = toplefty
            botleftx = topleftx
            botlefty = botrighty
            
            #convert to format for polytest
            box_poly = [(topleftx, toplefty), (toprightx, toprighty), (botrightx, botrighty), (botleftx, botlefty)]
            print "BOX POLY", box_poly
            
            counter_entries = 0
            counter_exits = 0
            #counter_timespent_within = 0
            counter_frames_within = 0
            #counter_timespent_outside = 0
            counter_frames_outside = 0
            status_locationlast = False
            status_locationcurrent = True

            for each in xypoints:
                split_each = each.split(',')
                split_each[0] = int(split_each[0])
                split_each[1] = int(split_each[1])
                split_each[2] = split_each[2].strip("\n")
                split_each[2] = int(split_each[2])
                print "SPLIT EACH", split_each

                if split_each[0] > frames_to_analyze:
                    break #end analysis
                
                #check if x,y point is within box
                status_locationcurrent = f_getlocation(split_each[1], split_each[2], box_poly)
                print "STATS_LOCATIONCURRENT", status_locationcurrent
                
                if status_locationcurrent == True and status_locationlast == True:
                #within box continuing
                    counter_frames_within += 1

                if status_locationcurrent == True and status_locationlast == False:
                #just entered box
                    counter_frames_within += 1
                    counter_entries += 1
                    status_locationlast = True #make true for next round

                if status_locationcurrent == False and status_locationlast == True:
                #just left box
                    counter_frames_outside += 1
                    counter_exits += 1
                    status_locationlast = False #make true for next round

                if status_locationcurrent == False and status_locationlast == False:
                #outside box continuing
                    counter_frames_outside += 1

            man_ents = str(counter_entries)
            man_exits = str(counter_exits)
            man_crosses = str(counter_entries+counter_exits)
            time_within = counter_frames_within / float(infolist[2])
            man_timein = str(time_within)
            time_outside = counter_frames_outside / float(infolist[2])
            man_timeout = str(time_outside)

        run_database.append([run_filename, dist_traveled, thig_ents, thig_exits, thig_crosses, thig_timein, thig_timeout, grid_crosses, man_ents, man_exits, man_crosses, man_timein, man_timeout])


    f_output_writer(savefile_str, run_database)                                                        
    l_progress.config(text="FINISHED!", background="green")

def bf_clearfiles():
    lb_mainlist.delete(0,END)
    
def del_lbitem(self):

    lbitemtemp = lb_mainlist.curselection()
    itemtodelete = int(lbitemtemp[0])
    lb_mainlist.delete(itemtodelete)

def click_viewfile(event):
    global can
    #load image -> send to canvas -> view
    #load trial properties
    #draw roi/apparatus image
    
    itemtemp = lb_mainlist.get(lb_mainlist.curselection())
    f = open(itemtemp[1], 'r')
    infoline = f.readline()
    infolist = infoline.split(',')
    f.close
    print itemtemp
    print itemtemp[1].replace('.a2p','.jpg')
    print infolist
    #0-avifile location 1-frames 2-fps 3-imagewidth 4-imageheight 5-length in seconds 6-apparatus roi coords

    resolution = infolist[3] + "x" + infolist[4]
    l_trial_name2.config(text=resolution)
    l_trial_fps2.config(text=infolist[2])
    l_trial_length2.config(text=infolist[5])

    #Load image and display
    imagefile = itemtemp[1].replace('.a2p','.jpg')
    image = Image.open(imagefile)
    photo = ImageTk.PhotoImage(image)
    can.create_image(320, 240, image=photo)
    can.image=photo
    

def canvas_click(event): # MOUSE 1 (LEFT-CLICK) PLACE POINT
    global grabbing_points
    global got_firstpoint
    global manual_firstx
    global manual_firsty
    global manual_lastx
    global manual_lasty
    
    if grabbing_points == True:
        if got_firstpoint == False:
            manual_firstx = event.x
            manual_firsty = event.y
            got_firstpoint = True
        else:
            manual_lastx = event.x
            manual_lasty = event.y
            grabbing_points = False
            got_firstpoint = False
            print "MANUAL CAPTURE:", manual_firstx, manual_firsty, manual_lastx, manual_lasty 
            can.create_rectangle(manual_firstx, manual_firsty, manual_lastx, manual_lasty, outline="purple")
    

def f_dispimage_old(frame):
    dispframe = frame.as_pil_image()
    ApImage = ImageTk.PhotoImage(dispframe)
    can.create_image(320, 240, image=ApImage)

def f_dispimage(image):
    ApImage = ImageTk.PhotoImage(image)
    can.create_image(320, 240, image=ApImage)

def f_getlocation(x, y, poly):
    #print poly, "X", x, "Y", y
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y) * (p2x-p1x) / (p2y-p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

############ ROOT WINDOW GUI #############
rootwindow = Tk()
rootwindow.title("OpenField Analyzer - Michael Kaufman 2010")
rootwindow.geometry("1000x700+200+0")
rootwindow.wm_state('zoomed')

### CANVAS WINDOW
can = Canvas(rootwindow, width='640', height='480')
can.configure(cursor="crosshair")
can.place(x=0, y=0)
can.bind("<Button-1>", canvas_click)
#photo = PhotoImage(file="test.jpg")

#f_dispimage(photo)

#image = Image.open("test.jpg")
#photo = ImageTk.PhotoImage(image)
#can.create_image(320, 240, image=photo)
can.create_text(320,240, text="Load Files to begin analysis", fill="red")
                   
###GUI FEATURES
menubar = Menu(rootwindow)

### Analyzer Settings
l_analyzer_settings = Label(rootwindow, text="Analyzer Settings:")
l_analyzer_settings.place(x=110,y=500)

#Checkbox variables
checkbox_boxsize = IntVar()
checkbox_grid = IntVar()
checkbox_manual = IntVar()

#check box
c_boxsize = Checkbutton(rootwindow, text="Box - Size in cm2", var=checkbox_boxsize, background = 'blue')
c_boxsize.place(x=150,y=530)
en_boxsize = Entry(rootwindow, width=4)
en_boxsize.insert(0, "0")
en_boxsize.place(x=300,y=535)

c_grid = Checkbutton(rootwindow, text="Grid - Divisions Level", var=checkbox_grid, background = 'green', state=DISABLED)
c_grid.place(x=150, y=565)
en_grid = Entry(rootwindow, width=4)
en_grid.insert(0, "0")
en_grid.place(x=300,y=565)

c_manual = Checkbutton(rootwindow, text="Manual - Selection", var=checkbox_manual, background = 'purple')
c_manual.place(x=150, y= 600)
b_manual_rect = Button(rootwindow, text="Set Rect", command=bf_mansetrect)
b_manual_rect.place(x=300, y=605)
#b_manual_circle = Button(rootwindow, text="Set Circle", command=bf_mansetcircle)
#b_manual_circle.place(x=360, y=605)

#preview buttons
b_preview_settings = Button(rootwindow, text="Preview Settings",command=bf_preview_settings)
b_preview_settings.place(x=100,y=660)

### Video Information
l_trial_info = Label(rootwindow, text="Trial Information:")
l_trial_info.place(x=700, y=470)
l_trial_name = Label(rootwindow, text="Resolution=")
l_trial_name.place(x=720, y=500)
l_trial_name2 = Label(rootwindow, text="")
l_trial_name2.place(x=820, y=500)
l_trial_fps = Label(rootwindow, text="FPS=")
l_trial_fps.place(x=720, y=520)
l_trial_fps2 = Label(rootwindow, text="")
l_trial_fps2.place(x=820, y=520)
l_trial_length = Label(rootwindow, text="Length=")
l_trial_length.place(x=720, y=540)
l_trial_length2 = Label(rootwindow, text="")
l_trial_length2.place(x=820, y=540)

### Seconds to Analyze
l_seconds_to_analyze = Label(rootwindow, text="Seconds to Analyze:")
l_seconds_to_analyze.place(x=700, y=630)
en_seconds_to_analyze = Entry(rootwindow, width=6)
en_seconds_to_analyze.insert(0,"120")
en_seconds_to_analyze.place(x=830, y=630)


#Progress Bar
l_progress = Label(rootwindow, text="")
l_progress.place(x=800, y=660)

### Analyze
b_analyzer = Button(rootwindow, text=">>ANALYZE!<<", background ="red", command=bf_analyzer)
### Analyze
b_analyzer.place(x=700, y=660)

#FileList #listbox
l_filestoprocess = Label(text = "Files to Process:")
lb_mainlist = Listbox(rootwindow, width=35, height=20)
lb_mainlist.bind("<BackSpace>", del_lbitem)
lb_mainlist.bind("<Double-Button-1>", click_viewfile)
l_filestoprocess.place(x = 700, y = 0)
lb_mainlist.place(x = 700, y = 20)

#filelist buttons
b_loadfiles = Button(rootwindow, text="Load Files", command=bf_load_files)
b_loadfiles.place(x=700, y=350)
b_clearfiles = Button(rootwindow, text="Clear Files", command=bf_clearfiles)
b_clearfiles.place(x=800, y=350)

#Zone Scroll Bar
sb_listscroll = Scrollbar(rootwindow)
sb_listscroll.place(x = 950, y = 50)
lb_mainlist.config(yscrollcommand=sb_listscroll.set)
sb_listscroll.config(command=lb_mainlist.yview)


### WIDGET PLACEMENT ###

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Load Video File", command=menu_load_files)
filemenu.add_separator()
filemenu.add_command(label="Save Zone Data", command=menu_saveconfig)
filemenu.add_command(label="Load Zone Data", command=menu_loadconfig)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=rootwindow.quit)
menubar.add_cascade(label="File", menu=filemenu)

# display the menu
rootwindow.config(menu=menubar)
rootwindow.mainloop()
