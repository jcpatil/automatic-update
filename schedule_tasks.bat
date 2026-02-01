@echo off
:: Batch Script to Schedule Naukri Updater
:: Runs daily at 09:20 AM and 02:30 PM

set TASK_NAME_MORNING="NaukriUpdater_Morning"
set TASK_NAME_AFTERNOON="NaukriUpdater_Afternoon"
:: Use wpython if available to hide console, otherwise python
set SCRIPT_PATH="C:\Users\shree\Desktop\naukri_updater\naukri_updater.py"
set WORK_DIR="C:\Users\shree\Desktop\naukri_updater"

echo Creating Morning Task (09:20 AM)...
:: /RL HIGHEST ensures it runs with permissions if needed
:: /KV ensures it runs in the user session so it can access the browser profile
schtasks /create /tn %TASK_NAME_MORNING% /tr "cmd /c cd /d %WORK_DIR% && python naukri_updater.py" /sc daily /st 09:20 /f

echo Creating Afternoon Task (02:30 PM)...
schtasks /create /tn %TASK_NAME_AFTERNOON% /tr "cmd /c cd /d %WORK_DIR% && python naukri_updater.py" /sc daily /st 14:30 /f

echo.
echo ---------------------------------------------------
echo Tasks scheduled successfully!
echo.
echo IMPORTANT: 
echo These tasks are set to run ONLY when you are logged in.
echo If you want them to run even when your screen is locked,
echo you may need to edit them in Task Scheduler to "Run whether user is logged on or not"
echo (though that might affect the browser opening).
echo.
echo To view them, open 'Task Scheduler' and look for:
echo - %TASK_NAME_MORNING%
echo - %TASK_NAME_AFTERNOON%
echo ---------------------------------------------------
pause
