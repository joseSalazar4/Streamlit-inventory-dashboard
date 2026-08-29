@echo off
setlocal
set "COLLABORATOR_ROOT=%~dp0.local\cas-document-platform\cas-collaborator-platform"

if not exist "%COLLABORATOR_ROOT%\scripts\run_streamlit.cmd" (
  echo Collaborator repository not found at "%COLLABORATOR_ROOT%".
  exit /b 1
)

call "%COLLABORATOR_ROOT%\scripts\run_streamlit.cmd" --prepare-only
if errorlevel 1 exit /b %errorlevel%

where docker.exe >nul 2>&1
if errorlevel 1 (
  echo Docker Desktop was not found. Install or start Docker Desktop and try again.
  exit /b 1
)

docker compose -f "%~dp0compose.yaml" up --build %*
