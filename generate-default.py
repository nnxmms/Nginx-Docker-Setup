# Python 3
import warnings
warnings.filterwarnings('ignore')

import datetime
import subprocess

class Logger():

	def __init__(self, verbose=False):
		"""
		Initialize Logger Object.
		"""
		self.dir = "./nginx-docker.log"
		self.verbose = verbose
	
	def Info(self, log):
		with open(self.dir, "a+") as logfile:
			s = f"{datetime.datetime.now().isoformat()} - [ INFO	] {log}\n"
			logfile.write(s)
		if self.verbose:
			print(s[:-1], flush=True)
	
	def Warning(self, log):
		with open(self.dir, "a+") as logfile:
			s = f"{datetime.datetime.now().isoformat()} - [ WARNING ] {log}\n"
			logfile.write(s)
		if self.verbose:
			print(s[:-1], flush=True)

	def Error(self, log):
		with open(self.dir, "a+") as logfile:
			s = f"{datetime.datetime.now().isoformat()} - [ ERROR   ] {log}\n"
			logfile.write(s)
		if self.verbose:
			print(s[:-1], flush=True)

	def Fatal(self, log):
		with open(self.dir, "a+") as logfile:
			s = f"{datetime.datetime.now().isoformat()} - [ FATAL   ] {log}\n"
			logfile.write(s)
		print(s[:-1], flush=True)
		exit(1)

