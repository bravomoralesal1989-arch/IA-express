#!/bin/bash
set -e

echo "=================================================================="
echo "    IA EXPRESS - SCRIPT DE DESPLIEGUE AUTOMÁTICO EN PRODUCCIÓN   "
echo "=================================================================="

# 1. Actualizar sistema e instalar dependencias
sudo apt update && sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

# 2. Crear directorio de aplicación
sudo mkdir -p /var/www/iaexpress
sudo cp -r ../backend /var/www/iaexpress/
sudo cp -r ../frontend /var/www/iaexpress/

# 3. Entorno virtual Python y dependencias
cd /var/www/iaexpress
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r backend/requirements.txt

# 4. Inicializar base de datos y datos reales
cd backend
../venv/bin/python seed_demo_data.py
../venv/bin/python add_bar_los_mayores.py

# 5. Instalar servicio Systemd
sudo cp /var/www/iaexpress/deploy/iaexpress.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iaexpress
sudo systemctl restart iaexpress

# 6. Configurar Nginx
sudo cp /var/www/iaexpress/deploy/nginx.conf /etc/nginx/sites-available/express.aedia.es
sudo ln -sf /etc/nginx/sites-available/express.aedia.es /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "=================================================================="
echo "  ¡DESPLIEGUE EN PRODUCCIÓN COMPLETADO CON ÉXITO!                "
echo "  URL del Servidor: https://express.aedia.es                      "
echo "=================================================================="
