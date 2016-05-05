#!/usr/bin/python
# Mazetrack Data Analyzer TODO :
# [LOW] Entry Box with points listed, ability to edit points, delete last point
# [MED] When  File Selecting... Make the ability to navigate within folders  (WIN32)
# Identify Center of Polygon
# File Load/Save folder locations dialog, WINDOWS?!
# Grab Ap Image file from video frame Linux - Done  Windows - BROKE!!!
# Initial Directory = Working Directroy 

from os import *
from Tkinter import *
from PIL import Image
import ImageTk
import ImageDraw
import xlrd
import tkFileDialog
import string, time
from math import *
import tkMessageBox
import gst

import shutil
points = []

#Dicts to Hold Summary Data
sum_disp = {}
sum_duration = {}
sum_reachgoal = {}
sum_ccorrect = {}
sum_cwrong = {}

pixcmratio = 0
pwd = ""
apimageloc = ""
pwd_saves = ""
#########################################################################
#MENU FUNCTIONS
#########################################################################

def menu_imageselect():
	global ApImage
	global temp
	global apimageloc
	global pwd_saves
	filestr = tkFileDialog.askopenfilename(title='Please select image:', filetypes = [('png images', '.png'), ('gif images', '.gif'),  ('jpg images', '.jpg')])
	#pilfilestr = '"' + filestr + '"'
	pilimage = Image.open(filestr)
	ApImage = ImageTk.PhotoImage(pilimage)
	temp = can.create_image(176,144, image = ApImage)
	l_pwd.config(text=filestr)
	apimageloc = filestr
	tempfilestr = filestr.rsplit("/",1)
	pwd_saves = tempfilestr[0] + "/"
	print "PWD SAVES:", pwd_saves

def menu_imageselectavi():
	global ApImage
	global temp
	global apimageloc
	global pwd_saves
	filestr = tkFileDialog.askopenfilename(title='Please select avi:', filetypes = [('avi files', '.avi')])
	print "AVI FILESTR:", filestr
	filestrsplit = filestr.rsplit('.', 1)
	theoreticalstr = filestrsplit[0] + "-apparatus.png"
	if path.exists(theoreticalstr) == False:
		imfilestr = '"' + filestr + '"'
		gfilename, gpwd = grabimframe(imfilestr)
		pilfilestr = gpwd + gfilename
		shutil.move(gfilename, gpwd)
		pilimage = Image.open(pilfilestr)
		ApImage = ImageTk.PhotoImage(pilimage)
		temp = can.create_image(176,144, image = ApImage)
		l_pwd.config(text=pilfilestr)
		apimageloc = pilfilestr
		print "API-LOC", apimageloc
		pwd = gpwd
		pwd_saves = gpwd
	elif path.exists(theoreticalstr) == True:
		pilimage = Image.open(theoreticalstr)
		ApImage = ImageTk.PhotoImage(pilimage)
		temp = can.create_image(176,144, image = ApImage)
		l_pwd.config(text=filestr)
		apimageloc = filestr
		tempfilestr = filestr.rsplit("/",1)
		pwd_saves = tempfilestr[0] + "/"
	print "PWD_SAVES", pwd_saves
#########################################################################
def menu_savedatafile():
	filestr = tkFileDialog.asksaveasfilename(title='Saving MTA Zone File...:', filetypes = [('MTA Zone File', '.mta')])
	
	#save entire listbox worth of zones
	f = file(filestr,'w')
	#print lbmainlist.get(0,END)
	for each in lbmainlist.get(0,END): 
		#print each
		f.writelines(each)
		f.writelines('/n')
	f.close()

#########################################################################
def menu_loaddatafile():
	filestr = tkFileDialog.askopenfilename(title='Please select MTA settings:', filetypes = [('MTA Zone File', '.mta')])
	f = file(filestr, 'r')
	for line in f:
		plistlines = string.split(line,'/n')
		#print "processline:", plistlines
		for item in plistlines:
			if item != '':
				entryline = item.split('[')
				#print "SPLIT ENTRYLINE:", entryline
				zonename = entryline[0]
				#print "ZONENAME:", zonename
				points = entryline[1]
				#print "POINTS1:", points
				points = '[' + points
				#print "POINTS2:", points
				lbmainlist.insert(END, (zonename, points))
			else:
				pass
	f.close()

#########################################################################

def menu_instructions():
	window3 = Toplevel()
	window3.title("Instructions...")
	filelist = Listbox(window2)
	lzoneentry = Label(text= "Zone Name:")

def menu_about():
	window4 = Toplevel()
	window4.title("About Mazetrack Analyzer")

def menu_hello():
	pass
#########################################################################
#########################################################################
#BUTTONS
#########################################################################

def bf_addzone():
	global ApImage
	global points
	zonename = ezonename.get()
	#points.append(points[0]) #FIX
	#points.append(points[1])
	temp = can.create_image(176,144, image = ApImage)
	can.create_polygon(points, fill="", outline="black")
	lbmainlist.insert(END, (zonename, points))
	points = []

def bf_deletezone():
	zonetodelete = lbmainlist.curselection()
	lbmainlist.delete(zonetodelete)
	temp = can.create_image(176,144, image = ApImage) #display image on canvas

def bf_showzone():
	points = []	
	temp = can.create_image(176,144, image = ApImage)
	#print "Redrawing Zone"
	zonetodraw = lbmainlist.curselection()
	zonedata = lbmainlist.get(zonetodraw)
	points = eval(zonedata[1])
	can.create_polygon(points, fill="", outline="black")

def bf_showall():
	temp = can.create_image(176,144, image = ApImage)
	points = []
	#print "Redrawing Zone:", lbmainlist
	temp_list = list(lbmainlist.get(0, END))
	for each in temp_list:
		zonedata = each
		points = eval(zonedata[1])
		can.create_text(points[0], points[1], text = zonedata[0], anchor = NW, fill = "red")
		can.create_polygon(points, fill="", outline="black")

def bf_clearpoints():
	global points
	points = []
	temp = can.create_image(176,144, image = ApImage)

