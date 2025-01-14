#!/bin/bash

# Ask for the domain
echo -n "[      FQDN       ] " 
read DOMAIN

# Ask for the filename
echo -n "[ Target Filename ] " 
read FILENAME

# Stop the running nginx server
cd /home/docker-user/nginx
docker compose down

# Create a temp directory
CERTBOT_DIR=$(xxd -l 16 -c 16 -p < /dev/random)
mkdir /tmp/$CERTBOT_DIR/

# Run certbot
certbot certonly --force-renew --config-dir /tmp/$CERTBOT_DIR/ -d $DOMAIN

# Move the generated certificates
cp /tmp/$CERTBOT_DIR/live/$DOMAIN/fullchain.pem /home/docker-user/nginx/cert/$FILENAME.crt
cp /tmp/$CERTBOT_DIR/live/$DOMAIN/privkey.pem /home/docker-user/nginx/cert/$FILENAME.key

# Change permissions
chmod 777 /home/docker-user/nginx/cert/$FILENAME.crt
chmod 777 /home/docker-user/nginx/cert/$FILENAME.key

# Start the nginx server again
cd /home/docker-user/nginx
docker compose up -d
