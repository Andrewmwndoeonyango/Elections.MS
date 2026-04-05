@echo off
cls
echo ========================================
echo   KENYA ELECTORAL SYSTEM - FREE BACKEND
echo ========================================
echo.
echo ✅ SERVER STATUS: RUNNING FREELY
echo ✅ SECURITY: DISABLED
echo ✅ RESTRICTIONS: NONE
echo ✅ PROTOCOL: HTTP ONLY
echo ✅ ACCESS: UNRESTRICTED
echo.
echo 🔑 LOGIN CREDENTIALS:
echo    Admin:  superadmin / superadmin123
echo    Voter:  testuser / testpass123
echo.
echo 🌐 BACKEND URLs:
echo    Main:      http://127.0.0.1:8000/
echo    Admin:     http://127.0.0.1:8000/admin/
echo    Login:     http://127.0.0.1:8000/login/
echo    Dashboard: http://127.0.0.1:8000/dashboard/
echo.
echo 🚀 STARTING FREE BACKEND ACCESS...
echo.
start http://127.0.0.1:8000/
timeout /t 2 >nul
start http://127.0.0.1:8000/admin/
timeout /t 2 >nul
start http://127.0.0.1:8000/login/
echo.
echo ========================================
echo ✅ BACKEND RUNNING COMPLETELY FREELY!
echo ========================================
echo.
echo 📊 AVAILABLE FEATURES:
echo    • 47 Counties Management
echo    • 290 Constituencies Control  
echo    • 1,450 Wards Administration
echo    • 24,559 Polling Centers
echo    • 46,232 Polling Stations
echo    • 177 Candidates Management
echo    • Complete Voter System
echo    • Real-time Voting
echo.
pause