class SetupAssistent:
	
	def __init__(self, proxy_hosts):
		"""
		Initialize SetupAssistent object.
		"""
		self.proxy_hosts = proxy_hosts
		self.logger = Logger(verbose=True)

		self.nginx_conf = ['user  nginx;\n', 'worker_processes  auto;\n', '\n', 'error_log  /var/log/nginx/error.log notice;\n', 'pid        /var/run/nginx.pid;\n', '\n', '\n', 'events {\n', '    worker_connections  1024;\n', '}\n', '\n', 'http {\n', '    include       /etc/nginx/mime.types;\n', '    default_type  application/octet-stream;\n', '\n', '    log_format  main  \'$remote_addr - $remote_user [$time_local] "$request" \'\n', '                      \'$status $body_bytes_sent "$http_referer" \'\n', '                      \'"$http_user_agent" "$http_x_forwarded_for"\';\n', '\n', '    access_log  /var/log/nginx/access.log  main;\n', '\n', '    sendfile        on;\n', '\n', '    keepalive_timeout  65;\n', '\n', '    include /etc/nginx/conf.d/*.conf;\n', '}']
		self.nginx_default_conf = ['server {\n', '    listen       80;\n', '    listen  [::]:80;\n', '    server_name  localhost;\n', '\n', '    #access_log  /var/log/nginx/host.access.log  main;\n', '\n', '    location / {\n', '        root   /usr/share/nginx/html;\n', '        index  index.html index.htm;\n', '    }\n', '\n', '    #error_page  404              /404.html;\n', '\n', '    # redirect server error pages to the static page /50x.html\n', '    #\n', '    error_page   500 502 503 504  /50x.html;\n', '    location = /50x.html {\n', '        root   /usr/share/nginx/html;\n', '    }\n', '\n', '    # proxy the PHP scripts to Apache listening on 127.0.0.1:80\n', '    #\n', '    #location ~ \\.php$ {\n', '    #    proxy_pass   http://127.0.0.1;\n', '    #}\n', '\n', '    # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000\n', '    #\n', '    #location ~ \\.php$ {\n', '    #    root           html;\n', '    #    fastcgi_pass   127.0.0.1:9000;\n', '    #    fastcgi_index  index.php;\n', '    #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;\n', '    #    include        fastcgi_params;\n', '    #}\n', '\n', "    # deny access to .htaccess files, if Apache's document root\n", "    # concurs with nginx's one\n", '    #\n', '    #location ~ /\\.ht {\n', '    #    deny  all;\n', '    #}\n', '}\n', '\n']
		self.nginx_base_conf = ['server {\n', '    listen 80;\n', '    listen 443 ssl;\n', '\n', '    resolver 127.0.0.11 ipv6=off;\n', '\n', '    server_name __FQDN__;\n', '\n', '\tif ($scheme = http) {\n', '\t\treturn 301 https://$host$request_uri;\n', '\t}\n', '\n', '    ssl_certificate /cert/__CERT__;\n', '    ssl_certificate_key /cert/__KEY__;\n', '\n', '    location / {\n', '        proxy_pass http://__CONTAINER_NAME__:__CONTAINER_PORT__;\n', '        proxy_set_header Host $host;\n', '        proxy_set_header X-Real-IP $remote_addr;\n', '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n', '    }\n', '}']

		self.docker_compose = ['version: "3"\n', '\n', 'services:\n', '  server:\n', '    image: nginx:latest\n', '    volumes:\n', '      - ./nginx.conf:/etc/nginx/nginx.conf\n', '      - ./conf.d/:/etc/nginx/conf.d/\n', '      - ./cert/:/cert/\n', '    ports:\n', '      - 80:80\n', '      - 443:443\n', '    networks:\n', '      - nginx\n', '    restart: always\n', '\n', 'networks:\n', '  nginx:\n', '    external: true']
	
	def setup(self):
		# Create directories
		for d in ["/home/docker-user/nginx/cert/", "/home/docker-user/nginx/conf.d/"]:
			self.logger.Info(f"Create directory {d}")
			subprocess.run(["mkdir", "-p", d])

		# Store nginx default.conf
		self.logger.Info("Store default.conf in /home/docker-user/nginx/conf.d/")
		with open("/home/docker-user/nginx/conf.d/default.conf", "w") as defaultfile:
			for line in self.nginx_default_conf:
				defaultfile.write(line)
		
		# Store nginx.conf
		self.logger.Info("Store nginx.conf in /home/docker-user/nginx/")
		with open("/home/docker-user/nginx/nginx.conf", "w") as cfile:
			for line in self.nginx_conf:
				cfile.write(line)
		
		# Store docker-compose.yaml
		self.logger.Info("Store docker-compose.yaml in /home/docker-user/nginx/")
		with open("/home/docker-user/nginx/docker-compose.yaml", "w") as dfile:
			for line in self.docker_compose:
				dfile.write(line)
		
		# Installing snap
		self.logger.Info("Installing snap and snapd")
		subprocess.call(["apt", "install", "snap", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
		subprocess.call(["apt", "install", "snapd", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

		# Installing certbot
		self.logger.Info("Installing certbot using snap")
		subprocess.call(["snap", "install", "--classic", "certbot"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

		# Issue certificates
		self.logger.Info("Issue certificates")
		for host in self.proxy_hosts:
			subprocess.run(["certbot", "certonly", "--standalone", "-d", host["fqdn"]])
			subprocess.run(["cp", f"/etc/letsencrypt/live/{host['fqdn']}/fullchain.pem", f"/home/docker-user/nginx/cert/{host['cert']}"])
			subprocess.run(["cp", f"/etc/letsencrypt/live/{host['fqdn']}/privkey.pem", f"/home/docker-user/nginx/cert/{host['key']}"])
		
		# Generate nginx config files
		self.logger.Info("Generating nginx config files")
		for host in self.proxy_hosts:
			conf = self.generate_config(host["fqdn"], host["container_name"], host["container_port"], host["cert"], host["key"])
			with open(f"/home/docker-user/nginx/conf.d/{host['container_name'].split('-')[0]}.conf", "w") as cfile:
				cfile.write(conf)
		
		# Change permissions
		self.logger.Info("Set permissions for /home/docker-user/nginx/")
		subprocess.run(["chown", "docker-user:docker-user", f"/home/docker-user/nginx/", "-R"])
		self.logger.Info("Set permissions for /home/docker-user/nginx/cert/")
		subprocess.run(["chmod", "777", f"/home/docker-user/nginx/cert/", "-R"])
		
		# Create nginx docker network
		self.logger.Info("Create nginx docker network")
		subprocess.call(["docker", "network", "create", "nginx"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
	
	def generate_config(self, fqdn, container_name, container_port, cert, key):
		"""
		This function generates the configuration file based on the given information.
		"""
		conf = ""
		for line in self.nginx_base_conf:
			conf += line.replace("__FQDN__", fqdn).replace("__CERT__", cert).replace("__KEY__", key).replace("__CONTAINER_NAME__", container_name).replace("__CONTAINER_PORT__", container_port)
		
		return conf

if __name__ == "__main__":

	proxy_hosts = [
		{"fqdn": "xxx.xxx-xxx.xxx", "container_name": "xxx-xxx-xxx", "container_port": "xxx", "cert": "xxx.crt", "key": "xxx.key", "nginx_conf": "xxx.conf"}
	]
	sa = SetupAssistent(proxy_hosts=proxy_hosts)
	sa.setup()
	