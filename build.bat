@echo off
setlocal enableextensions enabledelayedexpansion

REM ====================================================================
REM  Build-Skript fuer Kneipenquiz (PyInstaller, --onedir)
REM
REM  Standard-Sechs-Schritt-Schema mit zentraler _buildlib.bat.
REM    - venv im Build-Ordner (Desktop, kein OneDrive!)
REM    - --onedir + --noupx
REM    - Entry-Point ist start.py (Launcher fuer Eingabe + Dashboard)
REM    - app.py wird mitgepackt; Streamlit/Pandas/Plotly bewusst NICHT
REM      gebundelt (zu fett). Dashboard nutzt System-Python.
REM ====================================================================

set "BLIB=%~dp0..\260507_Diverses\_buildlib.bat"
if not exist "%BLIB%" (
    echo [FEHLER] _buildlib.bat nicht gefunden: %BLIB%
    if not defined DEPLOY_TOOL pause
    exit /b 1
)

cd /d "%~dp0"

set "APPNAME=Quiz"

if not exist "start.py" (
    echo [FEHLER] start.py nicht gefunden -- bitte aus Quellverzeichnis starten.
    if not defined DEPLOY_TOOL pause
    exit /b 1
)
if not exist "quiz_eingabe.py" (
    echo [FEHLER] quiz_eingabe.py nicht gefunden.
    if not defined DEPLOY_TOOL pause
    exit /b 1
)
if not exist "quiz_data.py" (
    echo [FEHLER] quiz_data.py nicht gefunden.
    if not defined DEPLOY_TOOL pause
    exit /b 1
)

echo.
echo ========================================================
echo  %APPNAME% - Kompilierung
echo ========================================================

call "%BLIB%" :bl_init "%APPNAME%" "%USERPROFILE%\Desktop\Kompilieren\%APPNAME%"
call "%BLIB%" :bl_cpu_cap 85


REM =====================================================
REM  [1/6] Quellen kopieren
REM =====================================================
call "%BLIB%" :bl_step 1 6 "Kopiere Quelldateien in Build-Ordner..."

copy /Y "!SOURCE_DIR!\start.py"        "!BUILD_DIR!\" >nul
copy /Y "!SOURCE_DIR!\quiz_eingabe.py" "!BUILD_DIR!\" >nul
copy /Y "!SOURCE_DIR!\quiz_data.py"    "!BUILD_DIR!\" >nul
copy /Y "!SOURCE_DIR!\app.py"          "!BUILD_DIR!\" >nul

set "USE_ICON=0"
set "ICON="
if exist "!SOURCE_DIR!\icon.ico" (
    copy /Y "!SOURCE_DIR!\icon.ico" "!BUILD_DIR!\" >nul
    set "ICON=!BUILD_DIR!\icon.ico"
    set "USE_ICON=1"
    call "%BLIB%" :bl_log INFO "icon.ico gefunden und kopiert."
) else (
    call "%BLIB%" :bl_log INFO "Kein Icon vorhanden - Standard wird verwendet."
)

cd /d "!BUILD_DIR!"


REM =====================================================
REM  [2/6] Virtuelle Umgebung + Abhaengigkeiten
REM =====================================================
call "%BLIB%" :bl_step 2 6 "Erzeuge virtuelle Umgebung und installiere Pakete..."

py -m venv ".venv"
if errorlevel 1 (
    call "%BLIB%" :bl_log FEHLER "venv konnte nicht angelegt werden."
    goto :error_exit
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    call "%BLIB%" :bl_log FEHLER "venv konnte nicht aktiviert werden."
    goto :error_exit
)

python -m pip install %Q_FLAG% --upgrade pip setuptools wheel
if errorlevel 1 (
    call "%BLIB%" :bl_log FEHLER "pip-Update fehlgeschlagen."
    goto :error_exit
)
REM Eingabe-GUI braucht Matplotlib (+ Numpy als Abhaengigkeit) fuer den Dashboard-Reiter.
pip install %Q_FLAG% --upgrade matplotlib pyinstaller
if errorlevel 1 (
    call "%BLIB%" :bl_log FEHLER "pip install fehlgeschlagen."
    goto :error_exit
)
for /f "delims=" %%V in ('pyinstaller --version 2^>nul') do call "%BLIB%" :bl_log OK "PyInstaller %%V einsatzbereit."


REM =====================================================
REM  [3/6] Kompilierung (PyInstaller, --onedir, --noupx)
REM =====================================================
call "%BLIB%" :bl_step 3 6 "Starte PyInstaller (--onedir, --noupx, log-level=!PI_LOG!)..."

REM app.py wird als Datei mitgeliefert, damit das Dashboard sie findet.
REM icon.ico ebenfalls, damit die Tk-Fenster sie zur Laufzeit ueber sys._MEIPASS laden koennen
REM (--icon bettet sie nur als EXE-Ressource ein, das deckt Taskbar + Explorer ab,
REM  aber Tk braucht die Datei separat).
set "ADD_DATA=--add-data app.py;."
if "!USE_ICON!"=="1" set "ADD_DATA=!ADD_DATA! --add-data icon.ico;."

REM Schwergewichte, die wir definitiv nicht brauchen, aus dem Bundle halten.
REM Matplotlib + Numpy MUESSEN dagegen drinbleiben (Dashboard-Reiter).
set "EXCLUDES=--exclude-module streamlit --exclude-module pandas --exclude-module plotly --exclude-module openpyxl --exclude-module scipy --exclude-module pyarrow --exclude-module IPython --exclude-module jupyter"
set "COLLECT=--collect-data matplotlib"

