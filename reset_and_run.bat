@echo off
SETLOCAL

:: --- KONFIGURASI PATH (SESUAIKAN JIKA PERLU) ---
SET "BACKEND_DIR=senbidev\smart_land\smart_land-faiz"
SET "FRONTEND_DIR=faizulhq\lahan-pintar2\LAHAN-PINTAR2-4a8a5e09b0db082605b6e735303c6d7af2d5e3a0"

echo ========================================================
echo      LAHAN PINTAR - AUTO RESET, SEEDING & RUN
echo ========================================================
echo.

:: 1. RESET BACKEND
echo [1/4] Mereset Database Backend...
if exist "%BACKEND_DIR%\db.sqlite3" (
    del "%BACKEND_DIR%\db.sqlite3"
    echo - Database lama dihapus.
) else (
    echo - Tidak ada database lama.
)

echo.
echo [2/4] Menjalankan Migrasi Ulang...
cd /d "%BACKEND_DIR%"
python manage.py makemigrations
python manage.py migrate

echo.
echo [3/4] Seeding Data (Roles & Superuser)...

:: --- SCRIPT PYTHON OTOMATIS (ONE-LINER) ---
:: Penjelasan Logika Script di bawah:
:: 1. Setup Django
:: 2. Import model Role & User (Pastikan 'authentication' adalah nama app Anda)
:: 3. Loop bikin Role: Superadmin, Admin, Operator, Investor, Viewer
:: 4. Ambil object role 'Superadmin'
:: 5. Buat Superuser 'admin' dan langsung pasang role-nya jadi Superadmin

python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_land.settings'); import django; django.setup(); from django.contrib.auth import get_user_model; from authentication.models import Role; User = get_user_model(); roles = ['Superadmin', 'Admin', 'Operator', 'Investor', 'Viewer']; [Role.objects.get_or_create(name=r) for r in roles]; print('- Roles berhasil dibuat.'); r_sup = Role.objects.get(name='Superadmin'); User.objects.create_superuser('admin', 'admin@example.com', 'admin', role=r_sup) if not User.objects.filter(username='admin').exists() else print('- Superuser sudah ada.')"

echo - Superuser SIAP: (User: admin / Pass: admin) dengan Role Superadmin.

echo.
echo [4/4] Menjalankan Server...

:: Jalankan Backend di Window Baru
start "Backend Lahan Pintar" cmd /k "python manage.py runserver"

:: Jalankan Frontend di Window Baru
cd /d "..\..\..\%FRONTEND_DIR%"
echo - Mengecek dependensi frontend...
if not exist "node_modules" call npm install
start "Frontend Lahan Pintar" cmd /k "npm run dev"

echo.
echo ========================================================
echo  SELESAI! APLIKASI SEDANG BERJALAN.
echo  Backend : http://127.0.0.1:8000
echo  Frontend: http://localhost:3000
echo.
echo  Login Superuser:
echo  Username: admin
echo  Password: admin
echo ========================================================
pause