def bf_excelselect():
	
	global filelist
	global window5
	window5 = Toplevel()
	window5.title("Select your excel worksheet:")
	window5.geometry("+400+200")
	filelist = Listbox(window5)
	filelist.grid(row = 0, column = 0)

	flist = listdir('./')

	for item in flist:
		filelist.insert(END,item)

	filelist.bind("<Double-Button-1>",ef_excelload)
	button = Button(window5, text="Close", command=window5.destroy)
	button.grid(row = 1, column =0)

# IF WINDOWS IS DETECTED, USE THIS EXCEL ADD FUNCTION
if sys.platform == "win32":
	#print "DETECTED WINDOWS:", sys.platform
	def bf_exaddfile():
		global exfilelist
		global window6
		window6 = Toplevel()
		window6.title("Select file to add:")
		window6.geometry("+400+400")
		exfilelist = Listbox(window6)
		exfilelist.grid(row = 0, column = 0)

		flist = listdir('./')
		flist.sort()
		for item in flist:
			if string.find(item,'.xls'):
				exfilelist.insert(END,item)

		exfilelist.bind("<Double-Button-1>",addtolist)
		button = Button(window6, text="Close", command=window6.destroy)
		button.grid(row = 1, column =0)

#FOR OTHER OS, USE THIS FUNCTION
else:
	#print "DETECTED Other Platform:", sys.platform
	def bf_exaddfile():
		xlsfile = tkFileDialog.askopenfilenames(title='Please select files to add:', filetypes = [('excel files', '.xls')])

		for filestr in xlsfile:
			filelocation = filestr
			filenametemp = filestr.split('/')
			#print filenametemp
			filename = filenametemp.pop()
			filetuple = (filename, filelocation)
			#print filetuple
			lb_excelfiles.insert(END, filetuple)

def addtolist(self):
	fileselection = exfilelist.curselection()
	filestr = exfilelist.get(fileselection[0])
	lb_excelfiles.insert(END, filestr)

def bf_exdelfile():
	filetodelete = lb_excelfiles.curselection()
	lb_excelfiles.delete(filetodelete)

def bf_expreview(self):
	#bf_clearpoints()
	rundata = []
	fileselection = lb_excelfiles.curselection()
	fileselection2 = lb_excelfiles.get(fileselection)
	filetoload = fileselection2[1]
	xlsfile = xlrd.open_workbook(filetoload)
	sh = xlsfile.sheet_by_index(0)
	num_datapoints = (sh.nrows-2)

	#Strip String Stuff
	firstrow = str(sh.row(0))
	firstrow = firstrow.split(',')
	processlist = []
	for each in firstrow:
		if each[1] == 't':
			if each[0] == '[':
				cellentry = each.lstrip("[text:u'")
				cellentry = cellentry.rstrip("'")
				processlist.append(cellentry)
			else:
				cellentry = each.lstrip(" text:u'")
				cellentry = cellentry.rstrip("'")
				processlist.append(cellentry)
		elif each[1] == 'e':
			cellentry = each.strip(" empty:u'")
			cellentry = cellentry.strip("]")
			processlist.append(cellentry)
		elif each[1] == 'n':
			cellentry = each.strip(" number:u")
			cellentry = cellentry.strip("'")
			processlist.append(cellentry)

	rodentdata = []
	currentcell = 0

	#Initial Locations
	#Time Point Locations
	loc_time = (2, 0)

	#X-Coord Locations
	loc_xcoord = (2, 2)

	#Y-Coord Locations
	loc_ycoord = (2, loc_xcoord[1] + 2)

	#Loop, Finding Data Points
	while currentcell <= num_datapoints + 1:

		#Set Points append to rodentdata
		time = sh.cell_value(rowx=loc_time[0], colx=loc_time[1])
		xcoord = sh.cell_value(rowx=loc_xcoord[0], colx=loc_xcoord[1])
		ycoord = sh.cell_value(rowx=loc_ycoord[0], colx=loc_ycoord[1])

		fudgefactorx = e_fudgex.get()
		fudgefactory = e_fudgey.get()
		ycoord = ycoord + int(fudgefactorx) # FIX Switched xcoord, ycoord to compensate for Mouse Tracker flaw
		xcoord = xcoord + int(fudgefactory) #FIX Switched xcoord, ycoord to compensate for Mouse Tracker flaw
		#Append to rodentdata
		rodentdata.append((time,(ycoord, xcoord))) #FIX  Switched xcoord, ycoord to compensate for Mouse Tracker flaw

		#Advance Locations
		loc_time = (loc_time[0] + 1, loc_time[1])
		loc_xcoord = (loc_xcoord[0] + 1, loc_xcoord[1])
		loc_ycoord = (loc_ycoord[0] + 1, loc_ycoord[1])

		currentcell = loc_time[0]

	#End While Loop; Append to rundata
	rundata.append(rodentdata)
	#POINT TRACER
	xcoords = []
	ycoords = []
	for each in rundata:
		#print "RUNDATA:", each
		for somepoints in each:
			unpackpoint = somepoints[1]
			xcoords.append(unpackpoint[0])
			ycoords.append(unpackpoint[1])
	while len(xcoords) > 0:
		xpop = xcoords.pop(0)
		ypop = ycoords.pop(0)
		can.create_oval(xpop, ypop, xpop+1, ypop+1, fill="red")
		#print xpop, ypop

#########################################################################
#########################################################################
#OTHER FUNCS
#########################################################################
def createPath(path):
	if not os.path.isdir(path):
		os.mkdir(path)
#CANVAS MOUSE CONTROLS
def zonecoords(event): # MOUSE 1 (LEFT-CLICK) PLACE POINT
	can.create_oval(event.x, event.y, event.x+1, event.y+1, fill="black")
	points.append(event.x)
	points.append(event.y)
	#print points
	return points

def zonedraw(event): # MOUSE 3 (RIGHT-CLICK) GRAPH POINTS
	global points	
	#print "Graphing!"
	#points.append(points[0]) #Append 1st points to End to create polygon
	#points.append(points[1]) #FIX - Make it so that it draws a seperate polygon from stored
	can.create_polygon(points, fill="", outline="black")
	#print points

# Addzone in the case of pressing <return> in zonename Entry box
def addzone(event):
	global ApImage
	global points
	zonename = ezonename.get()
	temp = can.create_image(176,144, image = ApImage)
	lbmainlist.insert(END, (zonename, points))
	points = []

