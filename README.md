# Gomoku
This project implements a Gomoku AI ("brain") for the Piskvork
manager, compatible with the Gomocup
tournament rules.
The AI is written in Python and compiled into a Windows .exe executable using PyInstaller.

## Here are the instructions for the user

To test out the bot, you can simply download the Piskvork manager and then download the zip file of this project. The exe file is already in \gomoku\pbrain


## Here is the simple tldr;
1. Download and install Piskvork manager:
2. https://gomocup.org/download-gomocup-manager/
3. Start Piskvork, go to Settings → Players, and add our bot pbrain-mybrain.exe file in  C:\Users\UserName\gomoku\pbrain. or wherever you put the project folder.

## Testing
1. poetry install
2. poetry run pytest --cov=pbrain --cov-report=term-missing

## Alternate (compile yourself)
1. In windows command line (windowsbutton + r then type cmd and enter)
2. cd C:\Users\UserName\gomoku\pbrain OR wherever you cloned/downloaded the project
3. copy paste this into the commandline: 
    pyinstaller.exe myBrain.py pisqpipe.py --name pbrain-mybrain.exe --onefile
