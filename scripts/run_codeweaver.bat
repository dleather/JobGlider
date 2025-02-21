@echo off
setlocal

REM Set paths
set ROOT_DIR=C:\Users\davle\jobhunt_webhook
set TEMPLATE_FILE=%ROOT_DIR%\awesome_cv_cover_letter_template.tex
set CLASS_FILE=%ROOT_DIR%\awesome-cv.cls

REM Create output directory if it doesn't exist
if not exist "%ROOT_DIR%\codeweaver_output" mkdir "%ROOT_DIR%\codeweaver_output"

REM Run codeweaver on the main template file
echo Processing cover letter template...
codeweaver analyze "%TEMPLATE_FILE%" ^
    --output "%ROOT_DIR%\codeweaver_output\template_analysis.json" ^
    --ignore "*.yml,*.yaml,*.md,LICENCE,*.gitignore" ^
    --focus "*.tex,*.cls" ^
    --context "LaTeX template for generating professional cover letters using the Awesome-CV class"

REM Run codeweaver on the class file
echo Processing class file...
codeweaver analyze "%CLASS_FILE%" ^
    --output "%ROOT_DIR%\codeweaver_output\class_analysis.json" ^
    --ignore "*.yml,*.yaml,*.md,LICENCE,*.gitignore" ^
    --focus "*.tex,*.cls" ^
    --context "LaTeX class file defining the structure and layout for Awesome-CV documents"

echo Analysis complete. Check the codeweaver_output directory for results.
pause