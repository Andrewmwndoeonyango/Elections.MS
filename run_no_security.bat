@echo off
cls
echo ========================================
echo    KENYA ELECTORAL SYSTEM - NO SECURITY
echo ========================================
echo.
echo Server Status: RUNNING
echo Protocol: HTTP (No SSL/HTTPS)
echo Security: DISABLED
echo CSRF Protection: REMOVED
echo Session Security: DISABLED
echo All Restrictions: REMOVED
echo.
echo Admin Credentials:
echo   Username: superadmin
echo   Password: superadmin123
echo.
echo Voter Credentials:
echo   Username: testuser
echo   Password: testpass123
echo.
echo Opening Kenya Electoral System...
echo.
start http://127.0.0.1:8000/
echo.
echo ========================================
echo SYSTEM ACCESS URLs:
echo ========================================
echo.
echo Main Site:       http://127.0.0.1:8000/
echo Voter Login:     http://127.0.0.1:8000/login/
echo Admin Panel:     http://127.0.0.1:8000/admin/
echo Voter Dashboard: http://127.0.0.1:8000/dashboard/
echo.
echo ========================================
echo NO SECURITY RESTRICTIONS - FREE ACCESS
echo ========================================
echo.
pause
