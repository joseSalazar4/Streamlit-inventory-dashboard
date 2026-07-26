@echo off
setlocal
set "REPO_ROOT=%~dp0.."
set "PYTHON_EXE=C:\Users\jsala\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not exist "%PYTHON_EXE%" (
  echo Bundled Python was not found at "%PYTHON_EXE%"
  exit /b 1
)

"%PYTHON_EXE%" "%REPO_ROOT%\scripts\run_streamlit.py" %*
