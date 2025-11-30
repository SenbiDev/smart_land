@echo off
:: PATH KE BACKEND
cd senbidev\smart_land\smart_land-faiz

echo [1/5] Menghapus Database Lama & Migrasi...
if exist db.sqlite3 del db.sqlite3
del authentication\migrations\0*.py

echo [2/5] Membuat Migrasi Baru...
python manage.py makemigrations
python manage.py migrate

echo [3/5] Membuat Superuser (admin/admin)...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_land.settings'); import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

echo [4/5] Mengisi Data Role (Seeding)...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_land.settings'); import django; django.setup(); from authentication.models import Role; roles=['Superadmin', 'Admin', 'Operator', 'Investor', 'Viewer']; [Role.objects.get_or_create(name=r, description=f'Role {r}') for r in roles]; print('Roles created successfully!')"

echo [5/5] Selesai! Jalankan server manual dengan: python manage.py runserver
pause