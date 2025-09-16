@echo off
echo Starting Weekly Invoice Follow-Up Report...
cd /d "%~dp0"
python weekly_report_script.py
pause

