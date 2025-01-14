# Nginx Docker

## Setup
Make sure, you are the root user:
```bash
su -
```

Allow HTTP and HTTPS in ufw:
```bash
# HTTP
ufw allow http

# HTTPS
ufw allow https
```

Modify the `proxy_hosts` in the script and execute it:
```bash
python3 generate-default.py
```

Now add all your applications to the `nginx` docker network and start nginx with the following command:
```bash
docker-compose up -d && docker logs -f nginx-server-1
```
