@echo off
echo Starting Litflix Application...
echo.

echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python main.py"
cd ..

echo.
echo Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo Both servers are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:5173
echo.
echo Press any key to exit this window...
pause > nul 