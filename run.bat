@echo off

REM Create a new virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies from requirements.txt file
pip install -r requirements.txt

REM Run the python script
python dataprep.py