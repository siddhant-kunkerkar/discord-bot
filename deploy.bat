@echo off
SETLOCAL EnableDelayedExpansion

:: --- CONFIGURATION ---
SET "INSTANCE_NAME=instance-20260311-142446"
SET "ZONE=us-west1-a"
SET "REMOTE_USER=siddhantkunkerkar07"
SET "REMOTE_PATH=/home/siddhantkunkerkar07/my_bot"

echo 📦 Step 1: Zipping everything to dbot1.zip...
:: This zips the current folder's contents (where the .bat is)
powershell -Command "Get-ChildItem -Exclude 'dbot1.zip', 'venv', '.venv', '.git' | Compress-Archive -DestinationPath 'dbot1.zip' -Force"

echo 📤 Step 2: Uploading to %REMOTE_PATH%...
call gcloud compute scp dbot1.zip %REMOTE_USER%@%INSTANCE_NAME%:%REMOTE_PATH%/dbot1.zip --zone=%ZONE%

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Upload failed.
    goto :EXIT
)

echo 🔧 Step 3: Unzipping to /dbot1 and restarting...
:: -o = overwrite
:: -d dbot1 = extract into a folder named dbot1 (creates it if missing)
call gcloud compute ssh %REMOTE_USER%@%INSTANCE_NAME% --zone=%ZONE% --command="cd %REMOTE_PATH% ; unzip -o dbot1.zip -d dbot1 ; rm dbot1.zip ; pm2 restart dbot1"

echo ---------------------------------------------------
echo ✅ Done! Files extracted to %REMOTE_PATH%/dbot1
echo ---------------------------------------------------

:EXIT
if exist dbot1.zip del dbot1.zip
pause