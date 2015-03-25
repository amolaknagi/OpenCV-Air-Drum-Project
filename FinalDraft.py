import pygame
import cv2
import numpy as np
import sys
import wave
import math
import pyaudio

#Class to run the entire music suite
class SuperEditor(object):
	#Define dimensions of window
	def __init__(self,width,height):
		self.width = width
		self.height = height
	
	#Define certain variables before starting application
	def initAnimation(self):
		#Create bools for each window, True if it's showing
		(self.startScreen, self.helpScreen, self.freePlay,
		self.drumSetStaffSetup,self.drumSetStaff,
		self.standardStaffSetup, self.standardStaff,
		self.saveWindow,self.openWindow) = (True,
		False,False,False,False,False,False,False,False)
		#Keep track of selected time signature based on index
		self.timeSignatures, self.selectedTime = ["2/4","3/4","4/4"], 2
		self.letters = ["B5","A5","G5","F5","E5","D5","C5","B4",
						"A4","G4","F4","E4","D4","C4"]		
		#Keep track of type, length, and pitch basd on index			
		(self.selectedType,
		 self.selectedLength, self.selectedPitch) = (0,2,0)
		#Record of user input of title/composer and whether they're typing
		self.title, self.titleInput = "", False
		self.composer, self.composerInput = "", False
		#Keep record of a filename to save audio files
		self.filename = ""
		#Store tuple notes in list
		self.standardNotes = []
		#Initialize pygame module
		pygame.init()
		#Create window based on dimensions
		self.window = pygame.display.set_mode((self.width,self.height))
		pygame.display.set_caption("SuperEditor")
		#Keep 16 and 8 pixel margins for whole/half steps in staff
		self.wholeStepHeight,self.halfStepHeight = 16, 8

	#Call this function to run entire application
	def run(self):
		#Call initial variables
		self.initAnimation()
		#Continuously loop through all screens. Run one if it's selected
		while True:
			if self.startScreen:
				self.runStartScreen()
			elif self.drumSetStaffSetup:
				self.runDrumSetStaffSetup()
			elif self.freePlay:
				self.runFreePlay()
			elif self.standardStaffSetup:
				self.runStandardStaffSetup()
			elif self.standardStaff:
				self.runStandardStaff()
			elif self.saveWindow:
				self.runSaveWindow()
			elif self.helpScreen:
				self.runHelpWindow()

	#Run the help window
	def runHelpWindow(self):
		#Call draw function before running the window
		self.redrawHelpWindow()
		while True:
			#Continuously respond to user actions in window
			self.respondToHelpWindowActions()
			#Quit showing help window if user clicks otherwise
			if not self.helpScreen:
				break

	#Respond to user input in help window
	def respondToHelpWindowActions(self):
		for event in pygame.event.get():
			#Allow user to return to start screen if he/she clicks back
			if event.type == pygame.MOUSEBUTTONDOWN:
				coord = pygame.mouse.get_pos()
				if self.backButton.collidepoint(coord):
					self.helpScreen = False
					self.startScreen = True
			#Close application if user presses x on top right of window
			elif event.type == pygame.QUIT:
				sys.exit()

	#Redraw help window. Store buttons in window for actions
	def redrawHelpWindow(self):
		self.backButton = HelpScreenDrawing(self.window).redrawAll()

	#Redraw save window. Store uttons in window for actions
	def redrawSaveWindow(self):
		(self.filenameBox,
			self.saveButton) = SaveSongScreen(self.window,
											self.selectedTime,
											self.selectedType,
											self.selectedLength,
											self.selectedPitch,
											self.standardNotes,
											self.title,
											self.composer,
											self.filename).redrawAll()

	#Run window to save audio files
	def runSaveWindow(self):
		#First draw the window before running it
		self.redrawSaveWindow()
		while True:
			#Continously respond to user actions while running
			self.respondToSaveWindowActions()
			#Quit showing save window if user decides not to
			if not self.saveWindow:
				break

	#Respond to user inputs on save window
	def respondToSaveWindowActions(self):
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				coord = pygame.mouse.get_pos()
				#Save notes in wave file if user clicks save
				#This should also return user to staff screen
				if self.saveButton.collidepoint(coord):
					PlayStandardNotes(self.standardNotes
										).saveWaveFile(self.filename)
					self.saveWindow = False
					self.standardStaff = True
				#Redraw save window on every mousepress
				self.redrawSaveWindow()
			#Allow user to type in name for audio file
			elif event.type == pygame.KEYDOWN:
				self.typeFilename(event)
				#Redraw save window every time user presses key
				self.redrawSaveWindow()
			#Close application if user clicks x on top right of window
			elif event.type == pygame.QUIT:
				sys.exit()

	#Allow for manual user text input for the name of the audio file
	def typeFilename(self,event):
		#Add letters to filename is ord falls within range of letters
		if 97 <= event.key <= 122:
			self.filename += chr(event.key)
		#Delete last letter of filename if user presses backspace
		elif event.key == 8:
			self.filename = self.filename[:len(self.filename) - 1]

	#Allow for manual user text input for the title and composer
	def typeText(self,event):
		#Modify title if program calls for it
		if self.titleInput:
			#Add letter to title if corresponding ord is pressed
			if 97 <= event.key <= 122:
				#Make first letter of every word capitalized
				if ((len(self.title) == 0) or 
					(self.title[len(self.title)-1] == " ")):
					event.key -= 32 
				self.title += chr(event.key)
			#Add space to title if user presses space
			elif event.key == 32: self.title += " "
			#Remove last letter if user presses backspace
			elif event.key == 8: self.title = self.title[:len(self.title)-1]
		#Modify composer if programs calls for it
		elif self.composerInput:
			#Add letter to composer if corresponding ord is pressed
			if 97 <= event.key <= 122:
				#Make first letter of every word capitalized
				if ((len(self.composer) == 0) or 
					(self.composer[len(self.composer)-1] == " ")):
					event.key -= 32 
				self.composer += chr(event.key)
			#Add space if user presses space
			elif event.key == 32: self.composer += " "
			#Remove last letter if user presses backspace
			elif event.key == 8: 
				self.composer = self.composer[:len(self.composer)-1]

	#Run function for the musical staff window
	def runStandardStaff(self):
		#Draw staff window prior to running
		self.redrawStandardStaff()
		while True:
			#Continously respond to user input while running
			self.respondToStandardStaffActions()
			#End running of this window if user decides to
			if not self.standardStaff:
				break

	#Draw all of musical staff. Store buttons for user mousepresses
	def redrawStandardStaff(self):
		(self.noteTypeButtons,
		self.noteLengthButtons,
		self.notePitchButtons,
		self.playButton,
		self.quitButton,
		self.saveButton) = StandardStaffDrawings(self.window,
							self.selectedTime,
							self.selectedType,
							self.selectedLength,
							self.selectedPitch,
							self.standardNotes,
							self.title,
							self.composer).redrawAll()
			
	#Respond to user input on music staff window
	def respondToStandardStaffActions(self):
		for event in pygame.event.get():
			#Act if user presses mouse
			if event.type == pygame.MOUSEBUTTONDOWN:
				coord = pygame.mouse.get_pos()
				self.respondToStandardStaffMousePress(coord)
				#Redraw staff on every mousePress
				self.redrawStandardStaff()
			#Act if user presses key
			elif event.type == pygame.KEYDOWN:
				keypress = event.key
				#Remove last note in staff if user presses backspace
				if keypress == 8:
					if len(self.standardNotes) > 0:
						self.standardNotes.pop()
				#Redraw staff on every keyPress
				self.redrawStandardStaff()
			#Close application if user presses x on top right of window
			elif event.type == pygame.QUIT:
				sys.exit()

	#Take action if user presses mouse on music staff window
	def respondToStandardStaffMousePress(self,coord):
		#Change noteType if user presses button
		for button in xrange(len(self.noteTypeButtons)):
			if self.noteTypeButtons[button].collidepoint(coord):
				self.selectedType = button
		#Change noteLength if user presses button
		for button in xrange(len(self.noteLengthButtons)):
			if self.noteLengthButtons[button].collidepoint(coord):
				self.selectedLength = button
		#Change notePitch if user presses button
		for button in xrange(len(self.notePitchButtons)):
			if self.notePitchButtons[button].collidepoint(coord):
				self.selectedPitch = button
		#Play audio if user presses play button
		if self.playButton.collidepoint(coord):
			PlayStandardNotes(self.standardNotes).generateTone()
		#Return to start screen if user presses quit
		elif self.quitButton.collidepoint(coord):
			self.standardStaff = False
			self.startScreen = True
			self.standardNotes = []
		#Go to save window if user presses save
		elif self.saveButton.collidepoint(coord):
			self.standardStaff = False
			self.saveWindow = True
			#Reset filename before user goes to save screen
			self.filename = ""
		#Determine if a note should go into the staff with the coord
		self.determineNote(coord)
	
	#Determine the note inputted to staff if user presses mouse
	def determineNote(self,coord):
		(xCoord,yCoord) = coord
		#Do nothing if mousePress isn't near a staff at all
		if (xCoord < 100) or (xCoord > 900):
			return
		#Determine which staff the use pressed in
		region = yCoord / 200
		#Do nothing if user pressed in region where staff isn't
		if region == 0:
			return
		#Keep reducing yCoord until it's feasible to determine a letter
		while (yCoord >= 200):
			yCoord -= 200
		#Define bounds for yCoord to determine if user really added note
		minYCoord, maxYCoord = 42, 150
		#Determine letter to add if user pressed within this  region
		if minYCoord <= yCoord <= maxYCoord:
			self.determineLetter(yCoord)

	#Determine letter to add to staff if user pressed within correct region
	def determineLetter(self,yCoord):
		#Adjust yCoord so that user can press around the note and stil add it
		yCoord += self.halfStepHeight/2
		#Offset yCoord by 44 so that we can use division to find correct index
		yCoord -= 44
		index = yCoord / self.halfStepHeight
		#Add note and current length, pitch, and type to notes list
		note = (index,
			self.selectedLength,
			self.selectedPitch,
			self.selectedType)
		self.standardNotes.append(note)

	#Run function for setup screen for musical staff
	def runStandardStaffSetup(self):
		#Draw setup screen before running it
		self.redrawStandardStaffSetup()
		while self.standardStaffSetup:
			#Continuously respond to user actions while running
			self.respondToStandardStaffSetupActions()
			#Don't show setup screen if user chooses to go elsewhere
			if not self.standardStaffSetup:
				break

	#Draw staff setup. Store all necessary buttons for user mousepresses.
	def redrawStandardStaffSetup(self):
		(self.timeButtons,
			self.titleBox,
			self.composerBox,
			self.goButton,
			self.backButton) = StaffSetupDrawings(self.window,
								self.selectedTime,
								self.title,	
								self.composer,
								"Staff Setup").redrawAll()

	#Respond to user actions in staff setup window
	def respondToStandardStaffSetupActions(self):
		for event in pygame.event.get():
			#Respond to user mousepresses
			if event.type == pygame.MOUSEBUTTONDOWN:
				coord = pygame.mouse.get_pos()
				self.respondToStaffSetupMousePress(coord)
				#Redraw window on every mousePress
				self.redrawStandardStaffSetup()
			#Add text to 
			elif event.type == pygame.KEYDOWN:
				self.typeText(event)
				self.redrawStandardStaffSetup()
			elif event.type == pygame.QUIT:
				sys.exit()

	#Respond to user mousePresses on staff setup window
	def respondToStaffSetupMousePress(self,coord):
		#Change selected time if user presses time button
		for button in xrange(len(self.timeButtons)):
			if self.timeButtons[button].collidepoint(coord):
				self.selectedTime = button
		#Allow user to input title if user clicks on title textbox
		if self.titleBox.collidepoint(coord):
			self.titleInput = True
			self.composerInput = False
			#Reset title if user clicks on it
			self.title = ""
		#Allow user to input composer if user clicks on composer textbox
		elif self.composerBox.collidepoint(coord):
			self.titleInput = False
			self.composerInput = True
			#Reset composer if user clicks on it
			self.composer = ""
		#Move onto musical staff once user clicks go
		elif self.goButton.collidepoint(coord):
			self.standardStaffSetup = False
			self.standardStaff = True
		#Return to start screen if user presses back
		elif self.backButton.collidepoint(coord):
			self.standardStaffSetup = False
			self.startScreen = True

	#Run function for air drum playing
	def runFreePlay(self):
		#Call run function in FreePlay class
		FreePlay(self.window).run()
		#Once function is done, move back to startScreen
		self.freePlay = False
		self.startScreen = True

	#Run function for startScreen
	def runStartScreen(self):
		#Only draw startscreen once in the beginning
		(self.freePlayButton,
			self.helpButton,
			self.staffButton) = StartScreenDrawings(self.window).redrawAll()
		while True:
			#Continously respond to user actions on startscreen
			self.respondToStartScreenActions()
			#Move onto another screen once user decides to move
			if not self.startScreen:
				break

	#Respond to user actions on startscreen
	def respondToStartScreenActions(self):
		for event in pygame.event.get():
			#Respond to user mousePresses
			if event.type == pygame.MOUSEBUTTONDOWN:
				#Go to freePlay if user clicks its button
				if self.freePlayButton.collidepoint(pygame.mouse.get_pos()):
					self.startScreen = False
					self.freePlay = True
				#Go to help screen if user presses its button
				elif self.helpButton.collidepoint(pygame.mouse.get_pos()):
					self.startScreen = False
					self.helpScreen = True
				#Go to staff setup if user presses staff button
				elif self.staffButton.collidepoint(pygame.mouse.get_pos()):
					self.standardStaffSetup = True
					self.startScreen = False
			#Quit window if user presses x button on top right of window
			elif event.type == pygame.QUIT:
				sys.exit()