#Showzone in the case of pressing <Button-3> on the lbmainlist listbox
def showzone(event):
	temp = can.create_image(176,144, image = ApImage)
	points = []
	#print "Redrawing Zone"
	zonetodraw = lbmainlist.curselection()
	zonedata = lbmainlist.get(zonetodraw)
	points = eval(zonedata[1])
	can.create_polygon(points, fill="", outline="black")

def del_zoneitem(self): # FIX ACTIVATE
	zonetodeletetemp = lbmainlist.curselection()
	zonetodelete = int(zonetodeletetemp[0])
	lbmainlist.delete(zonetodelete)

def del_excelitem(self): #FIX ACTIVATE
	itemtodeletetemp = lb_excelfiles.curselection()
	itemtodelete = int(itemtodeletetemp[0])
	lb_excelfiles.delete(itemtodelete)

def lbxlsup(self):
	itemtomovetemp = lb_excelfiles.curselection()
	itemtomove = int(itemtomovetemp[0])
	itemtoswap = int(itemtomove-1)
	#print "item", itemtomove
	if int(itemtomove) != 0:	
		temp1 = lb_excelfiles.get(itemtoswap)
		temp2 = lb_excelfiles.get(itemtomove)
		#print "temp1", temp1
		#print "temp2", temp2
		lb_excelfiles.delete(itemtoswap)
		lb_excelfiles.insert(itemtoswap, temp2)
		lb_excelfiles.delete(itemtomove)
		lb_excelfiles.insert(itemtomove, temp1)
	lb_excelfiles.activate(itemtomove)

def lbxlsdown(self):
	lbxlsindex = lb_excelfiles.size()
	#print "LB SIZE:", lbxlsindex
	itemtomovetemp = lb_excelfiles.curselection()
	itemtomove = int(itemtomovetemp[0])
	itemtoswap = int(itemtomove+1)
	#print "item", itemtomove
	if int(itemtomove) < lbxlsindex-1:	
		temp1 = lb_excelfiles.get(itemtoswap)
		temp2 = lb_excelfiles.get(itemtomove)
		#print "temp1", temp1
		#print "temp2", temp2
		lb_excelfiles.delete(itemtoswap)
		lb_excelfiles.insert(itemtoswap, temp2)
		lb_excelfiles.delete(itemtomove)
		lb_excelfiles.insert(itemtomove, temp1)
	lb_excelfiles.activate(itemtomove)

#function to load the list of zones into option menu for selection
def bf_loadlanelist():
	v_lanelist = ["None"]
	templist = lbmainlist.get(0, END)
	for each in templist:
		v_lanelist.append(each)
	om_lanechoices = OptionMenu(rootwindow, vom_lanechoices, *v_lanelist)
	#print "LANE LIST", v_lanelist
	om_lanechoices.place(x = 430, y = 410)

def bf_loadlanelist2(): #For Exit Zone
	v_lanelist2 = ["None"]
	templist = lbmainlist.get(0, END)
	for each in templist:
		v_lanelist2.append(each)
	om_lanechoices2 = OptionMenu(rootwindow, vom_lanechoices2, *v_lanelist2)
	#print "LANE LIST", v_lanelist
	om_lanechoices2.place(x = 430, y = 460)

def bf_setrefpoint():
	global points
	global ref_distance
	#find distance between two points
	xpoints = points[2] - points[0]
	ypoints = points[3] - points[1]
	ref_distance = sqrt(pow(xpoints,2)+pow(ypoints,2))
	messagestr = "The selected pixel distance =" + str(ref_distance) + " Pixels"
	tkMessageBox.showinfo("Reference Distance", messagestr)
	ve_setrefpoint.set(str(ref_distance))
	e_setrefpoint.config(textvariable=ve_setrefpoint)

def bf_entercm():
	global pixcmratio
	cmdist = e_entercm.get()
	ref_entry = e_setrefpoint.get()
	print cmdist[0]
	print ref_entry
	pixcmratio = round(float(cmdist)/float(ref_entry), 4)
	messagestr = "Calculated Pixel to cm Ratio =" + str(pixcmratio)
	tkMessageBox.showinfo("Pixel to cm Ratio", messagestr)

def bf_deleteallzones():
	lbmainlist.delete(0,END)

def bf_deleteallxls():
	lb_excelfiles.delete(0,END)

def auto_entercm():
	global pixcmratio
	cmdist = e_entercm.get()
	ref_entry = e_setrefpoint.get()
	print cmdist[0]
	print ref_entry
	pixcmratio = round(float(cmdist)/float(ref_entry), 4)

#Function to determine whether a point is contained within the area of a polygon or not
def isinpolygon(xytuple,poly):
	x = xytuple[0]
	y = xytuple[1]
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

def create_runimage(runid, runname, dir_pwd_saves):
	global rundata

	#POINT TRACER
	xcoords = []
	ycoords = []
	runim = Image.open(apimageloc)
	draw = ImageDraw.Draw(runim)
	for each in rundata[runid]:
		unpackpoint = each[1]
		xcoords.append(unpackpoint[0])
		ycoords.append(unpackpoint[1])
	while len(xcoords) > 0:
		xpop = xcoords.pop(0)
		ypop = ycoords.pop(0)
		draw.point((xpop, ypop), fill="red")
	jpegsave = str(runname) + ".jpg"
	runim.save(jpegsave, "JPEG")
	newlocation = dir_pwd_saves + jpegsave
	shutil.move(jpegsave, newlocation)
	del draw
	del runim

def grabimframe(filelocation):
	# Define your pipeline, just as you would at the command prompt.
	# This is much easier than trying to create and link each gstreamer element in Python.
	# This is great for pipelines that end with a filesink (i.e. there is no audible or visual output)
	filestr1 = filelocation.rsplit('/',1)
	filestr = filestr1[1].strip('"')
	#print "GLOCATION:", filelocation
	#print "STR1:", filestr1
	#print "STR:", filestr
	retfilelocation = filelocation.strip(filestr + '"')	
	filestr = filestr.rsplit(".",1)
	filestr = filestr[0]
	#build str for gst parse
	gstparse = "filesrc location=" + filelocation + " ! decodebin ! ffmpegcolorspace ! pngenc ! filesink location=" + filestr + "-apparatus.png"

	pipe = gst.parse_launch(gstparse)

	# Get a reference to the pipeline's bus
	bus = pipe.get_bus()

	# Set the pipeline's state to PLAYING
	pipe.set_state(gst.STATE_PLAYING)

	# Listen to the pipeline's bus indefinitely until we receive a EOS (end of stream) message.
	# This is a super important step, or the pipeline might not work as expected.  For example,
	# in my example pipeline above, the pngenc will not export an actual image unless you have
	# this line of code.  It just exports a 0 byte png file.  So... don't forget this step.
	bus.poll(gst.MESSAGE_EOS, -1)
	retfilename = filestr + "-apparatus.png"
	#print "RETURN", retfilename
	#print "RETURN", retfilelocation
	return retfilename, retfilelocation
