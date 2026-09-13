#!/bin/bash
set -e

echo "=================================================================="
echo "    IA EXPRESS - SCRIPT DE DESPLIEGUE AUTOMÁTICO EN PRODUCCIÓN   "
echo "=================================================================="

# 0. Determinar directorio del repositorio y de instalación
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
APP_DIR="/var/www/IA-express"

echo "--> Directorio detectado del repo: $REPO_DIR"

# Si no estamos en /var/www/IA-express, sincronizamos/creamos
if [ "$REPO_DIR" != "$APP_DIR" ]; then
    echo "--> Copiando archivos a $APP_DIR..."
    sudo mkdir -p "$APP_DIR"
    sudo cp -r "$REPO_DIR"/* "$APP_DIR"/
fi

cd "$APP_DIR"

# 1. Actualizar sistema e instalar dependencias
echo "--> Instalando paquetes del sistema..."
sudo apt update && sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

# 2. Entorno virtual Python y dependencias
echo "--> Creando/verificando entorno virtual de Python..."
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv "$APP_DIR/venv"
fi

echo "--> Instalando dependencias en venv..."
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r backend/requirements.txt

# 3. Inicializar base de datos y datos reales (Bar Los Mayores)
echo "--> Sembrando base de datos con Bar Los Mayores by La Extremeña..."
cd "$APP_DIR/backend"
"$APP_DIR/venv/bin/python" seed_demo_data.py
"$APP_DIR/venv/bin/python" add_bar_los_mayores.py

# 4. Instalar servicio Systemd
echo "--> Registrando servicio systemd (iaexpress)..."
sudo cp "$APP_DIR/deploy/iaexpress.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iaexpress
sudo systemctl restart iaexpress

# 5. Configurar Nginx
echo "--> Configurando Nginx..."
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/express.aedia.es
sudo ln -sf /etc/nginx/sites-available/express.aedia.es /etc/nginx/sites-enabled/

# Si el certificado SSL no existe aún, usar config HTTP de inicio rápido
if [ ! -f "/etc/letsencrypt/live/express.aedia.es/fullchain.pem" ]; then
    echo "--> SSL no detectado aún. Configurando Nginx en modo HTTP (puerto 80)..."
    sudo bash -c 'cat << "EOF" > /etc/nginx/sites-available/express.aedia.es
server {
    listen 80;
    server_name express.aedia.es _;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~* ^/[a-zA-Z0-9]+\.txt$ {
        proxy_pass http://127.0.0.1:8050;
    }
}
EOF'
fi

sudo nginx -t
sudo systemctl reload nginx

echo "=================================================================="
echo "  ¡DESPLIEGUE EN PRODUCCIÓN COMPLETADO CON ÉXITO!                "
echo "  Backend activo en systemd: service iaexpress status            "
echo "  Puerto local: http://127.0.0.1:8050                            "
echo "  Para habilitar HTTPS / SSL con Let's Encrypt ejecuta:          "
echo "  sudo certbot --nginx -d express.aedia.es                      "
echo "=================================================================="