REM Version aus CHANGELOG.md (Projektverwalter reicht EXE_VERSION als
REM Umgebungsvariable durch). Beim manuellen Build wird auf 0.0.0 zurueckgefallen.
REM Hinweis: PyInstaller nimmt --file-version/--product-version NICHT direkt;
REM dazu braeuchte es eine version.txt mit VSVersionInfo via --version-file.
REM Vorerst ohne expliziten Versionsstempel - die EXE laeuft auch so.
set "VER=%EXE_VERSION%"
if "!VER!"=="" set "VER=0.0.0"
call "%BLIB%" :bl_log INFO "Baue Version !VER! (ohne VSVersionInfo)."

if "!USE_ICON!"=="1" (
    pyinstaller --noconfirm --clean --onedir --windowed --noupx --log-level !PI_LOG! --name "%APPNAME%" --icon="!ICON!" !ADD_DATA! !EXCLUDES! !COLLECT! --distpath "!BUILD_DIR!" "start.py"
) else (
    pyinstaller --noconfirm --clean --onedir --windowed --noupx --log-level !PI_LOG! --name "%APPNAME%" !ADD_DATA! !EXCLUDES! !COLLECT! --distpath "!BUILD_DIR!" "start.py"
)

if errorlevel 1 (
    call "%BLIB%" :bl_log FEHLER "PyInstaller meldete Fehler."
    goto :error_exit
)


REM =====================================================
REM  [4/6] EXE + _internal\ zurueckkopieren (onedir-Mode)
REM =====================================================
call "%BLIB%" :bl_step 4 6 "Kopiere %APPNAME%.exe + _internal\ ins Quellverzeichnis..."

set "SRC_DIR=!BUILD_DIR!\%APPNAME%"
set "SRC_EXE=!SRC_DIR!\%APPNAME%.exe"
set "DEST_EXE=!SOURCE_DIR!\%APPNAME%.exe"
set "DEST_INTERNAL=!SOURCE_DIR!\_internal"

if not exist "!SRC_EXE!" (
    call "%BLIB%" :bl_log FEHLER "Build hat keine EXE produziert: !SRC_EXE!"
    goto :error_exit
)

REM Laufende Instanzen beenden, damit alte EXE freigegeben wird.
tasklist /FI "IMAGENAME eq %APPNAME%.exe" 2>nul | findstr /I "%APPNAME%.exe" >nul
if not errorlevel 1 (
    call "%BLIB%" :bl_log INFO "Laufende %APPNAME%.exe-Instanzen beenden..."
    taskkill /F /IM "%APPNAME%.exe" >nul 2>&1
    ping -n 2 127.0.0.1 >nul
)

REM Alte Artefakte entfernen (Retry gegen Locks durch OneDrive/AV)
set "RETRY_COUNT=0"
set "MAX_RETRIES=5"

:retry_clean
set "CLEAN_OK=1"
if exist "!DEST_EXE!" (
    del /F /Q "!DEST_EXE!" >nul 2>&1
    if exist "!DEST_EXE!" set "CLEAN_OK=0"
)
if exist "!DEST_INTERNAL!" (
    rmdir /S /Q "!DEST_INTERNAL!" >nul 2>&1
    if exist "!DEST_INTERNAL!" set "CLEAN_OK=0"
)
if "!CLEAN_OK!"=="1" goto :clean_done

set /a RETRY_COUNT+=1
if !RETRY_COUNT! lss !MAX_RETRIES! (
    call "%BLIB%" :bl_log WARNUNG "Versuch !RETRY_COUNT!/!MAX_RETRIES! - alte Artefakte gesperrt, warte 2 s..."
    ping -n 3 127.0.0.1 >nul
    goto :retry_clean
)

call "%BLIB%" :bl_log FEHLER "Alte Artefakte konnten nach !MAX_RETRIES! Versuchen nicht entfernt werden."
goto :error_exit

:clean_done
xcopy /E /I /Y /Q "!SRC_DIR!\*" "!SOURCE_DIR!\" >nul
if errorlevel 1 (
    call "%BLIB%" :bl_log FEHLER "xcopy nach Quellverzeichnis fehlgeschlagen."
    goto :error_exit
)

if not exist "!DEST_EXE!" (
    call "%BLIB%" :bl_log FEHLER "EXE nach Copy nicht im Quellverzeichnis gefunden."
    goto :error_exit
)
if not exist "!DEST_INTERNAL!" (
    call "%BLIB%" :bl_log FEHLER "_internal-Ordner nach Copy nicht im Quellverzeichnis gefunden."
    goto :error_exit
)

call "%BLIB%" :bl_size "!DEST_EXE!"


REM =====================================================
REM  [5/6] Aufraeumen
REM =====================================================
call "%BLIB%" :bl_step 5 6 "Aufraeumen..."

cd /d "!SOURCE_DIR!"
rmdir /S /Q "!BUILD_DIR!" 2>nul

if exist "!BUILD_DIR!" (
    call "%BLIB%" :bl_log WARNUNG "Build-Ordner konnte nicht vollstaendig geloescht werden: !BUILD_DIR!"
) else (
    call "%BLIB%" :bl_log OK "Build-Ordner entfernt."
)


REM =====================================================
REM  [6/6] Hinweise
REM =====================================================
call "%BLIB%" :bl_step 6 6 "Hinweise..."
call "%BLIB%" :bl_log INFO "EXE und _internal\ gehoeren zusammen - nicht trennen."
call "%BLIB%" :bl_log INFO "data.json muss neben der EXE liegen - sie wird zur Laufzeit gelesen und geschrieben."
call "%BLIB%" :bl_log INFO "Dashboard-Knopf benoetigt ein System-Python mit Streamlit im PATH."


call "%BLIB%" :bl_finish "%APPNAME%.exe"
exit /b 0


:error_exit
call "%BLIB%" :bl_error_exit
if not defined DEPLOY_TOOL pause
exit /b 1