#########################################################################
#########################################################################
#EXCEL FUNCS
def ef_excelload():
	excelfiles = []
	excelfilesdump = lb_excelfiles.get(0,END)
	for each in excelfilesdump:
		excelfiles.append(each[1]) #append just the file locations to process list

	ef_excelprocess(excelfiles)

def ef_excelprocess(exfilenames):
	global sum_disp
	global sum_duration
	global sum_reachgoal
	global sum_ccorrect
	global sum_cwrong
	global rundata
	rundata = []
	rodentid = []  #Load XLS file names to tag rodentid TODO	
	filename = e_outputfile.get()
	if filename == "":
		filename = "Output"	
	#print "Filename:", filename	

	if pixcmratio == 0:
		auto_entercm()
		print "Fired Auto CM Generator"

	summaries_struct = []
		#Summaries Struct
			#0 sum_runs
				#0 Runs
					#0 Duration
					#1 Reach Goal?
					#2 Correct
					#3 Wrong
					#4 Dist Traveled
			#1 sum_trial
				#0 Avg. Duration
				#1 Total Right
				#2 Total Wrong
				#3 Avg. Dist Traveled

	#Load File, Establish Working Sheet
	for each in exfilenames:
		runid = each.rsplit('/',1)
		runid2 = runid[1].rsplit('.xls',1)
		rodentid.append(runid2[0])

		currentrodentid = runid2[0]
		xlsfile = xlrd.open_workbook(each)
		sh = xlsfile.sheet_by_index(0)
		num_datapoints = (sh.nrows-2)

		#Strip String Stuff
		firstrow = str(sh.row(0))
		firstrow = firstrow.split(',')
		processlist = []
		for each in firstrow:
			if each[1] == 't':
				if each[0] == '[':
					cellentry = each.lstrip("[text:u'")
					cellentry = cellentry.rstrip("'")
					processlist.append(cellentry)
				else:
					cellentry = each.lstrip(" text:u'")
					cellentry = cellentry.rstrip("'")
					processlist.append(cellentry)
			elif each[1] == 'e':
				cellentry = each.strip(" empty:u'")
				cellentry = cellentry.strip("]")
				processlist.append(cellentry)
			elif each[1] == 'n':
				cellentry = each.strip(" number:u")
				cellentry = cellentry.strip("'")
				processlist.append(cellentry)

		#############################################################################
		#############################################################################

        	displacement = sh.cell_value(rowx=num_datapoints, colx=8) #grab displacement #FIX should be num_datapoints + 1  Mouse Tracker BUG
        	
		print "NUM_DATAPOITNS=", num_datapoints+1 
		print "DISPLACEMENT=", displacement
		print "CMRATIO=", pixcmratio

		if pixcmratio > 0:
			sum_disp[currentrodentid] = round(displacement*pixcmratio,2)
		else:
        		sum_disp[currentrodentid] = round(displacement,2)

		rodentdata = []
		currentcell = 0

		#Initial Locations
		#Time Point Locations
		loc_time = (2, 0)

		#X-Coord Locations
		loc_xcoord = (2, 2)

		#Y-Coord Locations
		loc_ycoord = (2, loc_xcoord[1] + 2)

		#Loop, Finding Data Points
		while currentcell <= num_datapoints: #SHOULD BE +1  FIX, MOUSE TRACKER BUG

			#Set Points append to rodentdata
			time = sh.cell_value(rowx=loc_time[0], colx=loc_time[1])
			xcoord = sh.cell_value(rowx=loc_xcoord[0], colx=loc_xcoord[1])
			ycoord = sh.cell_value(rowx=loc_ycoord[0], colx=loc_ycoord[1])

			fudgefactorx = e_fudgex.get()
			fudgefactory = e_fudgey.get()
			ycoord = ycoord + int(fudgefactorx) # FIX Switched xcoord, ycoord to compensate for Mouse Tracker flaw
			xcoord = xcoord + int(fudgefactory) #FIX Switched xcoord, ycoord to compensate for Mouse Tracker flaw

			#Append to rodentdata
			rodentdata.append((time,(ycoord, xcoord))) #FIX  Switched xcoord, ycoord to compensate for Mouse Tracker flaw

			#Advance Locations
			loc_time = (loc_time[0] + 1, loc_time[1])
			loc_xcoord = (loc_xcoord[0] + 1, loc_xcoord[1])
			loc_ycoord = (loc_ycoord[0] + 1, loc_ycoord[1])

			currentcell = loc_time[0]

		#End While Loop; Append to rundata
		rundata.append(rodentdata)

	#Analyis/Comparision of Results #Number of Times Entered Each Zone #Time to Find Zone/Platform #Time Spent in Zone
	#load lbmain data and create polygons out of zonepoint data

	zonelisttoprocess = []
	listmain = lbmainlist.get(0,END)
	for each in listmain:
		zonename = each[0]
		zonepoints = each[1]
		zonepoints = eval(zonepoints) #convert to list
		#zonepoints = zonepoints[:-2] #slice off copycat point #FIX
		#build list contain for zone, zone points
		zonepointsfinal = []
		while zonepoints != []: #create list of tuples (polygon)
			xp = zonepoints.pop(0)
			yp = zonepoints.pop(0)
			tupletime = (xp,yp)
			zonepointsfinal.append(tupletime)
		builttuple = (zonename, zonepointsfinal)
		zonelisttoprocess.append(builttuple)
	#print "ZoneList to Process:", zonelisttoprocess
	
	zonelistcount = 0
	for each in lbmainlist.get(0,END): 
		zonelistcount += 1
	#print "There are ", zonelistcount, " zones in this experiment."

