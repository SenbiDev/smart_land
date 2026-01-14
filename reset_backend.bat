@echo off
SETLOCAL EnableDelayedExpansion

:: Pindah ke direktori di mana script ini berada agar path relatif bekerja
cd /d "%~dp0"

echo ========================================================
echo    RESET DATABASE ^& SEED ROLE - LAHAN PINTAR
echo ========================================================
echo.
echo [WARNING] Script ini akan:
echo   1. MENGHAPUS database (db.sqlite3)
echo   2. Membersihkan file migrasi lama di SEMUA APP
echo   3. Membuat tabel baru (migrate)
echo   4. Seed Role dan Superuser default
echo.
set /p confirm="Lanjutkan? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Dibatalkan.
    pause
    exit /b
)

:: --- 1. CEK MANAGE.PY ---
if not exist "manage.py" (
    echo.
    echo [ERROR] manage.py tidak ditemukan di folder ini!
    echo Pastikan file .bat ini ada di folder sejajar dengan manage.py
    pause
    exit /b
)

:: --- 2. RESET DATABASE ---
echo.
echo [1/4] Menghapus Database Lama...
if exist "db.sqlite3" (
    del "db.sqlite3"
    echo        Deleted: db.sqlite3
) else (
    echo        Database belum ada.
)

:: --- 3. HAPUS FILE MIGRATIONS ---
echo.
echo [2/4] Membersihkan file migrations...

:: LIST APP KAMU (Tambahkan di sini jika ada app baru)
set APPS_LIST=asset authentication dashboard expense funding production profit_distribution sales

for %%A in (%APPS_LIST%) do (
    if exist "%%A\migrations" (
        echo        Checking: %%A...
        pushd "%%A\migrations"
        for %%F in (*.py) do (
            if not "%%F"=="__init__.py" (
                del "%%F"
                echo          - Del: %%F
            )
        )
        popd
    )
)

:: --- 4. MIGRATE ---
echo.
echo [3/4] Membuat Tabel Baru (Migrate)...
python manage.py makemigrations
if %errorlevel% neq 0 goto ErrorHandler

python manage.py migrate
if %errorlevel% neq 0 goto ErrorHandler

:: --- 5. SEED ROLE & SUPERUSER ---
echo.
echo [4/4] Seeding Data (Role ^& Admin)...

:: Python One-Liner (Pastikan nama project 'smart_land' benar)
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_land.settings'); import django; django.setup(); from django.contrib.auth import get_user_model; from authentication.models import Role; User = get_user_model(); roles = [('Superadmin', 'Akses Penuh'), ('Admin', 'Akses Kelola'), ('Operator', 'Input Data'), ('Investor', 'Akses Pantau')]; [Role.objects.get_or_create(name=r[0], defaults={'description': r[1]}) for r in roles]; print('       > Roles Created'); super_role = Role.objects.get(name='Superadmin'); User.objects.create_superuser('admin', 'admin@lahan.com', 'admin', role=super_role) if not User.objects.filter(username='admin').exists() else print('       > Admin already exists');"

if %errorlevel% neq 0 goto ErrorHandler

echo.
echo ========================================================
echo  SUKSES! Silakan jalankan: python manage.py runserver
echo  Login: admin / admin
echo ========================================================
pause
exit /b

:ErrorHandler
echo.
echo [FATAL ERROR] Terjadi kesalahan saat eksekusi.
pause
exit /b 1