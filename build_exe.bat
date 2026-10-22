@echo off
chcp 65001 >nul 2>&1
setlocal enableextensions enabledelayedexpansion

REM ====================================================================
REM  Build-Skript fuer Kneipenquiz (Nuitka, --onefile)
REM
REM  Migriert von PyInstaller --onedir auf Nuitka --onefile (EXE-Schlank-
REM  heitskur, Rezept: ..\260507_Diverses\REZEPT_KLEINE_EXE.md). Vorlage:
REM  260625_Schallberechnung\build_exe.bat (tkinter+numpy+matplotlib,
REM  naechstaehnlicher lebender Nuitka-Onefile-Bat).
REM
REM  Standard-Sechs-Schritt-Schema mit zentraler _buildlib.bat (Heartbeat,
REM  Verbosity-Schalter, Banner, Cleanup). Kein venv mehr -- Nuitka baut
REM  gegen das System-Python (pip install nuitka).
REM
REM  Entry-Point ist start.py (Bootstrap fuer die Tk-Eingabe-GUI mit
REM  Dashboard-Reiter). app.py (Streamlit-Variante) wird NICHT von Nuitka
REM  gebuendelt: die alte PyInstaller-onedir-Bundelung nach _internal\
REM  ergab dort keinen echten Mehrwert, und unter Onefile wuerde
REM  --include-data-file sie nur in den fluechtigen Onefile-Cache-Ordner
REM  extrahieren (versionsabhaengiger Temp-Pfad, kein fester Ort neben der
REM  EXE) -- fuer den manuellen "streamlit run app.py"-Aufruf nutzlos.
REM  app.py bleibt stattdessen einfach im Quellordner liegen (CHANGELOG:
REM  "bleibt im Repo fuer den manuellen Aufruf erhalten"), unangetastet
REM  vom Build. matplotlib + numpy sind dagegen ECHTE Laufzeit-Importe
REM  von quiz_eingabe.py (Dashboard-Reiter) und werden mitkompiliert.
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

if not defined DEPLOY_TOOL (
    echo.
    echo ========================================================
    echo  %APPNAME% - Kompilierung
    echo ========================================================
)

call "%BLIB%" :bl_init "%APPNAME%" "%USERPROFILE%\Desktop\Kompilieren\%APPNAME%"
call "%BLIB%" :bl_cpu_cap 80


REM =====================================================
REM  [1/6] Quellen kopieren
REM =====================================================
call "%BLIB%" :bl_step 1 6 "Kopiere Quelldateien in Build-Ordner..."

xcopy /Y "!SOURCE_DIR!\start.py"        "!BUILD_DIR!\" >nul
xcopy /Y "!SOURCE_DIR!\quiz_eingabe.py" "!BUILD_DIR!\" >nul
xcopy /Y "!SOURCE_DIR!\quiz_data.py"    "!BUILD_DIR!\" >nul

REM app.py (Streamlit-Dashboard) wird NICHT in den Build-Ordner kopiert
REM und NICHT von Nuitka gebuendelt -- siehe Begruendung im Kopf-Kommentar.

set "USE_ICON=0"
if exist "!SOURCE_DIR!\icon.ico" (
    xcopy /Y "!SOURCE_DIR!\icon.ico" "!BUILD_DIR!\" >nul
    set "USE_ICON=1"
    call "%BLIB%" :bl_log INFO "icon.ico gefunden und kopiert."
) else (
    call "%BLIB%" :bl_log INFO "Kein Icon vorhanden - Standard wird verwendet."
)

REM logo.png (Header-Bildmarke) mitkopieren, damit sie als Datendatei ins
REM Onefile-Bundle wandert und quiz_eingabe.py sie zur Laufzeit findet.
set "USE_LOGO=0"
if exist "!SOURCE_DIR!\logo.png" (
    xcopy /Y "!SOURCE_DIR!\logo.png" "!BUILD_DIR!\" >nul
    set "USE_LOGO=1"
    call "%BLIB%" :bl_log INFO "logo.png gefunden und kopiert."
) else (
    call "%BLIB%" :bl_log INFO "Kein logo.png vorhanden - Header ohne Bildmarke."
)

cd /d "!BUILD_DIR!"


