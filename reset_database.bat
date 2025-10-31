@echo off
ECHO ==========================================================
ECHO == SCRIPT RESET DATABASE & MIGRATIONS SMART_LAND ==
ECHO ==========================================================
ECHO.
ECHO PERINGATAN: Ini akan MENGHAPUS database (db.sqlite3)
ECHO dan SEMUA file migrasi lama (.py) sebelum membuat yang baru.
ECHO.
PAUSE

REM --- LANGKAH 1: HAPUS DATABASE LAMA ---
ECHO [1/3] Menghapus database lama (db.sqlite3)...
IF EXIST db.sqlite3 (
    del db.sqlite3
    ECHO [OK] db.sqlite3 dihapus.
) ELSE (
    ECHO [INFO] db.sqlite3 tidak ditemukan, melanjutkan.
)
ECHO.

REM --- LANGKAH 2: HAPUS FILE MIGRATIONS LAMA (.PY) ---
ECHO [2/3] Menghapus file migrasi lama di semua app...

REM Daftar semua app Anda yang memiliki 'migrations'
set "APPS=asset authentication dashboard distribution_detail expense funding funding_source investor ownership production profit_distribution project reporting"

FOR %%A IN (%APPS%) DO (
    ECHO.
    ECHO   -> Memproses '%%A\migrations\'...
    IF EXIST "%%A\migrations\" (
        pushd "%%A\migrations\"
        REM Loop dan hapus .py SELAIN __init__.py
        FOR %%F IN (*.py) DO (
            IF NOT "%%F" == "__init__.py" (
                ECHO      - Menghapus %%F
                del "%%F"
            )
        )
        popd
        ECHO   [OK] Folder '%%A\migrations\' dibersihkan.
    ) ELSE (
        ECHO   [WARN] Folder '%%A\migrations\' tidak ditemukan.
    )
)
ECHO.
ECHO [OK] Semua file migrasi lama telah dihapus.
ECHO.

REM --- LANGKAH 3: BUAT MIGRATIONS & DATABASE BARU ---
ECHO [3/3] Membuat migrasi baru berdasarkan model...
python manage.py makemigrations
IF %errorlevel% NEQ 0 (
    ECHO [ERROR] Gagal membuat migrasi! Hentikan.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO Menerapkan migrasi ke database baru...
python manage.py migrate
IF %errorlevel% NEQ 0 (
    ECHO [ERROR] Gagal menerapkan migrasi! Hentikan.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO ==========================================================
ECHO == BERHASIL! ==
ECHO Database dan migrasi Anda telah di-reset.
ECHO ==========================================================
ECHO.
ECHO Langkah selanjutnya:
ECHO 1. (Opsional) python manage.py createsuperuser
ECHO 2. python manage.py runserver
ECHO 3. Lanjutkan ke Langkah 4 (Update Serializer) di instruksi.
ECHO.
PAUSE