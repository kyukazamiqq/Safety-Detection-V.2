@echo off
echo Installing YOLO Safety Detection Dashboard dependencies...
echo.

echo Installing Python packages...
pip install -r requirements.txt

echo.
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "results" mkdir results

echo.
echo Installation completed!
echo.
echo To run the dashboard:
echo python app.py
echo.
echo Then open your browser and go to: http://localhost:5000
echo.
pause