REM =====================================================
REM  [2/6] Pakete pruefen (Pre-Flight, kein automatisches pip install)
REM =====================================================
call "%BLIB%" :bl_step 2 6 "Prüfe benötigte Pakete..."

python -c "import nuitka, tkinter, matplotlib, numpy" 2>nul
if errorlevel 1 (
    call "%BLIB%" :bl_log FEHLER "Pakete fehlen. Bitte installieren: pip install nuitka matplotlib numpy"
    goto :error_exit
)
call "%BLIB%" :bl_log OK "Pakete bereit."

REM Datei-Version: aus Projektverwaltung (EXE_VERSION, oberste CHANGELOG-Version)
REM oder Fallback 0.0.0 bei manuellem Build. Vierstellige FILE_VERSION fuer Nuitka.
call "%BLIB%" :bl_resolve_version
set "FILE_VERSION=%EXE_VERSION%.0"

REM Firmen-/Urheber-Metadaten: Firma + Name gemeinsam im CompanyName-Feld
REM (Hover) und im Copyright-Feld (Details). Aus der Projektverwaltung
REM (EXE_COMPANY/EXE_COPYRIGHT), sonst Fallback fuer den manuellen Direkt-Build.
if not defined EXE_COMPANY set "EXE_COMPANY=E1 Energiemanagement · Felix Rundel"
if not defined EXE_COPYRIGHT set "EXE_COPYRIGHT=© E1 Energiemanagement · Felix Rundel"


REM =====================================================
REM  [3/6] Kompilierung (ohne --show-progress, Heartbeat traegt das Lebenszeichen)
REM =====================================================
call "%BLIB%" :bl_step 3 6 "Starte Nuitka..."

set "ICON_FLAG="
set "ICON_DATA_FLAG="
if "!USE_ICON!"=="1" (
    set "ICON_FLAG=--windows-icon-from-ico=icon.ico"
    REM icon.ico zusaetzlich als Datendatei buendeln, damit quiz_eingabe.py
    REM (Tk iconbitmap) sie zur Laufzeit findet -- --windows-icon-from-ico
    REM deckt nur die EXE-Ressource ab (Taskleiste/Explorer), nicht den
    REM Tk-Fensterrahmen, der die Datei separat oeffnet.
    set "ICON_DATA_FLAG=--include-data-file=icon.ico=icon.ico"
)

set "LOGO_DATA_FLAG="
if "!USE_LOGO!"=="1" (
    REM logo.png als Datendatei buendeln -- der Header laedt sie via
    REM tk.PhotoImage (Tk liest PNG nativ, kein PIL zur Laufzeit).
    set "LOGO_DATA_FLAG=--include-data-file=logo.png=logo.png"
)

