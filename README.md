# Gomoku
This project implements a Gomoku AI ("brain") for the Piskvork
manager, compatible with the Gomocup
tournament rules.
The AI is written in Python and compiled into a Windows .exe executable using PyInstaller.


To test out the bot, you can simply download the Piskvork manager and then download the zip file of this project. 

## Here is the simple tldr;
1. Download and install Piskvork manager:
2. https://gomocup.org/download-gomocup-manager/
3. Start Piskvork, go to Settings → Players, and add our bot pbrain-mybrain.exe file in  C:\Users\UserName\gomoku\pbrain.

## Alternate (compile yourself)
1. In windows command line (windowsbutton + r then type cmd and enter)
2. cd C:\Users\UserName\gomoku\pbrain OR wherever you cloned/downloaded the project
3. copy paste this into the commandline: 
 pyinstaller.exe myBrain.py pisqpipe.py --name pbrain-mybrain.exe --onefile


## Known Limitations
Advanced heuristics (e.g., open three, open four detection) are not yet implemented.