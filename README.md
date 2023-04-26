# Measurements
This repository contains code for running measurements in the OSU NSL PPMS. 
Edited by Justin Michel (michel.169@osu.edu)

# Installation
1. Make sure you have Python 3.7 installed. Later Python versions do not work with the pythonnet version we need to interface with the PPMS. You can check the Python version you have in the command line with:
```
python --version
```
If you have multiple versions of Python installed, you may need to do, for example:
```
python37 --version
```
For further steps in the installation, always make sure to use Python 3.7.

2. Install git:
https://git-scm.com/download/win

3. Clone this repository to some local folder with:
```
git clone https://github.com/justinm678/Measurements
```

4. Optionally, you can use a virtual environment to download the packages required here. 
In the project directory, do 
```
python37 -m venv venv
```
Then activate it with:
```
venv\Scripts\activate
```
The prompt line should now show a ` (venv) ` at the beginning.
You can then download the packages required with
```
python37 -m pip install requirements.txt
```