REM ---------------------------------------------------------------------------
REM  EXE-Schlankheitskur (siehe ..\260507_Diverses\REZEPT_KLEINE_EXE.md).
REM  Import-Grep gegen start.py/quiz_eingabe.py/quiz_data.py (18.07.2026):
REM   - echte Fremdpakete: matplotlib (+ numpy als Zwangs-Abhaengigkeit,
REM     NICHT sperren -- Regel 5 im CLAUDE.md, Musterfall Quizverwaltung).
REM   - app.py (streamlit/pandas/plotly/numpy) wird gar nicht erst
REM     angefasst (siehe Kopf-Kommentar) -- Nuitka sieht ihre Importe nie,
REM     daher duerfen streamlit/pandas/plotly gesperrt werden.
REM   - kein PIL/Pillow im Quellstamm (anders als Schallberechnung/
REM     tkintermapview) -- PIL wird gesperrt.
REM   - Saeule A: generische Mitfahrer -- Dev-/Test-Tools, Alt-GUIs
REM     (PyQt5/6, PySide2/6, wx), DB-/Data-Science-Freeloader, die im
REM     Code nirgends importiert werden.
REM   - Saeule B: Tcl/Tk-Fremdencodings raus (tkinter genutzt, aber keine
REM     CJK/Kyrillisch-Eingabe im Tool).
REM   - Saeule C: matplotlib-Beiwerk (nur eingebettete Liniencharts/Heatmap/
REM     Scatter im Dashboard-Reiter, kein Stylelib/Sample-Data/Web-Backend).
REM   - Saeule D: --lto=no -- matplotlib-Stack ist schwer, LTO bringt hier
REM     laut Rezept kaum Ersparnis bei deutlich laengerer Linkzeit.
REM   - Cache-Haertung: {VERSION} im Onefile-Tempdir-Pfad, damit ein
REM     Rebuild den alten Cache nicht weiterverwendet; Datei-/Produktversion
REM     kommt aus FILE_VERSION (an EXE_VERSION/CHANGELOG gebunden).
REM ---------------------------------------------------------------------------
python -m nuitka ^
    --standalone --onefile ^
    %NUITKA_JOB_FLAG% ^
    --onefile-tempdir-spec="{CACHE_DIR}\Nuitka-Cache\Quiz\{VERSION}" ^
    --onefile-cache-mode=cached ^
    --lto=no ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --enable-plugin=matplotlib ^
    !ICON_FLAG! ^
    !ICON_DATA_FLAG! ^
    !LOGO_DATA_FLAG! ^
    --noinclude-pytest-mode=nofollow ^
    --noinclude-setuptools-mode=nofollow ^
    --noinclude-unittest-mode=nofollow ^
    --noinclude-IPython-mode=nofollow ^
    --nofollow-import-to=doctest ^
    --nofollow-import-to=sphinx ^
    --nofollow-import-to=pip ^
    --nofollow-import-to=wheel ^
    --nofollow-import-to=jupyter ^
    --nofollow-import-to=notebook ^
    --nofollow-import-to=PyQt5 ^
    --nofollow-import-to=PyQt6 ^
    --nofollow-import-to=PySide2 ^
    --nofollow-import-to=PySide6 ^
    --nofollow-import-to=wx ^
    --nofollow-import-to=streamlit ^
    --nofollow-import-to=pandas ^
    --nofollow-import-to=plotly ^
    --nofollow-import-to=scipy ^
    --nofollow-import-to=cryptography ^
    --nofollow-import-to=pyarrow ^
    --nofollow-import-to=psycopg2 ^
    --nofollow-import-to=psycopg2_binary ^
    --nofollow-import-to=greenlet ^
    --nofollow-import-to=sqlalchemy ^
    --nofollow-import-to=lxml ^
    --nofollow-import-to=tables ^
    --nofollow-import-to=h5py ^
    --nofollow-import-to=sympy ^
    --nofollow-import-to=numba ^
    --nofollow-import-to=llvmlite ^
    --nofollow-import-to=torch ^
    --nofollow-import-to=tensorflow ^
    --nofollow-import-to=sklearn ^
    --nofollow-import-to=cv2 ^
    --nofollow-import-to=bokeh ^
    --nofollow-import-to=xlsxwriter ^
    --nofollow-import-to=openpyxl ^
    --nofollow-import-to=bs4 ^
    --nofollow-import-to=zstandard ^
    --nofollow-import-to=babel ^
    --nofollow-import-to=tkcalendar ^
    --nofollow-import-to=mplcursors ^
    --nofollow-import-to=seaborn ^
    --nofollow-import-to=docutils ^
    --noinclude-data-files=tcl/encoding/iso2022*.enc ^
    --noinclude-data-files=tcl/encoding/koi8*.enc ^
    --noinclude-data-files=tcl/encoding/mac*.enc ^
    --noinclude-data-files=tcl/encoding/big5.enc ^
    --noinclude-data-files=tcl/encoding/gb2312.enc ^
    --noinclude-data-files=tcl/encoding/euc_jp.enc ^
    --noinclude-data-files=tcl/encoding/euc_kr.enc ^
    --noinclude-data-files=tcl/msgs/*.msg ^
    --noinclude-data-files=tcl/tzdata/* ^
    --noinclude-data-files=tk/demos/* ^
    --noinclude-data-files=matplotlib/mpl-data/sample_data/* ^
    --noinclude-data-files=matplotlib/mpl-data/images/* ^
    --noinclude-data-files=matplotlib/mpl-data/stylelib/* ^
    --noinclude-data-files=matplotlib/backends/web_backend/* ^
    --prefer-source-code ^
    --python-flag=no_site ^
    --python-flag=-OO ^
    --windows-company-name="%EXE_COMPANY%" ^
    --copyright="%EXE_COPYRIGHT%" ^
    --windows-product-name="Quiz" ^
    --windows-file-version=%FILE_VERSION% ^
    --windows-product-version=%FILE_VERSION% ^
    --output-filename=Quiz.exe ^
    --assume-yes-for-downloads ^
    start.py

if !ERRORLEVEL! NEQ 0 (
    call "%BLIB%" :bl_log FEHLER "Nuitka-Kompilierung fehlgeschlagen."
    goto :error_exit
)


REM =====================================================
REM  [4/6] EXE zurückkopieren
REM =====================================================
call "%BLIB%" :bl_step 4 6 "Kopiere %APPNAME%.exe ins Quellverzeichnis..."

REM Laufende Instanzen beenden, damit die alte EXE freigegeben wird
REM (onedir hatte zusaetzlich einen _internal\-Ordner -- entfaellt bei onefile).
tasklist /FI "IMAGENAME eq %APPNAME%.exe" 2>nul | findstr /I "%APPNAME%.exe" >nul
if not errorlevel 1 (
    call "%BLIB%" :bl_log INFO "Laufende %APPNAME%.exe-Instanzen beenden..."
    taskkill /F /IM "%APPNAME%.exe" >nul 2>&1
    ping -n 2 127.0.0.1 >nul
)

if exist "%APPNAME%.exe" (
    copy /Y "%APPNAME%.exe" "!SOURCE_DIR!\" >nul
) else if exist "start.dist\%APPNAME%.exe" (
    copy /Y "start.dist\%APPNAME%.exe" "!SOURCE_DIR!\" >nul
)

if not exist "!SOURCE_DIR!\%APPNAME%.exe" (
    call "%BLIB%" :bl_log FEHLER "Konnte %APPNAME%.exe nicht ins Quellverzeichnis kopieren."
    goto :error_exit
)

REM Altes _internal\ aus der PyInstaller-onedir-Aera entfernt sich selbst nicht --
REM onefile braucht es nicht mehr, ein Altrest wuerde nur verwirren.
if exist "!SOURCE_DIR!\_internal" (
    rmdir /S /Q "!SOURCE_DIR!\_internal" 2>nul
    call "%BLIB%" :bl_log INFO "Alten _internal\-Ordner aus onedir-Aera entfernt."
)

call "%BLIB%" :bl_size "!SOURCE_DIR!\%APPNAME%.exe"


REM =====================================================
REM  [5/6] Aufräumen
REM =====================================================
call "%BLIB%" :bl_step 5 6 "Aufräumen..."

cd /d "!SOURCE_DIR!"
rmdir /S /Q "!BUILD_DIR!" 2>nul

if exist "!BUILD_DIR!" (
    call "%BLIB%" :bl_log WARNUNG "Build-Ordner konnte nicht vollständig gelöscht werden: !BUILD_DIR!"
) else (
    call "%BLIB%" :bl_log OK "Build-Ordner entfernt."
)


REM =====================================================
REM  [6/6] Hinweise
REM =====================================================
call "%BLIB%" :bl_step 6 6 "Hinweise..."
call "%BLIB%" :bl_log INFO "Onefile: kein _internal\ mehr noetig - die EXE steht allein."
call "%BLIB%" :bl_log INFO "data.json liegt im PROJEKTORDNER (seit v0.8.1), nicht neben der EXE - die EXE findet ihn ueber die OneDrive-Wurzel."
call "%BLIB%" :bl_log INFO "Grund: data.json ist die Datenquelle des veroeffentlichten Streamlit-Dashboards und mitversioniert. Ein neuer Abend erreicht die Web-Ansicht nur ueber Commit und Push."
call "%BLIB%" :bl_log INFO "Dashboard ist ein eingebetteter matplotlib-Reiter in der EXE selbst - kein Extra-Prozess."
call "%BLIB%" :bl_log INFO "app.py (Streamlit-Variante) bleibt unangetastet im Quellordner - manueller 'streamlit run app.py'-Aufruf mit System-Python."


call "%BLIB%" :bl_finish "%APPNAME%.exe"
exit /b 0


:error_exit
call "%BLIB%" :bl_error_exit
if not defined DEPLOY_TOOL pause
exit /b 1
