@echo off
REM Create complete PPP_PROJECT folder structure
REM Run this ONCE to set up all directories

setlocal enabledelayedexpansion

set BASE=C:\PPP_PROJECT

echo.
echo ========================================
echo PPP PROJECT FOLDER STRUCTURE CREATION
echo ========================================
echo.
echo Creating directories in: %BASE%
echo.

REM Create main directories
for %%d in (
    data
    products\status
    products\sp3
    products\clk
    products\erp
    products\dcb
    products\bia
    products\ionex
    products\atx
    products\snx
    GAMP_work
    PRIDE_work
    RTKLIB_work
    results
    station_reports
    config
    scripts
) do (
    if not exist "%BASE%\%%d" (
        mkdir "%BASE%\%%d"
        echo [OK] Created: %BASE%\%%d
    ) else (
        echo [SKIP] Already exists: %BASE%\%%d
    )
)

echo.
echo ========================================
echo FOLDER STRUCTURE COMPLETE
echo ========================================
echo.
echo Structure:
echo.
echo C:\PPP_PROJECT\
echo ├── data\                    (observation files .rnx)
echo ├── products\
echo │   ├── status\              (status files for station checking)
echo │   ├── sp3\                 (precise orbit files)
echo │   ├── clk\                 (precise clock files)
echo │   ├── erp\                 (earth rotation parameters)
echo │   ├── dcb\                 (code bias files)
echo │   ├── bia\                 (phase bias for PPP-AR)
echo │   ├── ionex\               (ionosphere maps)
echo │   ├── atx\                 (antenna corrections)
echo │   └── snx\                 (station coordinates)
echo ├── GAMP_work\               (GAMP config and results)
echo ├── PRIDE_work\              (PRIDE results)
echo ├── RTKLIB_work\             (RTKLIB results)
echo ├── results\                 (final analysis output)
echo ├── station_reports\         (station analysis markdown)
echo ├── config\                  (configuration files)
echo └── scripts\                 (helper scripts)
echo.
echo.
echo ✓ Download status files:
echo   - Place 26015.V2status in products\status\
echo   - Place 26015.V3status in products\status\
echo.
echo ✓ Download observation files:
echo   - Run: python download_ppp_data.py
echo.
echo ✓ Check a station:
echo   - Run: python check_station.py BJFS
echo   - Run: python check_station.py GOLD
echo.
pause
