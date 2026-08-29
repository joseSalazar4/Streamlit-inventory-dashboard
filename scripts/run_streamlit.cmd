@echo off
setlocal
set "REPO_ROOT=%~dp0.."

if defined CAS_PYTHON_EXE if exist "%CAS_PYTHON_EXE%" (
  "%CAS_PYTHON_EXE%" "%REPO_ROOT%\scripts\run_streamlit.py" %*
  exit /b %errorlevel%
)

where py.exe >nul 2>&1
if not errorlevel 1 (
  py -3 "%REPO_ROOT%\scripts\run_streamlit.py" %*
  exit /b %errorlevel%
)

where python.exe >nul 2>&1
if not errorlevel 1 (
  python "%REPO_ROOT%\scripts\run_streamlit.py" %*
  exit /b %errorlevel%
)

set "PYTHON_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%PYTHON_EXE%" (
  "%PYTHON_EXE%" "%REPO_ROOT%\scripts\run_streamlit.py" %*
  exit /b %errorlevel%
)

echo Python 3.10 or newer was not found. Install Python or set CAS_PYTHON_EXE.
exit /b 1