#Class to draw our help screen
class HelpScreenDrawing(object):
	#Define inputted window and its dimensions
	def __init__(self,window):
		self.window = window
		(self.width,self.height) = self.window.get_size()

	#Define color of all text as black
	def initAnimation(self):
		self.textColor = (0,0,0)		

	#Draw all of help screen
	def redrawAll(self):
		self.initAnimation()
		self.drawBackground()
		self.drawWindowHeader()
		self.drawInstructionsBox()
		self.drawBackButton()
		#Reset display of pygame window
		pygame.display.flip()
		#Return button for user mousepresses
		return self.backButton

	#Draw background for help screen
	def drawBackground(self):
		#Make notes image background of window
		background = pygame.image.load("notesBackground.jpg")
		self.window.blit(background,(0,0))

	#Draw header for help screen window
	def drawWindowHeader(self):
		header = "Instructions"
		#Center text, keep it near top
		textX = self.width / 2
		textY = self.height / 16
		fontSize = 100
		self.drawText(textX,textY,header,fontSize)

	#Draw box with all help instructions for user
	def drawInstructionsBox(self):
		#Setup box so that it takes up most of window
		#Top left corner near top left of window
		self.startX, self.startY = 100, 100
		self.endX, self.endY = self.width - self.startX, self.height - 50
		#Define width and height to take up most of window
		self.boxWidth = self.endX - self.startX
		self.boxHeight = self.endY - self.startY
		rect = (self.startX,self.startY,self.boxWidth,self.boxHeight)
		fill = (213,165,33)
		outlineWidth = 0
		#Draw box rectangle and black border
		pygame.draw.rect(self.window,fill,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Draw line through half of screen to separate two instructions
		lineStart = (self.width / 2,self.startY)
		lineEnd = (self.width / 2, self.endY)
		pygame.draw.line(self.window,(0,0,0),lineStart,lineEnd)
		#Draw instructions for each mode
		self.drawStaffHelp()
		self.drawFreePlayHelp()

	#Draw help for staff screen
	def drawStaffHelp(self):
		self.drawStaffImage()
		self.drawStaffHeader()
		self.drawStaffText()

	#Input image of what user would see on staff screen to make it easier
	def drawStaffImage(self):
		image = pygame.image.load("staffimage.jpg")
		location = (x,y) = (165,180)
		self.window.blit(image,location)

	#Display instructions text for staff window
	def drawStaffText(self):
		staffText = [
			"Note options are shown on the top.",
			"Click on your note length, type, and",
			"pitch of choice. To place a note in ",
			"the staff, simply click its location ",
			"in the staff. Press backspace to remove",
			"the last note in the staff. If you want",
			"to hear what you've written, click the",
			"Play button and your music will be ",
			"played back synthetically. Like what",
			"you've written? Click save to save your",
			"music as an audio file for keeps."]
		#Iterate through all texts, display them in window sequentially
		for header in xrange(len(staffText)):
			textX = self.startX + 10
			textY = (self.height / 2) + (25 * header)
			words = staffText[header]
			fontSize = 30
			self.drawHelpText(textX,textY,words,fontSize) 

	#Draw header for staff instructions. Keep it near top left of box
	def drawStaffHeader(self):
		header = "Staff"
		fontSize = 60
		textX = self.startX + (self.boxWidth / 4)
		textY = self.startY + 50
		self.drawText(textX,textY,header,fontSize)

	#Draw help information for free play air drum mode
	def drawFreePlayHelp(self):
		self.drawFreePlayHeader()
		self.drawFreePlayText()
		self.drawFreePlayImage()

	#Input image of what user would see for ease of use
	def drawFreePlayImage(self):
		image = pygame.image.load("freeplayimage.jpg")
		location = (x,y) = (565,180)
		self.window.blit(image,location)

	#Draw header for free play instructions
	def drawFreePlayHeader(self):
		header = "Free Play"
		fontSize = 60
		#Keep header near top right of window
		textX = self.startX + (3 * self.boxWidth / 4)
		textY = self.startY + 50
		self.drawText(textX,textY,header,fontSize)

	#Draw text instructions for free play mode
	def drawFreePlayText(self):
		freePlayText = [
			"Prior to FreePlay, make sure you have",
			"your colored drumsticks and you're in",
			"appropriate lighting conditions. Make",
			"sure you're not wearing red or blue!",
			"Hold up your drum sticks and they'll be", 
			"tracked on the window. Hit a rectangle",
			"region to play a drum. The top right ",
			"rectangle is a smash, the bottom right",
			"is a snare, the bottom left is a tom,",
			"and the top left is a highhat. That's it!"]
		#Iterate through all texts, display them sequentially
		for header in xrange(len(freePlayText)):
			textX = self.startX + (self.boxWidth/2) + 10
			textY = (self.height / 2) + (25 * header)
			words = freePlayText[header]
			fontSize = 30
			self.drawHelpText(textX,textY,words,fontSize)

	#Helper function to display instructions text for each mode
	def drawHelpText(self,textX,textY,header,fontSize):
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		self.window.blit(text,(textX,textY))

	#Draw back button to return to startscreen
	def drawBackButton(self):
		#Orient button on bottom left of screen
		startX = 20
		endY = self.height - 20
		buttonHeight = 45
		buttonWidth = 60
		startY = endY - buttonHeight
		fill = (213,165,33)
		rect = (startX,startY,buttonWidth,buttonHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,fill,rect,0)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		self.backButton = pygame.Rect(startX,startY,buttonWidth,buttonHeight)
		textX = startX + buttonWidth / 2
		textY = startY + buttonHeight / 2
		header = "Back"
		fontSize = 25
		self.drawText(textX,textY,header,fontSize)

	#Helper function to draw centered text on the window
	def drawText(self,textX,textY,header,fontSize):
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		#Redefine center coordinates of rendered font
		textPosition = text.get_rect()
		textPosition.centerx = textX
		textPosition.centery = textY
		self.window.blit(text,textPosition)	

#Class to draw start screen
class StartScreenDrawings(object):
	#Define initial window and its dimensions
	def __init__(self,window):
		self.window = window
		(self.width,self.height) = self.window.get_size()
		
	#Define initial parameters for animation
	def initStartScreen(self):
		self.options = ["Select Mode:", "Free Play",
						"Standard Staff", "Help"]
		#Define color for all text to be white
		self.textColor = (255,255,255)

	#Redraw everything for start screen
	def redrawAll(self):
		self.initStartScreen()
		self.drawStartScreenBackground()
		self.drawStartScreenHeader()
		self.drawOptionsHeader()
		self.drawFreePlayButton()
		self.drawStandardStaffButton()
		self.drawHelpButton()
		#Reupdate pygame window with new drawings
		pygame.display.flip()
		#Return buttons for user mousepresses
		return (self.freePlayButton,
				self.helpButton,self.staffButton)

	#Draw background for start screen window
	def drawStartScreenBackground(self):
		#Import background with musical notes image
		background = pygame.image.load("notesBackground.jpg")
		self.window.blit(background,(0,0))

	#Draw header title for start screen
	def drawStartScreenHeader(self):
		#Center text in middle of window near top
		textX = self.width / 2
		textY = self.height / 20
		fontSize = 80
		font = pygame.font.Font(None,fontSize)
		header = "Welcome to SuperEditor!"
		text = font.render(header,1,self.textColor)
		#Recenter rendered text with text location
		textPosition = text.get_rect()
		textPosition.centerx = textX
		textPosition.centery = textY
		self.window.blit(text,textPosition)

	#Draw text header for user to select mode
	def drawOptionsHeader(self):
		header = self.options[0]
		#Center this header in middle of window, lower than title
		textX = self.width / 2
		textY = self.height / (len(self.options) + 1)
		fontSize = 60
		self.drawText(textX,textY,header,fontSize)

	#Draw button for user to go to free play mode
	def drawFreePlayButton(self):
		header = self.options[1]
		#Center text in middle of window, lower than options header
		textX = centerX = self.width / 2
		textY = centerY = (2 * self.height) / (len(self.options) + 1)
		fontSize = 40
		#Store button for user mousepresses
		self.freePlayButton = self.drawButton(centerX,centerY)
		self.drawText(textX,textY,header,fontSize)

	#Draw button for user to go to musical staff mode
	def drawStandardStaffButton(self):
		header = self.options[2]
		#Center text in middle of window, lower than freeplay mode
		textX = centerX = self.width / 2
		textY = centerY = (3 * self.height) / (len(self.options) + 1)
		fontSize = 40
		#Store button for user mousepresses
		self.staffButton = self.drawButton(centerX,centerY)
		self.drawText(textX,textY,header,fontSize)

	#Draw button for user to go to help screen
	def drawHelpButton(self):
		header = self.options[3]
		#Center text in middle of window somewhat near bottom
		textX = centerX = self.width / 2
		textY = centerY = (4 * self.height) / (len(self.options) + 1)
		fontSize = 40
		#Store button for mousepresses
		self.helpButton = self.drawButton(centerX,centerY)
		self.drawText(textX,textY,header,fontSize)

	#Standard buttondraw function for start screen
	def drawButton(self,centerX,centerY):
		#Define button size
		buttonWidth = 300
		buttonHeight = 100
		#Define start location of rectangle
		startX = centerX - (buttonWidth / 2)
		startY = centerY - (buttonHeight / 2)
		rect = (startX,startY,buttonWidth,buttonHeight)
		color = (213,165,33)
		outlineWidth = 0
		#Draw button and outline it with black rectangle
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Retrieve button and return it for user mousepresses
		button = pygame.Rect(startX,startY,buttonWidth,buttonHeight)
		return button

	#Standard textDraw function for centered text
	def drawText(self,textX,textY,header,fontSize):
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,(255,255,255))
		#Redefine center coordinates of rendered text
		textPosition = text.get_rect()
		textPosition.centerx = textX
		textPosition.centery = textY
		self.window.blit(text,textPosition)

