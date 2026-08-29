@echo off
call "%~dp0scripts\run_streamlit.cmd" %*
exit /b %errorlevel%
