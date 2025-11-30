@echo off
SETLOCAL

:: --- KONFIGURASI PATH (SESUAIKAN JIKA PERLU) ---
:: Pastikan path ini sesuai dengan struktur folder Anda
SET "BACKEND_DIR=senbidev\smart_land\smart_land-faiz"
SET "FRONTEND_DIR=faizulhq\lahan-pintar2\LAHAN-PINTAR2-4a8a5e09b0db082605b6e735303c6d7af2d5e3a0"

echo ========================================================
echo      LAHAN PINTAR - AUTO RESET & RUN SCRIPT
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

:: Hapus folder migrations (Opsional - aktifkan jika ingin reset total migrasi)
:: for /d /r "%BACKEND_DIR%" %%d in (migrations) do @if exist "%%d" rd /s /q "%%d"

echo.
echo [2/4] Menjalankan Migrasi Ulang...
cd /d "%BACKEND_DIR%"
python manage.py makemigrations
python manage.py migrate

echo.
echo [3/4] Membuat Superuser Default...
:: Menggunakan script python one-liner untuk membuat superuser otomatis
:: Username: admin, Email: admin@example.com, Password: admin
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_land.settings'); import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None"
echo - Superuser dibuat: (User: admin / Pass: admin)

echo.
echo [4/4] Menjalankan Server...

:: Jalankan Backend di Window Baru
start "Backend Lahan Pintar" cmd /k "python manage.py runserver"

:: Jalankan Frontend di Window Baru
cd /d "..\..\..\%FRONTEND_DIR%"
echo - Menginstall dependensi frontend (jika belum)...
call npm install
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