#Class to run free play air drums
class FreePlay(object):
	#Define initial input window and its dimensions
	def __init__(self,window):
		self.window = window
		(self.width,self.height) = self.window.get_size()
		
	#Define initial values for freeplay mode
	def initAnimation(self):
		#Define all text to be black
		self.textColor = (0,0,0)
		#Define parameter for when this run is over
		self.run = True
		#Retrieve sound data for all parts of drum set.
		self.snareSound = pygame.mixer.Sound("snare2short.wav")
		self.highhatSound = pygame.mixer.Sound("highhatshort.wav")
		self.tomSound = pygame.mixer.Sound("lowsnare.wav")
		self.smashSound = pygame.mixer.Sound("smash.wav")
		#Initialize coordinates of location of red and blue
		self.blueX0, self.blueY0 = 0, 0
		self.redX0, self.redY0 = 0, 0
		self.blueX1, self.blueY1 = 0, 0
		self.redX1, self.redY1 = 0, 0
		#Assume red and blue at start is not inside drum
		self.blueInsidePrevious = False
		self.redInsidePrevious = False
		self.blueInside = False
		self.redInside = False
		#Fill window with black background before going onto camera input
		self.window.fill((0,0,0))

	#Run function for free play modde
	def run(self):
		self.initAnimation()
		#Initialized vidocapture
		vidCapture = cv2.VideoCapture(0)
		while True:
			#Perform all drawings and camera operations
			self.drawQuitButton()
			self.respondToActions()
			ret, self.frame = vidCapture.read()
			self.resizeCameraInput()
			self.drawDrums()
			self.performBlueTracking()
			self.performRedTracking()
			self.drawBlueTrackers()
			self.drawRedTrackers()
			#Reset variable values with every frame
			self.blueX0,self.blueY0 = self.blueX1,self.blueY1
			self.redX0,self.redY0 = self.redX1,self.redY1
			self.blueInsidePrevious = self.blueInside
			self.redInsidePrevious = self.redInside
			#Convert open cv2 image to show in pygame
			image = self.cvimage_to_pygame()
			#Show frame in pygame window and update screen
			self.window.blit(image,(0,0))
			pygame.display.update()
			#End run if value for run changes upon user input
			if not self.run:	break

	#Resize camera frame
	#Learned how to do this here
	#http://www.pyimagesearch.com/2014/01/20/basic-image-manipulations-in-
	#python-and-opencv-resizing-scaling-rotating-and-cropping/
	#and
	#http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/
	#py_imgproc/py_geometric_transformations/py_geometric_transformations.html
	def resizeCameraInput(self):
		ratio = 1000.0 / self.frame.shape[1]
		dim = (1000, int(self.frame.shape[0] * ratio))
		self.frame = cv2.resize(self.frame,dim,interpolation = cv2.INTER_CUBIC)

	#Draw button for user to quit and return to start menu
	def drawQuitButton(self):
		#Orient button near bottom left of screen
		startX = 20
		startY = 750
		buttonWidth = 80
		buttonHeight = 50
		rect = (startX,startY,buttonWidth,buttonHeight)
		color = (213,165,33)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store button rect for user mousepresses
		self.quitButton = pygame.Rect(startX,startY,buttonWidth,buttonHeight)
		
		header = "Quit"
		fontSize = 30
		textX = startX + buttonWidth / 2
		textY = startY + buttonHeight / 2
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,(0,0,0))

		textPosition = text.get_rect()
		textPosition.centerx = textX
		textPosition.centery = textY
		self.window.blit(text,textPosition)

	#Respond to user actions on freeplay screen
	def respondToActions(self):
		for event in pygame.event.get():
			#Respond to user mousepresses
			if event.type == pygame.MOUSEBUTTONDOWN:
				coord = pygame.mouse.get_pos()
				#Quit freeplay window if user clicks on quit button
				if self.quitButton.collidepoint(coord):
					self.run = False
			#Quit application if user x's out window
			elif event.type == pygame.QUIT:
				sys.exit()

	#Determine trackers for blue color
	#Learned about contours with opencv documentation
	#http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/
	#py_contours/py_contour_features/py_contour_features.html
	def drawBlueTrackers(self):
		try:
			#Determine areas of blue region in frame
			areas = self.blueContours[0]
			#Determine the center moment of inertia of the found blue contours
			moment = cv2.moments(areas)
			#This method to extract moment data is copied verbatim from cv2
			self.blueX1 = int(moment['m10']/moment['m00'])
			self.blueY1 = int(moment['m01']/moment['m00'])
			#Determine speed of stick based on previous position
			speed = FreePlay.determineDistance(self.blueX0,self.blueY0,
												self.blueX1,self.blueY1)
			#Draw blue circle to follow stick
			radius, color, thickness = 15, (255,255,255), 4
			cv2.circle(self.frame,(self.blueX1,self.blueY1),
						radius,color,thickness)
			#Determine sound to make with drum stick
			self.determineBlueSound(speed)
		#If no contours are found in image, code above will crash.
		#Do nothing if no blue is found.
		except:
			pass

	#Determine trackers for red color
	#Learned about contours with opencv documentation
	#http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/
	#py_contours/py_contour_features/py_contour_features.html
	def drawRedTrackers(self):
		try:
			#Determine areas of red region in frame
			areas = self.redContours[0]
			#Determine the center moment of inertia of the found recd contours
			moment = cv2.moments(areas)

			#Determine coordinates of current moment
			#This extraction of moment data is copied verbatim fromm cv2 docs
			self.redX1 = int(moment['m10']/moment['m00'])
			self.redY1 = int(moment['m01']/moment['m00'])

			#Determine speed based on prior red coordinates
			speed = FreePlay.determineDistance(self.redX0,self.redY0,
												self.redX1,self.redY1)

			radius, color, thickness = 15, (255,255,255), 4
			#Draw red circle to follow red sticks
			cv2.circle(self.frame,(self.redX1,self.redY1),
						radius,color,thickness)
			#Determine sound that red stick should make based on location
			self.determineRedSound(speed)
			#If no contours are found, then above code will crash.
			#Raise exception in case no red is found,
		except:
			self.redInside = False

	def determineBlueSound(self,speed):
		#Determine if blue falls within one of drum set regions
		#and if it's fast enough to play the sound
		if (self.snareX0 < self.blueX1 < self.snareX1 and
			 self.snareY0 < self.blueY1 < self.snareY1 and speed > 10):
			#Define blue as inside a region if it is
			self.blueInside = True
			#Only play a sound if blue wasn't previously in drum
			if self.blueInside and not self.blueInsidePrevious:
				self.snareSound.play()
		elif (self.highhatX0 < self.blueX1 < self.highhatX1 and 
				self.highhatY0 < self.blueY1 < self.highhatY1 and speed > 10):
			#Define blue as inside a region if it is
			self.blueInside = True
			#Only play a sound if blue wasn't previously in drum
			if self.blueInside and not self.blueInsidePrevious:
				self.highhatSound.play()
		elif (self.tomX0 < self.blueX1 < self.tomX1 and 
				self.tomY0 < self.blueY1 < self.tomY1 and speed > 10):
			#Define blue as inside a region if it is
			self.blueInside = True
			#Only play a sound if blue wasn't previously in drum
			if self.blueInside and not self.blueInsidePrevious:
				self.tomSound.play()
		elif (self.smashX0 < self.blueX1 < self.smashX1 and
			 self.smashY0 < self.blueY1 < self.smashY1 and speed > 10):
			#Define blue as inside a region if it is
			self.blueInside = True
			#Only play a sound if blue wasn't previously in drum
			if self.blueInside and not self.blueInsidePrevious:
				self.smashSound.play()
		#Drum not in region if none applicable
		else: self.blueInside = False

	#Determine what sound red tracking should make
	def determineRedSound(self,speed):
		#Determine if red falls within one of drum set regions
		#and if it's fast enough to play the sound
		if (self.snareX0 < self.redX1 < self.snareX1 and 
			self.snareY0 < self.redY1 < self.snareY1 and speed > 10):
			#Define red as inside a region if it is
			self.redInside = True
			#Only play sound if red wasn't previously in drum
			if self.redInside and not self.redInsidePrevious:
				self.snareSound.play()
		elif self.highhatX0 < self.redX1 < self.highhatX1 and self.highhatY0 < self.redY1 < self.highhatY1:
			#Define red as inside a region if it is
			self.redInside = True
			#Only play sound if red wasn't previously in drum
			if self.redInside and not self.redInsidePrevious:
				self.highhatSound.play()
		elif self.tomX0 < self.redX1 < self.tomX1 and self.tomY0 < self.redY1 < self.tomY1:
			#Define red as inside a region if it is
			self.redInside = True
			#Only play sound if red wasn't previously in drum
			if self.redInside and not self.redInsidePrevious:
				self.tomSound.play()
		elif self.smashX0 < self.redX1 < self.smashX1 and self.smashY0 < self.redY1 < self.smashY1:
			#Define red as inside a region if it is
			self.redInside = True
			#Only play sound if red wasn't previously in drum
			if self.redInside and not self.redInsidePrevious:
				self.smashSound.play()
		#Drum not in region if not applicable
		else:
			self.redInside = False

	#Draw drum regions on frame
	def drawDrums(self):
		#Define regions to be white hollow rectangles
		color = (255,255,255)
		drumWidth,drumHeight,outlineWidth = 170, 215, 3
		#Draw each rectangle for each specific drum typee
		highhatStart = (self.highhatX0, self.highhatY0) = (40,80)
		highhatEnd = (self.highhatX1,
						self.highhatY1) = (self.highhatX0 + drumWidth,
											self.highhatY0 + drumHeight)
		cv2.rectangle(self.frame,highhatStart,highhatEnd,color,3)
		snareStart = (self.snareX0,self.snareY0) = (290,455)
		snareEnd = (self.snareX1,
					self.snareY1) = (self.snareX0 + drumWidth,
										self.snareY0 + drumHeight)
		cv2.rectangle(self.frame,snareStart,snareEnd,color,outlineWidth)
		tomStart = (self.tomX0,self.tomY0) = (540,455)
		tomEnd = (self.tomX1,
					self.tomY1) = (self.tomX0 + drumWidth,
									self.tomY0 + drumHeight)
		cv2.rectangle(self.frame,tomStart,tomEnd,color,outlineWidth)
		smashStart = (self.smashX0,self.smashY0) = (790,80)
		smashEnd = (self.smashX1,
					self.smashY1) = (self.smashX0 + drumWidth,
									self.smashY0 + drumHeight)
		cv2.rectangle(self.frame,smashStart,smashEnd,color,outlineWidth)

	#Perform tracking for blue color
	#I learned basic image processing on opencv2 documentation
	def performBlueTracking(self):
		#Convert bgr frame to hsv (hue-value-saturation)
		hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
		#Define kernel
		kernel = np.ones((5,5),np.uint8)
		#Define upper and lower blue thresholds
		lowerBlue = np.array([100,150,80], dtype = np.uint8)
		upperBlue = np.array([130,255,255], dtype = np.uint8)

		#Mask the frame with the thresholds to only output blue
		mask = cv2.inRange(hsv, lowerBlue, upperBlue)

		#Perform opening to accentuate smaller blue regions
		opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		#Perform closing to get rid of small blue white noise
		closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

		#Use threshold of closing to find contours of image. Store contours
		ret, thresh = cv2.threshold(closing,127,255,0)
		contours, hierarchy = cv2.findContours(thresh,1,2)
		self.blueContours = contours

	#Perform tracking for red color
	#I learned about basic image processing on oopencv2 documentation
	def performRedTracking(self):
		#Convert bgr frame to hsv (hue-value-saturation)
		hsv = cv2.cvtColor(self.frame,cv2.COLOR_BGR2HSV)
		#Define kernel
		kernel = np.ones((5,5),np.uint8)
		#Define upper and lower red thresholds
		lowerRed = np.array([160,100,180], dtype = np.uint8)
		upperRed = np.array([180,255,255], dtype = np.uint8)

		#Mask the frame with the thresholds to only output red
		mask = cv2.inRange(hsv,lowerRed,upperRed)

		#Perform opening to accentuate smaller red regions
		opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		#Perform closing to get rid of small red white noise
		closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

		#Use threshold of closing to find contours if image. Store contours.
		ret, thresh = cv2.threshold(closing,127,255,0)
		contours, hierarchy = cv2.findContours(thresh,1,2)
		self.redContours = contours

	#Determine distance between two points with distance formula
	@staticmethod
	def determineDistance(x0,y0,x1,y1):
		xComp = abs(x0-x1)
		yComp = abs(y0-y1)
		return (xComp**2 + yComp**2)**0.5

	#Convert opencv image to pygame format to show in pygame window
	#This was almost all copied verbatim
	#http://stackoverflow.com/questions/19306211/
	#opencv-cv2-image-to-pygame-image
	def cvimage_to_pygame(self):	 
		#Switch BGR to RBG
	    image = cv2.cvtColor(self.frame,cv2.COLOR_BGR2RGB)
	    #Reverse frame so it doesn't look backwards to user
	    for row in xrange(len(image)):
	    	image[row] = image[row][::-1]
	    #Perform operation to get pygame image
	    return pygame.image.frombuffer(image.tostring(), image.shape[1::-1],
	                                   "RGB")

