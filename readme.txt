My project is, in short, an experience that combines both a
simpler approach to music editing and a fun new interface
for percussion instrumentation. There are two major parts to my
project. One part is a music editor which allows for professional
level music composition with a simple user interface. This music
editor also allows users to playback their music with artificially
generated audio and to also save this audio as a wave file for 
personal keeping. The second part to my project is a free play mode
in which, provided two colored sticks, the user can play drums 
"in the air" and using advanced image and video processing the 
computer and its webcam will track the sticks and play 
certain drum sounds accordingly based on the sticks' location in
relation to predetermined drum regions.

There were several modules that I used to make this project happen.
The most evident of these modules is Pygame, a third party library
for python dedicated to easy game development. While I didn't use 
this module for gaming purposes, I used it to form my entire user
interface. All of the graphics shown in my program, including buttons,
text input, and images, were displayed with Pygame. Pygame is the tool
I used in the hopes to establish a simple UI. I also used Pygame to 
playback audio files when it was necessary to generate a sound in the 
air drums mode when a user hits a drum. Pygame allowed for access and
playback of pre-saved audio files. 
To get Pygame, you must go to the Pygame website and click on downloads on the left
hand side of the window. There you will be given a list of pygame releases
where you must click to download and install the exe file coresponding to 
your operating system. The link to this download page is here:

http://www.pygame.org/download.shtml

I also utilized a module called PyAudio which is a python-unique
library dedicated to sound output. While most use PyAudio for simple
music input in a user interface, I used PyAudio's capabilities, including
the ability to set certain sound parameters such as bandwidth and bitrate,
to generate waveData based on the user's notes in the music staff. I also
use PyAudio to playback this wave data in the form of synthetic music for
the user to listen to their composition. To download PyAudio, you must go to
the PyAudio website and click on downloads at the top of the screen.
This downloads page lists the corresponding exe files for each operating 
system and version of python to download PyAudio. Run the exe files to 
install the library. For my project I downloadedthe Microsoft Windows version 
for Python 2.7. This is the link to that download page:

http://people.csail.mit.edu/hubert/pyaudio/#downloads

For camera tracking for the air drums, I used two modules: openCV2 and
numpy. openCV2 is a library available for several languages which is
dedicated to image and video processing. Its built-in functions allowed me 
to track the specific colors of my user's drumsticks in order to play the
air drums. Along with openCV2 is numpy which is a Python-unique package
dedicated to more advanced scientific computation than other math modules
such as Python's built-in math module. I needed numpy only because openCV2
exploits numpy specifically for its powerful computations, specifically its
N-dimensional array objects for images. To download openCV2, you must go to
the openCV homepage, click on downloads at the top of the window, and 
download openCV version 2.4.10 for your respective operating system. Here you 
will download an exe that will install the openCV library for you. Here 
is the link to the downloads page:

http://opencv.org/downloads.html

To download numpy, you must go to the numpy downloads page which will take you
to a sourceforge link with all the versions. Click on the latest version and 
download the exe file for your OS which will install the numpy library for you.
Here's the link to the latest version downloads:

http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/

I used some other python modules that are built into the language. I utilized
the sys module for the one reason to close the application if the user closes
window. I utilized the wave module which is what made possible my saving of
audio music files. While PyAudio generates the waveData, the wave module
writes this data to a blank wave file with a filename of your choice. Finally, I
used python's built in math module for some simple sine calculations.

Once all of the modules are downloaded and installed, then Python will
be able to import these modules and the application will run smoothly.