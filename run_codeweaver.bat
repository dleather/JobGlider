@echo off
setlocal

REM Set paths
set ROOT_DIR=%~dp0
set OUTPUT_DIR=%ROOT_DIR%codeweaver

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Process the entire codebase with simplified ignore patterns
echo Processing codebase...
codeweaver -output "%OUTPUT_DIR%\codebase.md" ^
    -ignore "\.env,coverletters,outputs,references,\.git,codeweaver,\.bat,\.venv,\.venv-3.12,\.venv-3.13"

echo Analysis complete. Check the codeweaver directory for results.
pause