#Class to draw staff setup screen
class StaffSetupDrawings(object):
	#Define initial input variables, define size of window
	def __init__(self,window,selectedTime,title,composer,header):
		self.window = window
		(self.width,self.height) = self.window.get_size()
		self.header = header
		self.selectedTime = selectedTime
		self.title = title
		self.composer = composer
		self.textColor = (255,255,255)

	#Define initial variables for animation
	def initAnimation(self):
		#Define options list for options to be inputted in staff
		self.options = ["Time Signature:",
						"Title:", "Composer:"]

	#Redraw everything for staff setup screen
	def redrawAll(self):
		#Define initial variables
		self.initAnimation()
		#Perform all draw functions and draw buttons
		self.drawBackground()
		self.drawWindowHeader()
		self.drawOptions()
		self.drawGoButton()
		self.drawBackButton()
		#Update pygame window
		pygame.display.flip()
		#Return buttons for user mousepresses.
		return(self.timeButtons,
			self.titleBox,
			self.composerBox,
			self.goButton,
			self.backButton)
		
	#Draw background of whole window
	def drawBackground(self):
		#Set notesbackground for background of window
		background = pygame.image.load("notesBackground.jpg")
		self.window.blit(background,(0,0))

	#Draw header for whole window
	def drawWindowHeader(self):
		#Locate near top center of window
		textX = self.width / 2
		textY = self.height / 10
		fontSize = 100
		self.drawText(textX,textY,self.header,fontSize)

	#Draw all options displayed for staff setup
	def drawOptions(self):
		#Draw box for all options
		self.sideMargin = startX = startY = 200
		self.boxWidth = self.width - 2 * self.sideMargin
		self.boxHeight = self.height - 2 * self.sideMargin
		color = (213,165,33)
		rect = (startX,startY,self.boxWidth,self.boxHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)

		#Draw all options
		self.drawTimeSignatureOptions()
		self.drawTitleInput()
		self.drawComposerInput()

	#Draw choices for user to select time signature
	def drawTimeSignatureOptions(self):
		#Keep all buttons and labels 1/4 from top of options box
		textX = self.sideMargin + 10
		textY = self.sideMargin + (1*self.boxHeight/(len(self.options)+1))
		header = self.options[0]
		fontSize = 30
		#Draw text label for time signature
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		textPosition = text.get_rect()
		textPosition.centery = textY
		textPosition.centerx = textX + 80
		textEnd = textPosition.centerx + 40
		self.window.blit(text,textPosition)
		#Draw button selecion for time signatures
		self.drawTimeButtons(textEnd,textY)

	#Draw buttons for time signature choices
	def drawTimeButtons(self,textEnd,textY):
		#Display 3 choices for time signature
		choices = ["2/4","3/4","4/4"]
		#Create list of buttons to return
		self.timeButtons = []
		startX = textEnd + 10
		endX = self.sideMargin + self.boxWidth - 10
		regionWidth = endX - startX
		#Iterate through all choices, create buttons and rectangles for each
		for i in xrange(len(choices)):
			xCoord = startX + (i + 1) * (regionWidth / (len(choices) + 1))
			yCoord = textY
			#Create 50 x 50 button
			boxWidth = boxHeight = 50
			boxStartX,boxStartY = xCoord-(boxWidth/2), yCoord-(boxHeight/2)
			rect = (boxStartX,boxStartY,boxWidth,boxHeight)
			#Make color of selected time signature black
			if i == self.selectedTime: color = (0,0,0)
			else:	color = (213,165,33)
			#Draw rectangle and outlining rectangle for each button
			outlineWidth,fontSize = 0, 35
			pygame.draw.rect(self.window,color,rect,outlineWidth)
			pygame.draw.rect(self.window,(0,0,0),rect,1)
			button = pygame.Rect(boxStartX,boxStartY,boxWidth,boxHeight)
			#Add button to buttons list
			self.timeButtons.append(button)
			#Draw text label for button
			font = pygame.font.Font(None,fontSize)
			text = font.render(choices[i],1,self.textColor)
			textPosition = text.get_rect()
			textPosition.centerx, textPosition.centery = xCoord,yCoord
			self.window.blit(text,textPosition)

	#Draw titleInput for user to type in title manually
	def drawTitleInput(self):
		#Orient title label on left of options box
		textX = self.sideMargin + 10
		#Keep title label 1/2 way from top of options box
		textY = self.sideMargin + (2*self.boxHeight / (len(self.options) + 1))
		#Retrieve text for header
		header = self.options[1]
		#Draw text on window
		fontSize = 30
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		textPosition = text.get_rect()
		textPosition.centerx = textX + 25
		textPosition.centery = textY 
		self.window.blit(text,textPosition)
		#Draw titleBox that contains title text
		self.drawTitleBox(textY)

	#Draw titleInput box that shows title text
	def drawTitleBox(self,textY):
		text = self.title
		#Determine proper dimensions for box to fit inside options box
		startX, startY = self.sideMargin + 70, textY - 30
		endX, endY = self.width - self.sideMargin - 10, textY + 30
		boxWidth, boxHeight = endX - startX, endY - startY
		#Draw box rectangle
		rect = (startX,startY,boxWidth,boxHeight)
		fill = (255,255,255)
		outlineWidth = 0
		pygame.draw.rect(self.window,fill,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Save titlebox as button for mousepress
		self.titleBox = pygame.Rect(startX,startY,boxWidth,boxHeight)
		#Draw Title Text
		textX = startX + 10
		textY -= 10
		words = self.title
		fontSize = 30
		textColor = (0,0,0)
		font = pygame.font.Font(None,fontSize)
		text = font.render(words,1,textColor)
		self.window.blit(text,(textX,textY))

	#Draw composerInput for user to type in composer manually
	def drawComposerInput(self):
		#Orient composer label on left of options box
		textX = self.sideMargin + 20
		#Keep composer label 3/4 from top of options box
		textY = self.sideMargin + (3*self.boxHeight/(len(self.options)+1))
		#Retrieve text for header
		header = self.options[2]
		#Draw text on window
		fontSize = 30
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		textPosition = text.get_rect()
		textPosition.centerx = textX + 40
		textPosition.centery = textY
		self.window.blit(text,textPosition)
		#Draw composer box that contains composer text
		self.drawComposerBox(textY)

	#Draw box for manual composer text input
	def drawComposerBox(self,textY):
		text = self.title
		#Determine proper dimensions for box to fit inside options box
		startX, startY = self.sideMargin + 120, textY - 30
		endX, endY = self.width - self.sideMargin - 10, textY + 30
		boxWidth, boxHeight = endX - startX, endY - startY
		#Draw box rectangle
		rect = (startX,startY,boxWidth,boxHeight)
		fill = (255,255,255)
		outlineWidth = 0
		pygame.draw.rect(self.window,fill,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Save composerBox as button for mousepresses
		self.composerBox = pygame.Rect(startX,startY,boxWidth,boxHeight)
		#Draw Composer Text
		textX = startX + 10
		textY -= 10
		words = self.composer
		fontSize = 30
		textColor = (0,0,0)
		font = pygame.font.Font(None,fontSize)
		text = font.render(words,1,textColor)
		#Reupdate pygame window with new drawings
		self.window.blit(text,(textX,textY))

	#Draw button to move onto music staff
	def drawGoButton(self):
		#Orient go button near bottom right of screen
		endX = self.width - self.sideMargin
		startX = endX - 50
		startY = self.sideMargin + self.boxHeight + 10
		buttonWidth, buttonHeight = 80, 60
		#Draw button rectangle withh black outline
		rect = (startX, startY, buttonWidth, buttonHeight)
		fill = (213,165,33)
		outlineWidth = 0
		pygame.draw.rect(self.window,fill,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store button location for user mousepresses
		self.goButton = pygame.Rect(startX,startY,buttonWidth,buttonHeight)
		words = "Go!"
		fontSize = 40
		textColor = (0,0,0)
		font = pygame.font.Font(None,fontSize)
		text = font.render(words,1,textColor)
		#Update pygame window with new drawings
		self.window.blit(text,(startX + 17,startY + 17))

	#Draw button to move back to start screen
	def drawBackButton(self):
		#Orient back button on bottom left of screen
		startX = self.sideMargin - 15
		startY = self.sideMargin + self.boxHeight + 15
		buttonWidth, buttonHeight = 80,60
		#Draw back button rectangle with black outline
		rect = (startX,startY,buttonWidth,buttonHeight)
		fill = (213,165,33)
		outlineWidth = 0
		pygame.draw.rect(self.window,fill,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store back button for user mousepresses
		self.backButton = pygame.Rect(startX,startY,buttonWidth,buttonHeight)
		#Draw back button text
		words = "Back"
		fontSize = 35
		font = pygame.font.Font(None,fontSize)
		textColor = (0,0,0)
		text = font.render(words,1,textColor)
		self.window.blit(text,(startX + 10, startY + 15))

	#Helper function to draw centered text on window
	def drawText(self,textX,textY,header,fontSize):
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		#Redefine centerX and centerY for rendered text
		textPosition = text.get_rect()
		textPosition.centerx = textX
		textPosition.centery = textY
		#Update pygame window with new drawings
		self.window.blit(text,textPosition)

#Class to draw music staff window
class StandardStaffDrawings(object):
	#Define initial input variables, define window dimensions
	def __init__(self,window,selectedTime,
				selectedType,selectedLength,selectedPitch,
				notes,title,composer):
		self.window = window
		self.window.set_colorkey((255,255,255))
		(self.width,self.height) = self.window.get_size()
		self.selectedTime = selectedTime
		self.selectedType = selectedType
		self.selectedLength = selectedLength
		self.selectedPitch = selectedPitch
		self.notes = notes
		self.title = title
		self.composer = composer

	#Define initial values for staff screena animation
	def initAnimation(self):
		self.textColor = (0,0,0)
		self.trebleClef = pygame.image.load("treble-clef.jpg")
		self.noteTypes = ["Note","Rest"]
		self.noteLengths = ["1","1/2","1/4","1/8","1/16"]
		self.noteLengthValues = [1,0.5,0.25,0.125,0.0625]
		self.pitchTypes = ["Natural","Sharp","Flat"]
		self.playBacks = ["Play"]
		self.wholeStepHeight = 16
		self.halfStepHeight = 8

	#Redraw all of music staff screen
	def redrawAll(self):
		#Define initial variables
		self.initAnimation()
		#Peform all draw functions
		self.drawBackground()
		self.drawTitleAndComposer()
		self.drawStaffs()
		self.drawNotes()
		self.drawOptions()
		self.drawQuitButton()
		#Update pygame window with new drawings
		pygame.display.flip()
		#Return buttons for user mousepresses
		return (self.noteTypeButtons,self.noteLengthButtons,
				self.notePitchButtons,self.playButton,
				self.quitButton,self.saveButton)

	#Draw music notes on staff
	def drawNotes(self):
		#Create new surface to draw notes on
		surface = pygame.Surface((self.width,self.height))
		#Fill surface white to start off
		#Define white colorkey to make all white things transparent
		surface.fill((255,255,255)),surface.set_colorkey((255,255,255))
		#Define length of measure based on time signature
		measureLength = float(self.selectedTime + 2) / 4
		numOfMeasures, noteSpacing, startX,xCoord= 1, 40, 150, 150
		#Store list of all notes so far in loop
		currentNotes = []
		for note in xrange(len(self.notes)):
			(yIndex,length,pitch,noteType) = self.notes[note]
			#Add note to currentNotes list
			currentNotes.append(self.notes[note])
			#Determine total time length of all notes so far in loop
			totalLength = self.determineTotalLength(currentNotes)
			#Add spacing for next note
			xCoord += noteSpacing
			#Add extra spacing if a measure is complete
			if totalLength / measureLength > numOfMeasures:
				numOfMeasures += 1
				#Draw measure bar if measure is done
				self.drawMeasureBar(xCoord,currentNotes)
				xCoord += noteSpacing
			#Once 14 notes go on a line, it resets xCoord to next line
			if note % 14 == 0: xCoord = startX
			#Adjust yCoord based on the yIndex of the note
			halfStepHeight = 8
			yCoord = (200*((note/14)+1)+44) + (yIndex*halfStepHeight)
			if noteType == 0:
				self.drawNormalNote(length,pitch,xCoord,yCoord,surface)
			elif noteType == 1:
				self.drawRest(length,pitch,xCoord,yCoord,surface)
		#Draw notes surface onto window
		self.window.blit(surface,(0,0))

	#Draw a single note
	def drawNormalNote(self,length,pitch,xCoord,yCoord,surface):
		#Retrieve filename based on type of note
		filename = str(length) + str(pitch) + ".jpg"
		noteImage = pygame.image.load(filename)
		#Add 66 pixel offset to adjust photo correctly
		yCoord -= 66
		#Draw note image onto surface
		surface.blit(noteImage,(xCoord,yCoord))

	#Draw a single rest
	def drawRest(self,length,pitch,xCoord,yCoord,surface):
		#Retrieve filename based on type of rest
		filename = str(length) + "rest.jpg"
		#Place rest image right starting at staffMargin at top
		staffRegionHeight = 200
		thisStaff = yCoord / staffRegionHeight
		staffMargin = 64
		yCoord = (thisStaff * 200) + staffMargin
		#Load the image
		restImage = pygame.image.load(filename)
		#Load image onto surface
		surface.blit(restImage,(xCoord,yCoord))

	#Draw a single measure bar
	def drawMeasureBar(self,xCoord,currentNotes):
		#Determine number of staffs
		numOfStaffs = (len(currentNotes) / 14) + 1
		#Subtract 1 from this number if a line staff is full
		if (float(len(currentNotes)) / 14) + 1 == numOfStaffs:
			numOfStaffs -= 1
		#Draw line from top to bottom of this line of staff
		staffRegionHeight = 200
		staffMargin = 68
		y0 = (numOfStaffs * 200) + staffMargin
		staffheight = 64
		y1 = y0 + staffheight
		color = (0,0,0)
		#Add line offset to make line fit more evenly with notes
		lineOffset = 20
		xCoord += lineOffset
		if xCoord > 900:
			return
		#Draw the line after defining location
		start, end = (xCoord,y0), (xCoord,y1)
		pygame.draw.line(self.window,color,start,end)

	#Determine total length of all notes in a list
	def determineTotalLength(self,notes):
		totalLength = 0
		#Iterate through all notes, sum up length from lengthIndex
		for note in notes:
			lengthIndex = note[1]
			length = self.noteLengthValues[lengthIndex]
			totalLength += length
		return totalLength

	#Draw music staffs on window
	def drawStaffs(self):
		#Determine num of staffs based on num of notes
		numOfStaffs = (len(self.notes) / 14) + 1
		#Start first staff 1/4 from top of screen
		startX, startY = 0, 200
		#Iterate through to draw every single staff individually
		for staff in xrange(numOfStaffs):
			x0 = startX
			y0 = startY + (staff * startY)
			x1 = self.width
			y1 = y0 + startY
			self.drawSingleStaff(x0,y0,x1,y1)

	#Draw background for whole window
	def drawBackground(self):
		#Keep simple white background
		backgroundColor = (255,255,255)
		self.window.fill(backgroundColor)

	#Draw title and composer at top of window
	def drawTitleAndComposer(self):
		#Draw title on window
		fontSize = 80
		font = pygame.font.Font(None,fontSize)
		#If no title is inputted, make it carpe diem
		if len(self.title) == 0:
			self.title = "Carpe Diem!"
		#Render title and place it on window
		title = font.render(self.title,1,self.textColor)
		titlePosition = title.get_rect()
		titlePosition.centerx = self.width / 2
		titlePosition.centery = self.height / 16
		self.window.blit(title,titlePosition)

		#Draw composer on window
		fontSize = 50
		font = pygame.font.Font(None,fontSize)
		#If no composer inputted, make it Professor
		if len(self.composer) == 0:
			self.composer = "David Kosbie"
		text = "by " + self.composer
		#Render composer and place it on window
		composer = font.render(text,1,self.textColor)
		composerPosition = composer.get_rect()
		composerPosition.centerx = self.width / 2
		composerPosition.centery = 3 * self.height / 16
		self.window.blit(composer,composerPosition)

	#Draw a single music staff with given coords
	def drawSingleStaff(self,x0,y0,x1,y1):
		#Create new surface for staff
		surface = pygame.Surface((x1-x0,y1-y0))
		#Set colorkey and fill so that white is transparent
		surface.set_colorkey((255,255,255))
		surface.fill((255,255,255))
		#4 rectangles to draw per staff
		numOfBoxes = 4
		startX, startY = 50, 68
		boxWidth, boxHeight = 900, self.wholeStepHeight
		#Iterate through 4 boxes and draw each rectangle
		for box in xrange(numOfBoxes):
			xCoord = startX
			yCoord = startY + (box * boxHeight)
			fill = (0,0,0)
			outlineWidth = 1
			rect = (xCoord,yCoord,boxWidth,boxHeight)
			pygame.draw.rect(surface,fill,rect,outlineWidth)
		#Draw treble clef and time on a second suurface
		secondSurface = pygame.Surface((x1-x0,y1-y0))
		secondSurface.fill((255,255,255))
		self.drawTrebleClefAndTimeSignature(secondSurface,startX,startY)
		#first put second surface on window and then staff surface
		self.window.blit(secondSurface,(x0,y0))
		self.window.blit(surface,(x0,y0))

	#Draw treble clef and time signature
	def drawTrebleClefAndTimeSignature(self,surface,startX,startY):
		#Input treble clef image at location
		trebleLocation = (startX,startY)
		surface.blit(self.trebleClef,trebleLocation)
		#Input time signature image 40 pixels to the right
		startX += 40
		timeLocation = (startX,startY)
		#Retrieve filename from current selected time
		filename = str(self.selectedTime) + "time.jpg"
		timeSig = pygame.image.load(filename)
		surface.blit(timeSig,timeLocation)

	#Draw options for music staff window
	def drawOptions(self):
		#Draw 2 brownish rectangles, each on a top corner of window
		boxColor =(233,204,151)
		rect = (0,0,300,200)
		outlineWidth = 0
		pygame.draw.rect(self.window,boxColor,rect,outlineWidth)
		rect = (700,0,300,200)
		outlineWidth = 0
		pygame.draw.rect(self.window,boxColor,rect,outlineWidth)
		#Draw all options
		self.drawNoteTypeOptions()
		self.drawNoteLengthOptions()
		self.drawNotePitchOptions()
		self.drawPlaybackOptions()
		self.drawSaveButton()

	#Draw options for note types
	def drawNoteTypeOptions(self):
		#Orient note type position on top left of window
		self.startX = 25
		self.startY = 10
		self.boxWidth = 250
		self.boxHeight = 80
		color = (255,255,255)
		#Draw rectangle for note types
		rect = (self.startX,self.startY,self.boxWidth,self.boxHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		header = "Note Types:"
		#Draw text header for note types
		self.drawHeader(header)
		#Draw note type buttons
		self.drawNoteTypeButtons()

	#Draw buttons for note types
	def drawNoteTypeButtons(self):
		#Store note type buttons to be used for mousepresses
		self.noteTypeButtons = []
		#Define region of space that button has
		buttonRegion = float(self.boxWidth) / len(self.noteTypes)
		#each button can be drawn halfway through the buttonRegion
		startXCoord, buttonWidth, buttonHeight = buttonRegion / 2, 40, 30
		#Iterate through all notetypes, draw each respective button
		for note in xrange(len(self.noteTypes)):
			xCoord = self.startX + (startXCoord + note * buttonRegion)
			yCoord = self.startY + 0.7 * self.boxHeight
			rectX = xCoord - buttonWidth / 2
			rectY = yCoord - buttonHeight / 2
			rect = (rectX,rectY,buttonWidth,buttonHeight)
			if note == self.selectedType:
				color = (255,255,255)
			else:
				color = (233,204,151)
			outlineWidth = 0
			#Draw respective button and black outline
			pygame.draw.rect(self.window,color,rect,outlineWidth)
			pygame.draw.rect(self.window,(0,0,0),rect,1)
			#Store each button in the buttonslist
			button = pygame.Rect(rectX,rectY,buttonWidth,buttonHeight)
			self.noteTypeButtons.append(button)
			#Draw button labels
			label = self.noteTypes[note]
			fontSize = 20
			self.drawText(xCoord,yCoord,label,fontSize)
			
	#Draw options for note lengths
	def drawNoteLengthOptions(self):
		#Orient note length position under note type positions
		self.startX = 25
		self.startY = 110
		self.boxWidth = 250
		self.boxHeight = 80
		color = (255,255,255)
		#Draw rectangle for note types
		rect = (self.startX,self.startY,self.boxWidth,self.boxHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		header = "Note Lengths:"
		#Draw text header for note types
		self.drawHeader(header)
		#Draw note type buttons
		self.drawNoteLengthButtons()

	#Draw buttons for these note lengths
	def drawNoteLengthButtons(self):
		#Store note length buttons to be used for mousepress
		self.noteLengthButtons = []
		#Define region of space that each button has
		buttonRegion = float(self.boxWidth) / len(self.noteLengths)
		#Each button is drawn halfway through buttionRegion
		startXCoord, buttonWidth, buttonHeight = buttonRegion / 2, 40, 30
		#Iterate through each noteLength, draw each respective button
		for note in xrange(len(self.noteLengths)):
			xCoord = self.startX + (startXCoord + note * buttonRegion)
			yCoord = self.startY + 0.7 * self.boxHeight
			rectX = xCoord - buttonWidth / 2
			rectY = yCoord - buttonHeight / 2
			rect = (rectX,rectY,buttonWidth,buttonHeight)
			#make color of selected length button white
			if note == self.selectedLength:
				color = (255,255,255)
			else:
				color = (233,204,151)
			outlineWidth = 0
			#Draw respective note length button
			pygame.draw.rect(self.window,color,rect,outlineWidth)
			pygame.draw.rect(self.window,(0,0,0),rect,1)
			#Store note length Rect for mousepress
			button = pygame.Rect(rectX,rectY,buttonWidth,buttonHeight)
			self.noteLengthButtons.append(button)
			#Draw button text on window
			label = self.noteLengths[note]
			fontSize = 20
			self.drawText(xCoord,yCoord,label,fontSize)

	#Draw options for note pitches
	def drawNotePitchOptions(self):
		#Orient note pitch position on top right of window
		self.startX = 725
		self.startY = 10
		self.boxWidth = 250
		self.boxHeight = 80
		color = (255,255,255)
		#Draw rectangle fro note pitches
		rect = (self.startX,self.startY,self.boxWidth,self.boxHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		header = "Note Pitch:"
		#Draw text header for note types
		self.drawHeader(header)
		#Draw note pitch buttons
		self.drawNotePitchButtons()

	#Draw buttons for these note pitches
	def drawNotePitchButtons(self):
		#Store note pitch buttons to be used for mousepress
		self.notePitchButtons = []
		#Define region of space that each button has
		buttonRegion = float(self.boxWidth) / len(self.pitchTypes)
		#Each button is drawin halfway through buttonRegion
		startXCoord,buttonWidth,buttonHeight = buttonRegion / 2, 50, 30
		#Iterate through each notePitch, draw each respective button
		for note in xrange(len(self.pitchTypes)):
			xCoord = self.startX + (startXCoord + note * buttonRegion)
			yCoord = self.startY + 0.7 * self.boxHeight
			rectX = xCoord - buttonWidth / 2
			rectY = yCoord - buttonHeight / 2
			rect = (rectX,rectY,buttonWidth,buttonHeight)
			#Make color of selected button white
			if note == self.selectedPitch:
				color = (255,255,255)
			else:
				color = (233,204,151)
			outlineWidth = 0
			#Draw respective note pitch button
			pygame.draw.rect(self.window,color,rect,outlineWidth)
			pygame.draw.rect(self.window,(0,0,0),rect,1)
			#Store note pitch Rect for mousePress
			button = pygame.Rect(rectX,rectY,buttonWidth,buttonHeight)
			self.notePitchButtons.append(button)
			#Draw button text on window
			label = self.pitchTypes[note]
			fontSize = 20
			self.drawText(xCoord,yCoord,label,fontSize)

	#Draw play button for audio playback
	def drawPlaybackOptions(self):
		#Orient playback button underneath note pitch buttons
		buttonX, buttonY = 745, 120
		buttonWidth = 80
		buttonHeight = 60
		#Make button white
		color = (255,255,255)
		#Draw button rectangle with black outline
		rect = (buttonX,buttonY,buttonWidth,buttonHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store playButton for user mousepresses
		self.playButton = pygame.Rect(buttonX,buttonY,buttonWidth,buttonHeight)
		#Draw button text
		textX = buttonX + buttonWidth / 2
		textY = buttonY + buttonHeight / 2
		label = "Play"
		fontSize = 30
		self.drawText(textX,textY,label,fontSize)

	#Draw save button for saving wave files
	def drawSaveButton(self):
		#Orient save button to right of playback button
		buttonX,buttonY = 895, 120
		buttonWidth = 80
		buttonHeight = 60
		#Make button white
		color = (255,255,255)
		#Draw button and its black border
		rect = (buttonX,buttonY,buttonWidth,buttonHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store saveButton for user mousepresses
		self.saveButton = pygame.Rect(buttonX,buttonY,buttonWidth,buttonHeight)
		#Draw save button label
		textX = buttonX + buttonWidth / 2
		textY = buttonY + buttonHeight / 2
		label = "Save"
		fontSize = 30
		self.drawText(textX,textY,label,fontSize)

	#Draw quite button for returning to start screen
	def drawQuitButton(self):
		#Orient quit button on bottom left of window
		startX = 20
		buttonWidth = 60
		endY = self.height - 15
		buttonHeight = 40
		startY = endY - buttonHeight
		#Make button brownish gold
		color = (213,165,33)
		#Draw button and its black border
		rect = (startX,startY,buttonWidth,buttonHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,color,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store quitButton for user mousePress
		self.quitButton = pygame.Rect(startX,startY,buttonWidth,buttonHeight)
		#Draw quitButton label
		textX = startX + (buttonWidth / 2)
		textY = startY + (buttonHeight / 2)
		text = "Quit"
		fontSize = 30
		self.drawText(textX,textY,text,fontSize)
	
	#Drawing helper function to draw centered text
	def drawText(self,textX,textY,header,fontSize):
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		#Redefine rendered text cx and cy before drawing
		textPosition = text.get_rect()
		textPosition.centerx = textX
		textPosition.centery = textY
		self.window.blit(text,textPosition)

	#Drawing helper function to draw header for options boxes
	def drawHeader(self,header):
		#Orient header at top of box
		textX = self.startX + (self.boxWidth / 2)
		textY = self.startY + (self.boxHeight / 6)
		#Draw header text
		fontSize = 25
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		#Redefine rendered text cx and cy before drawing
		textPosition = text.get_rect()
		textPosition.centerx = textX
		textPosition.centery = textY
		self.window.blit(text,textPosition)

#Class to playback audio and save wave files
class PlayStandardNotes(object):
	#Initialize class, store notes
	def __init__(self,notes):
		self.notes = notes
		self.noteLengths = [1,0.5,0.25,0.125,0.0625]

	#Generate tone from notes and play it back to user
	def generateTone(self):
		#Convert notes to frequencies
		frequencies = self.convertToFrequency()
		#Convert frequencies to waveData
		waveData = self.generateSoundData(frequencies)
		#Stream the sound to user
		self.streamSound(waveData)

	#Convert the self.notes to frequency
	def convertToFrequency(self):
		#Iterate through all notes, convert each note individually
		frequencies = []
		for note in self.notes:
			frequency = self.noteToFrequency(note)
			frequencies.append(frequency)
		return frequencies

	#Manually retrieve frequency based on note and note pitch
	def noteToFrequency(self,note):
		frequencies = [[1975.53,2093.00,1864.66],	#B5
						[1760.00,1864.66,1661.22],	#A5
						[1567.98,1661.22,1479.98],	#G5
						[1396.91,1479.98,1318.51],	#F5
						[1318.51,1396.91,1244.51],	#E5
						[1174.66,1244.51,1108.73],	#D5
						[1046.50,1108.73,987.77],	#C5
						[987.77,1046.50,932.22],	#B4
						[880.00,932.33,830.61],		#A4
						[783.99,830.61,739.99],		#G4
						[698.46,739.99,659.25],		#F4
						[659.25,698.46,622.25],		#E4
						[587.33,622.25,554.37],		#D4
						[523.25,554.37,493.88]]		#C4

		frequency = frequencies[note[0]]
		#Index in sublist is based on note pitch (note[2])
		pitch = frequency[note[2]]
		return pitch

	#Generate sound wavedata from frequencies
	#Got some help to do this from online
	#http://askubuntu.com/questions/202355/
	#how-to-play-a-fixed-frequency-sound-using-python
	def generateSoundData(self,frequencies):
		bitRate = 16000
		waveData = ""
		#Iterate through all frequencies
		for frequency in xrange(len(frequencies)):
			#Retrieve each note's length.
			index = self.notes[frequency][1]
			noteType = self.notes[frequency][3]
			# Correspond length to length of tone
			length = (2 * self.noteLengths[index])
			numberOfFrames = int(bitRate * length)
			restFrames = numberOfFrames % bitRate
			#Make frequency practically zero if it's a rest
			if noteType == 0:
				frequency = frequencies[frequency]
			else:
				frequency = 1
			for x in xrange(numberOfFrames):
				#This equation was copied verbatim 
				#to convert frequency to waveData
				waveData += chr(int(math.sin(x/
						((bitRate/frequency)/math.pi))*127+128))

		return waveData

	#Save sound data to a wave file
	#Learned about saving waves on python documentation
	#https://docs.python.org/2/library/wave.html
	def saveWaveFile(self,filename):
		#Retrieve waveData from self.notes
		frequencies = self.convertToFrequency()
		waveData = self.generateSoundData(frequencies)
		#Add .wav to filename to make it valid for computer
		filename += ".wav"
		#Open wave file in write mode
		waveFile = wave.open(filename,mode = "wb")
		channels = 1
		sampWidth = 1
		frameRate = 16000
		nframes = 0
		compType = "NONE"
		compname = ""
		#Set initial parameters before writing
		waveFile.setparams((channels,sampWidth,frameRate,nframes,
							compType,compname))
		#Write waveData to wave file
		waveFile.writeframes(waveData)
		waveFile.close()

	#Playback the sound data to the user
	#I did this myself but I got some help with the formatting of
	#of py.open
	#http://askubuntu.com/questions/202355/how-to-play-a-fixed-
	#frequency-sound-using-python 
	def streamSound(self,waveData):
		bitRate = 16000
		#Initialize pyaudio
		PyAudio = pyaudio.PyAudio
		py = PyAudio()
		#Initialize stream
		stream = py.open(format = py.get_format_from_width(1),
						channels = 1,
						rate = bitRate,
						output = True)
		#Write the waveData to the stream
		stream.write(waveData)
		#Stop the stream once it's done. Then end pyaudio
		stream.stop_stream()
		stream.close()
		py.terminate()

#Class for the save song screen
class SaveSongScreen(object):
	#Initialize class, define window dimensions and other values
	def __init__(self,window,selectedTime,
				selectedType,selectedLength,selectedPitch,
				notes,title,composer,filename):
		self.window = window
		self.selectedTime = selectedTime
		self.selectedType = selectedType
		self.selectedLength = selectedLength
		self.selectedPitch = selectedPitch
		self.notes = notes 
		self.title = title
		self.composer = composer
		(self.width,self.height) = self.window.get_size()
		self.filename = filename

	#Define initial values for save song screen
	def initAnimation(self):
		self.textColor = (0,0,0)

	#Redraw everything for save song screen
	def redrawAll(self):
		#Define initial vars
		self.initAnimation()
		#Draw music staff first and then draw save box over it
		StandardStaffDrawings(self.window,
							self.selectedTime,
							self.selectedType,
							self.selectedLength,
							self.selectedPitch,
							self.notes,
							self.title,
							self.composer).redrawAll()
		#Draw save box and then update pygame window
		self.drawSaveBox()
		pygame.display.flip()
		#Return buttons for user mousepresses
		return (self.filenameBox,self.saveButton)

	#Draw save box drawn over music staff
	def drawSaveBox(self):
		#Center box in middle of window with 200 side margin
		self.startX, self.startY = 200, 200
		self.boxWidth = 600
		self.boxHeight = 400
		#Draw saveBox with black border
		background = (213,165,33)
		rect = (self.startX,self.startY,self.boxWidth,self.boxHeight)
		outlineWidth = 0
		pygame.draw.rect(self.window,background,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Draw other parts of save box
		self.drawSaveBoxHeader()
		self.drawFilenameInput()
		self.drawSaveButton()

	#Draw header for saveBox
	def drawSaveBoxHeader(self):
		#Center header at top of saveBox
		header = "Save File"
		textX = self.startX + (self.boxWidth / 2)
		textY = self.startY + (self.boxHeight / 4)
		fontSize = 50
		self.drawText(textX,textY,header,fontSize)

	#Drawing text helper function to draw centered text
	def drawText(self,textX,textY,header,fontSize):
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		textPosition = text.get_rect()
		#Redefine centerx and centery for rendered font
		textPosition.centerx = textX
		textPosition.centery = textY
		self.window.blit(text,textPosition)

	#Draw label and box for user to input filename to save audio
	def drawFilenameInput(self):
		#Center filename in middle of window
		textX = self.startX + 35
		textY = self.startY + (2 * self.boxHeight / 4)
		#Draw filename text
		header = "Filename: "
		fontSize = 30
		font = pygame.font.Font(None,fontSize)
		text = font.render(header,1,self.textColor)
		#Redefine centerx and centery of rendered font
		textPosition = text.get_rect()
		textPosition.centerx = textX + 25
		textPosition.centery = textY 
		self.window.blit(text,textPosition)
		#Draw white text box for filename
		self.drawFilenameBox(textY)

	#Draw box for filename
	def drawFilenameBox(self,textY):
		#Orient box just a little bit right of filename label in window
		startX = self.startX + 120
		startY = textY - 30
		endX = self.width - self.startX - 10
		endY = textY + 30
		boxWidth = endX - startX
		boxHeight = endY - startY
		#Draw white rectangle with black border
		rect = (startX,startY,boxWidth,boxHeight)
		fill = (255,255,255)
		outlineWidth = 0
		pygame.draw.rect(self.window,fill,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store filenameBox as a button for mousePress
		self.filenameBox = pygame.Rect(startX,startY,boxWidth,boxHeight)
		#Draw text inside of filenameBox
		textX = startX + 10
		textY -= 10
		words = self.filename
		fontSize = 30
		font = pygame.font.Font(None,fontSize)
		text = font.render(words,1,self.textColor)
		self.window.blit(text,(textX,textY))

	#Draw save button for save song screen
	def drawSaveButton(self):
		#Orient save button at bottom of saveBox
		endX = self.startX + self.boxWidth - 10
		startX = endX - 80
		startY = self.startY + (3 * self.boxHeight / 4)
		buttonWidth, buttonHeight = 80,60
		#Draw white box with black border for button
		rect = (startX,startY,buttonWidth,buttonHeight)
		fill = (255,255,255)
		outlineWidth = 0
		pygame.draw.rect(self.window,fill,rect,outlineWidth)
		pygame.draw.rect(self.window,(0,0,0),rect,1)
		#Store save button for mousepress
		self.saveButton = pygame.Rect(startX,startY,buttonWidth,buttonHeight)
		words = "Save"
		#Draw text inside of buton
		fontSize = 35
		font = pygame.font.Font(None,fontSize)
		text = font.render(words,1,self.textColor)
		self.window.blit(text,(startX + 12,startY + 15))

def runSuperEditor():
	width = 1000
	height = 800
	SuperEditor(1000,800).run()

runSuperEditor()