# major IF processor <complex> (ability to destinguish in multiple zones at once aka platforms within zones)
# rundata [0] = (time,(x,y))
# zonelisttoprocess [('Zone 1', [(158, 169), (118, 248), (154, 268), (191, 188)]), ('Zone 2', [(199, 189), (247, 268), (287, 244), (232, 167), (199, 189)])]

	finalstructure = [] # Finalized Data Structure to hold ALL DATA COLLECTED AND PROCESSED, Made up of Trials
	#print "\nRUNDATA:", rundata	
	for trial in rundata: #trial is a list of (time,(xy))
		#print "Using this TRIAL in rundata:", trial		
		finaltrialsdata = []	#List of Zones in this Trial
		for zone in zonelisttoprocess: # zone is a tuple of (zonename, listofpolygonpoints)
			zoneDPlist = []
			#print "For this ZONE in the list to process:", zone
			for frame in trial: # frame is a step in the timeline (time,(x,y))
				location = frame[1]
				zone_polygon = zone[1]
				#print "This is the ZONE POlYGON we are checking for points within:", zone_polygon

				if isinpolygon(location, zone_polygon) == True:
					#print "this one is true!"
					atuple = (frame[0], True)
					zoneDPlist.append(atuple)

				else:	#if not in a zone:
					#print "false!"
					atuple = (frame[0], False)
					zoneDPlist.append(atuple)

			btuple = (zone[0],zoneDPlist)

			finaltrialsdata.append(btuple)  #BUGGER
		finalstructure.append(finaltrialsdata)
	#print "FINAL STRUCTURE:", finalstructure

############################################################################################
#CALCULATE REPORT STATS #Time spent in Each Zone #Time to find Each Zone
#Choices: Correct vs Incorrect

	trials_struct = []
	report_summary = []
	for trial in finalstructure:
		for zone_set in trial:
			zone_name = zone_set[0]
			zone = zone_set[1]
			frame1 = zone[0]
			time = frame1[0]
			marker = frame1[1]
			if marker == True:
				initial_zone = zone_name
				#print "INITAL ZONE:", initial_zone

	for trial in finalstructure:
		#print "THIS IS THE TRIAL:", trial
		#[('Zone 1', [(324.0, False), (648.0, False), (972.0, False), (1296.0, False), (1620.0, False)]), ('Zone 2', [(324.0, False), (648.0, False), (972.0, False), (1296.0, False), (1620.0, False)]), ('Zone 3', [(324.0, False), (648.0, False), (972.0, True), (1296.0, False), (1620.0, False)])]
		zone_stats = []
		trial_summary = []
		last_frame = False
		for zone_set in trial:
		#('Zone 1', [(324.0, False), (648.0, False), (972.0, False), (1296.0, False), (1620.0, False)])
			zone_name = zone_set[0]
			zone = zone_set[1]
			zonestats = []
			#Calculate Trial Time # Inefficient  FIX
			unpack_trial = zone_set[1]
			n = len(unpack_trial)-1
			timetuple = unpack_trial[n]
			total_trial_time = timetuple[0]

			#Calculate Time to Reach the Zone
			tfmarker = False
			time_to_reach_zone = 0
			
			if zone_name == initial_zone: #if this is the starting zone
				itfmarker = True #initial Truth Marker
				tfmarker = True
				for frame in zone:
					this_time = frame[0]
					this_frame = frame[1] #True or False
					if this_frame == False and itfmarker == True:
						itfmarker = False
						tfmarker = False
					if tfmarker == False:
						if this_frame == True:
							tfmarker = True
							time_to_reach_zone = this_time
					else: pass
			else:
				for frame in zone:
					this_time = frame[0]
					this_frame = frame[1] #True or False
					if tfmarker == False:
						if this_frame == True:
							tfmarker = True
							time_to_reach_zone = this_time
					else: pass
			#####
			#Calculate Number of Entries to Zone
			number_of_entries = 0
			for frame in zone:
				this_frame = frame[1] #True or False
				if this_frame == True and last_frame == False:
					number_of_entries += 1
				else: pass
				last_frame = this_frame
			#####
			#Calculate Total Time Spent in Zone
			time_spent_in_zone = 0
			last_time_true = 0
			for frame in zone:
				this_time = frame[0]
				this_frame = frame[1] #True or False

				if this_frame == True and last_frame == False: #start timing
					last_time_true = this_time
				elif this_frame == True and last_frame == True: #continue timing
					time_spent_in_zone += (this_time - last_time_true)
					last_time_true = this_time
				else: pass
				last_frame = this_frame
			#####
			#Append Zone Stats to zonestats, then append to zone_stats
			zonestats.append(zone_name)		#0
			zonestats.append(time_to_reach_zone)	#1
			zonestats.append(number_of_entries)	#2
			zonestats.append(time_spent_in_zone)	#3
			zone_stats.append(zonestats)

		##Trial Summary - Store in trial_summary[]
		#print "ZONE STATS:", zone_stats
		#reach_goal? TODO
		total_trial_choices = 0
		for stat in zone_stats: 
			total_trial_choices += stat[2]
		trial_summary.append(total_trial_time)
		trial_summary.append(total_trial_choices)

		#Append to Trials_Struct[], zone_stats[] and trial_summary data
		build_tuple = (zone_stats, trial_summary)
		trials_struct.append(build_tuple)


	sum_ccorrectname = vom_lanechoices.get()
	sum_cname1 = sum_ccorrectname.split(',')
	sum_cname2 = sum_cname1[0]
	sum_cname = sum_cname2.strip("')(,")

	sum_exitname1 = vom_lanechoices2.get()
	sum_cname1 = sum_exitname1.split(',')
	sum_cname2 = sum_cname1[0]
	sum_exitname = sum_cname2.strip("')(,")
