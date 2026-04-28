@echo off
REM Fix MySQLdb Error - Install MySQL Driver

cd /d C:\Users\shaimae\Desktop\e_commerce

echo Installing MySQLdb (mysqlclient)...
.venv\Scripts\pip install mysqlclient

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Successfully installed mysqlclient
    echo.
    echo Now you can run: python manage.py runserver
    echo.
) else (
    echo.
    echo ✗ Installation failed. Trying alternative PyMySQL...
    .venv\Scripts\pip install PyMySQL
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✓ Successfully installed PyMySQL
        echo Update your settings.py to use PyMySQL instead:
        echo.
        echo import pymysql
        echo pymysql.install_as_MySQLdb(^)
        echo.
    )
)

pause
