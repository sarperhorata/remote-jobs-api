#!/bin/bash

# Install certbot
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily
docker-compose stop nginx

# Get SSL certificate
certbot certonly --standalone -d buzz2remote.com -d www.buzz2remote.com

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Copy certificates to ssl directory
cp /etc/letsencrypt/live/buzz2remote.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/buzz2remote.com/privkey.pem ssl/

# Start nginx
docker-compose up -d nginx

# Set up auto-renewal
echo "0 0 * * * root certbot renew --quiet && cp /etc/letsencrypt/live/buzz2remote.com/fullchain.pem /app/ssl/ && cp /etc/letsencrypt/live/buzz2remote.com/privkey.pem /app/ssl/ && docker-compose restart nginx" > /etc/cron.d/certbot-renew 