#########################################################################
#########################################################################
    #REPORT GENERATION FUNCTIONS
    #########################################################################
    #Output of results - HTML!
    #Prep for output

	filename = filename + ".html"
	reporttitle = "MTA -" + filename + " at: " #+ str(time.ctime())
	reporthead = "Report Sheet:" + filename

	#create folder with createPath(path) for images and other info (possible)

	dirname = str(filename + "-Report")
	global pwd_saves
	dir_pwd_saves = pwd_saves + dirname + "/"
	savecounter = 0

	while path.isdir(dir_pwd_saves) == True:
		savecounter += 1
		dir_pwd_saves = pwd_saves + dirname + str(savecounter) + "/"

	if not path.isdir(dir_pwd_saves):
		mkdir(dir_pwd_saves)

	print "PWD SAVES", pwd_saves

	# Start Output to File
	f = file(filename,'w')
	htmlfile = filename
	newfilename = filename.rsplit(".",1)
	filename = newfilename[0]
	writebuffer = "<HTML>\n<TITLE>" + reporttitle + "</TITLE>\n"
	f.write(writebuffer)
	writebuffer = "<h1>" + reporthead + "</h1>\n"
	f.write(writebuffer)
	#writebuffer = "This file has been auto-generated using the Maze Track Analyzer Program on " #+ str(time.ctime()) + "\n"
	#f.write(writebuffer)
	f.write("<center><HR>")
	writebuffer = "<img src='" + filename + ".jpg'/>\n"
	f.write(writebuffer)


	im = Image.open(apimageloc)
	draw = ImageDraw.Draw(im)

	temp = can.create_image(176,144, image = ApImage)
	points = []
	#print "Redrawing Zone:", lbmainlist
	temp_list = list(lbmainlist.get(0, END))
	for each in temp_list:
		zonedata = each
		points = eval(zonedata[1])
		textpoint = (points[0], points[1])
		draw.text(textpoint, text = zonedata[0], fill ="red")
		draw.polygon(points, outline="black")
	del draw
	jpegsave = str(filename) + ".jpg"
	im.save(jpegsave, "JPEG")
	newlocation = dir_pwd_saves + jpegsave
	shutil.move(jpegsave, newlocation)
############################################################################################
#HTML OUTPUT OF TRIAL DATA
	writebuffer = "<H1>Raw Data:</H1>\n"
	f.write(writebuffer)
	trial_num = 0
	runidnum = 0 #for drawing image of run
	for trial in trials_struct:
		trial_num += 1
		zoneinfo = trial[0]
		trialsum = trial[1]
	#Start Generating Table
		run = rodentid[trial_num-1]
		writebuffer = "<H1>" + str(rodentid[trial_num-1]) + "</H1>\n"
		f.write(writebuffer)
		writebuffer = '<table border="1"> \n <tr>'	#Start of table
		f.write(writebuffer)
		writebuffer = "<img src='" + run + ".jpg' ALIGN='right'/>"
		f.write(writebuffer)
		#Column Headings
		f.write("<td>Zone:</td>")
		f.write("<td><B>Time to Reach (s)</B></td>")
		f.write("<td><B>Entries</B></td>")
		f.write("<td><B>Time Spent (s)</B></td></tr>")
		total_choices = 0
		for zone in zoneinfo:
			f.write("<tr>") #Start New Row
			writebuffer = "<td><b>" + str(zone[0]) + "</b></td>"  #Zone Name
			f.write(writebuffer)
			writebuffer = "<td><center>" + str(zone[1]/float(1000)) + "</center></td>" #Time to Reach
			f.write(writebuffer)

			if zone[0] == initial_zone:
				writebuffer = "<td><center>" + str(zone[2]-1) + "</center></td>"	#Entries
				f.write(writebuffer)
			else:
				writebuffer = "<td><center>" + str(zone[2]) + "</center></td>"	#Entries
				f.write(writebuffer)

			writebuffer = "<td><center>" + str(zone[3]/float(1000)) + "</center></td>" #Timespent
			f.write(writebuffer)

			if zone[0] == sum_cname: 	#IF THIS IS CORRECT ZONE
				sum_ccorrect[run] = zone[2]

			if zone[0] == sum_exitname: 	#IF THIS IS EXIT
				sum_duration[run] = (zone[1]/float(1000))
				if zone[2] > 0:
					sum_reachgoal[run] = 1
				else:
					sum_reachgoal[run] = 0

			if zone[0] == initial_zone:
				total_choices += zone[2]-1 #remove extra entry due to starting zone
			else:
				total_choices += zone[2]

		if sum_duration[run] == 0: #if rodent does not find exit, make duration 60 seconds
			sum_duration[run] = 60

		f.write("</tr></table>\n")
		create_runimage(runidnum, run, dir_pwd_saves)

		sum_cwrong[run] = (total_choices - sum_ccorrect[run] - sum_reachgoal[run]) #wrong choices is equal to the total - correct - exit
		runidnum += 1 #advance for next run

#HTML OUTPUT OF RUN SUMMARY
	f.write("\n<H1>Run(s) Summary </H1>\n")
	writebuffer = '<table border="1"> \n <tr>'	#Start of table
	f.write(writebuffer)
#Column Headings
	f.write("<td>Run(s) #</td>")
	f.write("<td><B>Duration (s)</B></td>")
	f.write("<td><B>Reach Goal (1/0)</B></td>")
	f.write("<td><B>Choice Correct</B></td>")
	f.write("<td><B>Choice Wrong</B></td>")
	f.write("<td><B>Correct (%)</B></td>")
	f.write("<td><B>Distance Traveled (cm)</B></td></tr>")
	f.write("<tr>") #Start New Row
	
	total_disp = 0
	total_correct = 0
	total_wrong = 0
	total_duration = 0
	total_reached = 0

	for run in rodentid:
		writebuffer = "<td><b><center>" + str(run) + "</center></b></td>" #Run #
		f.write(writebuffer)
		writebuffer = "<td><b><center>" + str(sum_duration[run]) + "</center></b></td>" #Duration
		f.write(writebuffer)
		writebuffer = "<td><b><center>" + str(sum_reachgoal[run]) + "</center></b></td>" #ReachGoal?
		f.write(writebuffer)
		writebuffer = "<td><b><center>" + str(sum_ccorrect[run]) + "</center></b></td>" #Right Choice
		f.write(writebuffer)
		writebuffer = "<td><b><center>" + str(sum_cwrong[run]) + "</center></b></td>" #Wrong Choice
		f.write(writebuffer)
		correctvswrong1 = (sum_ccorrect[run] / float(sum_cwrong[run] + sum_ccorrect[run]))*100
		correctvswrong = round(correctvswrong1, 2)
		writebuffer = "<td><b><center>" + str(correctvswrong) + "</center></b></td>" #% Right vs Wrong
		f.write(writebuffer)
		writebuffer = "<td><b><center>" + str(sum_disp[run]) + "</center></b></td></tr>" #Distance Traveled
		f.write(writebuffer)
		
		total_disp += sum_disp[run]
		total_correct += sum_ccorrect[run]
		total_wrong += sum_cwrong[run]
		total_duration += sum_duration[run]
		total_reached += sum_reachgoal[run]

	f.write("</table>\n")


