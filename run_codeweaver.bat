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
    -ignore "\.env,coverletters,outputs,references,\.git,codeweaver,\.bat,\.venv,\.venv-3.12,\.venv-3.13,uv\.lock,templates\\latex,requirements.lock, README\.md, tests\\__pycache__,tests\\integration\\__pycache__,tests\\unit\\__pycache__, src\\__pycache__,src\\core\\__pycache__,src\\utils\\__pycache__,\.pytest_cache,\.github,\.github\workflows,\.coverage,src\\server\\__pycache__,src\\api\\__pycache__"

echo Analysis complete. Check the codeweaver directory for results.
pause