#HTML OUTPUT OF TRIALS SUMMARY
	writebuffer = "\n<H1>Trial Summary: " + filename + "</H1>\n"
	f.write(writebuffer)
	writebuffer = '<table border="1"> \n <tr>'	#Start of table
	f.write(writebuffer)
	#Column Headings
	f.write("<td></td>")
	f.write("<td><B>Avg. Run Duration (s)</B></td>")
	f.write("<td><B>Reached Goal (%)</B></td>")
	f.write("<td><B>Total Correct</B></td>")
	f.write("<td><B>Total Wrong</B></td>")
	f.write("<td><B>Correct (%)</B></td>")
	f.write("<td><B>Avg. Dist Traveled (cm)</B></td></tr>")

	f.write("<tr>") #Start New Row
	trial_name1 = run.rsplit('R', 1)
	trial_name = trial_name1[0]

	writebuffer = "<td><b><center>" + str(trial_name) + "</center></b></td>" #Trial
	f.write(writebuffer)
	avg_duration = total_duration/float((len(rodentid)))
	writebuffer = "<td><b><center>" + str(round(avg_duration,2)) + "</center></b></td>" #Avg Duration
	f.write(writebuffer)
	per_reached = total_reached/float(len(rodentid))*100
	writebuffer = "<td><b><center>" + str(round(per_reached,2)) + "</center></b></td>" #% Reached Goal
	f.write(writebuffer)
	writebuffer = "<td><b><center>" + str(total_correct) + "</center></b></td>" #Total Correct
	f.write(writebuffer)
	writebuffer = "<td><b><center>" + str(total_wrong) + "</center></b></td>" #Total Wrong
	f.write(writebuffer)
	per_right = total_correct/float((total_wrong + total_correct))*100
	writebuffer = "<td><b><center>" + str(round(per_right,2)) + "</center></b></td>" #% Correct
	f.write(writebuffer)
	avg_disp = total_disp/float(len(rodentid))
	#print "LENGTHOFRODENTID = ", len(rodentid)
	writebuffer = "<td><b><center>" + str(round(avg_disp,2)) + "</center></b></td>" #Avg Dist Traveled
	f.write(writebuffer)
	f.write("</table>\n")

#end HTML file
	writebuffer = "<img src='" + trial_name + ".jpg'/>\n"
	f.write(writebuffer)
	f.write("</center></HTML>")
	f.close()

	newlocation = dir_pwd_saves + htmlfile
	shutil.move(htmlfile, newlocation)

#	dirname = str(trial_name + "-runimages")
#	if not path.isdir("./" + dirname + "/"):
#		mkdir("./" + dirname + "/")
#	imagename = "Trial" + str(rodentid[trial_num-1]) + ".jpg"
#	writebuffer = '<img src="' + imagename + '"/>'

#TODO DRAW AP AND ZONES

#DRAWS ALL POINTS IN TRIAL
	#POINT TRACER
	xcoords = []
	ycoords = []
	for each in rundata:
		im = Image.open(apimageloc)

		draw = ImageDraw.Draw(im)
		for somepoints in each:
			unpackpoint = somepoints[1]
			xcoords.append(unpackpoint[0])
			ycoords.append(unpackpoint[1])
	while len(xcoords) > 0:
		xpop = int(xcoords.pop(0))
		ypop = int(ycoords.pop(0))
		can.create_oval(xpop, ypop, xpop+1, ypop+1, fill="blue")
		draw.point((xpop, ypop), fill="red")
	del draw
	jpegsave = str(trial_name) + ".jpg"
	im.save(jpegsave, "JPEG")
	newlocation = dir_pwd_saves + jpegsave
	shutil.move(jpegsave, newlocation)

#IF WINDOWS SYSTEM... OPEN THE CREATED HTML REPORT  TODO

#########################################################################
#MAIN - TK Window and Widget Generation
#########################################################################
rootwindow = Tk()
rootwindow.title("Mazetrack Data Analyzer rev8")
rootwindow.geometry("600x600+300+0")

#default maze image view
#ApImage = PhotoImage(file = "default.gif") #took out default image
ApImage = PhotoImage(file = "")

menubar = Menu(rootwindow)

#create canvas
can = Canvas(rootwindow, width = '352', height = '288', bg = 'white')
can.configure(cursor="crosshair")
can.bind("<Button-1>", zonecoords)
can.bind("<Button-3>", zonedraw)
temp = can.create_image(176,144, image = ApImage) #display image on canvas


# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Select Apparatus Image", command=menu_imageselect)
filemenu.add_command(label="Select AVI Apparatus Image", command=menu_imageselectavi)
filemenu.add_separator()
filemenu.add_command(label="Save Zone Data", command=menu_savedatafile)
filemenu.add_command(label="Load Zone Data", command=menu_loaddatafile)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=rootwindow.quit)
menubar.add_cascade(label="File", menu=filemenu)

# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Cut", command=menu_hello)
editmenu.add_command(label="Copy", command=menu_hello)
editmenu.add_command(label="Paste", command=menu_hello)
menubar.add_cascade(label="Edit", menu=editmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Instructions", command=menu_instructions)
helpmenu.add_command(label="About", command=menu_about)
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
rootwindow.config(menu=menubar)

#rootwindow buttons
baddzone = Button(rootwindow, text="Add Zone", command=bf_addzone)
bclearpoints = Button(rootwindow, text="Clear Points", command=bf_clearpoints)
bdeletezone = Button(rootwindow, text="Delete Zone", command=bf_deletezone)
bdeleteallzones = Button(rootwindow, text="Delete All", command=bf_deleteallzones)
bviewzone = Button(rootwindow, text="View Zone", command=bf_showzone)
bexcelprocess = Button(rootwindow, text="Process Files", command=ef_excelload)
bdeleteallxls = Button(rootwindow, text="Delete All", command=bf_deleteallxls)
bviewall = Button(rootwindow, text="View All Zones", command=bf_showall)
#rootbindings

#labels
lzoneentry = Label(text= "Zone Name:")
llistname = Label(text= "Zone List:")
l_excelfiles = Label(text = "Excel Files to Process:")

#zone name entrybox
ezonename = Entry(rootwindow)
ezonename.bind("<Return>", addzone)
ezonename.focus()

#listbox
lbmainlist = Listbox(rootwindow, width=20)
lbmainlist.bind("<Button-3>", showzone)
lbmainlist.bind("<BackSpace>", del_zoneitem)
#Zone Scroll Bar
sb_zonelist = Scrollbar(rootwindow)  
sb_zonelist.place(x = 530, y = 240)
lbmainlist.config(yscrollcommand=sb_zonelist.set)
sb_zonelist.config(command=lbmainlist.yview)

#excelfile listbox
lb_excelfiles = Listbox(rootwindow)
lb_excelfiles.bind("<BackSpace>", del_excelitem)
lb_excelfiles.bind("<Shift-Up>", lbxlsup)
lb_excelfiles.bind("<Shift-Down>", lbxlsdown)
lb_excelfiles.bind("<Button-3>", bf_expreview)  #FIX

#widget positions
can.place(x = 0, y = 0)
lzoneentry.place(x = 360, y = 0)
ezonename.place(x = 360, y = 20)
baddzone.place(x = 360, y = 50)
bdeletezone.place(x = 360, y = 80)
bviewzone.place(x = 360, y = 110)
llistname.place(x = 360, y = 160)
lbmainlist.place(x = 360, y = 180)
bdeleteallzones.place(x = 470, y = 80)
bdeleteallxls.place(x = 30, y = 570)

bclearpoints.place(x = 240, y = 300)
bviewall.place(x = 240, y = 330)

#excel buttons
b_exaddfile = Button(rootwindow, text="Add File(s)", command=bf_exaddfile)
b_exdelfile = Button(rootwindow, text="Delete File", command=bf_exdelfile)
#b_expreview = Button(rootwindow, text="Preview", command=bf_expreview)
#excel
bexcelprocess.place(x = 170, y = 500)
lb_excelfiles.place(x = 0, y = 320)
l_excelfiles.place(x = 0, y = 300)
b_exaddfile.place(x = 170, y = 420)
b_exdelfile.place(x = 170, y = 450)
#b_expreview.place(x = 170, y = 480)
#Excel Scroll Bar
sb_excellist = Scrollbar(rootwindow)  
sb_excellist.place(x = 170, y = 380)
lb_excelfiles.config(yscrollcommand=sb_excellist.set)
sb_excellist.config(command=lb_excelfiles.yview)

e_outputfile = Entry(rootwindow)
e_outputfile.place (x = 0, y = 505)

###EXTRA OPTIONS
#Choice
#l_options = Label(rootwindow, text="Processing Options:")
l_choices = Label(rootwindow, text="Correct Choice Zone:")
v_lanelist = ["None"]
vom_lanechoices = StringVar(rootwindow)
vom_lanechoices.set(v_lanelist[0]) #Default option
om_lanechoices = OptionMenu(rootwindow, vom_lanechoices, *v_lanelist)
b_lanechoices = Button(rootwindow, text="Populate >>", command=bf_loadlanelist)

#Exit
l_exit = Label(rootwindow, text="Exit Zone:")
v_lanelist2 = ["None"]
vom_lanechoices2 = StringVar(rootwindow)
vom_lanechoices2.set(v_lanelist2[0]) #Default option
om_lanechoices2 = OptionMenu(rootwindow, vom_lanechoices2, *v_lanelist2)
b_lanechoices2 = Button(rootwindow, text="Populate >>", command=bf_loadlanelist2)

#Displacement
l_trackdisp = Label(rootwindow, text="Displacement:")
b_setrefpoint = Button(rootwindow, text="Grab Ref. Points", command=bf_setrefpoint)
e_setrefpoint = Entry(rootwindow, width = 5)

l_entercm = Label(rootwindow, text="Enter cm:")
e_entercm = Entry(rootwindow,  width = 5)
b_entercm = Button(rootwindow, text="Calc", command=bf_entercm)

###E-O PLACEMENT
#Choice
#l_options.place(x = 300, y = 370)
l_choices.place(x = 310, y = 390)
b_lanechoices.place(x = 320, y = 410)
om_lanechoices.place(x = 430, y = 410)

#Exit
l_exit.place(x = 310, y = 440)
b_lanechoices2.place(x = 320, y = 460)
om_lanechoices2.place(x = 430, y = 460)

#Displacement
l_trackdisp.place(x = 310, y = 500)
b_setrefpoint.place(x = 320, y = 520)
e_setrefpoint.place(x = 380, y = 550)
ve_setrefpoint = StringVar(rootwindow)
ve_setrefpoint.set("0") #Default option

l_entercm.place(x = 450, y = 500)
e_entercm.place(x = 450, y = 525)
b_entercm.place(x = 500, y = 520)


#FUDGEFACTOR ENTRY
l_fudgefactor = Label(rootwindow, text="Fudge Factor(s) X and Y:")
l_fudgefactor.place(x = 0, y = 530)
e_fudgex = Entry(rootwindow, width = 3)
l_fudgex = Label(rootwindow, text="X:")
l_fudgex.place(x = 0, y = 550)
e_fudgex.place(x = 20, y = 550)
e_fudgex.delete(0, END)
e_fudgex.insert(0, "-5")
e_fudgey = Entry(rootwindow, width =  3)
e_fudgey.place(x = 80, y = 550)
e_fudgey.delete(0, END)
e_fudgey.insert(0, "-5")
l_fudgey = Label(rootwindow, text="Y:")
l_fudgey.place(x = 60, y = 550)

#PWD and PWF
l_pwd = Label(rootwindow, text=pwd)
l_pwd.place(x = 25, y = 580)
rootwindow.mainloop()
