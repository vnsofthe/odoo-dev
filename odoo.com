server {
	listen 443 default;
	server_name 10.0.1.43;
	access_log /var/log/nginx/oddo.access.log;
	error_log /var/log/nginx/oddo.error.log;
	ssl on ;
	ssl_certificate /etc/nginx/ssl/server.crt;
	ssl_certificate_key /etc/nginx/ssl/server.key;
	keepalive_timeout 60;
	ssl_ciphers HIGH:!ADH:!MD5;
	ssl_protocols           SSLv3 TLSv1;
	ssl_prefer_server_ciphers on;
	location / {
		proxy_pass http://127.0.0.1:8069;
		proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
		proxy_buffer_size 128k ;
		proxy_buffers 16 64k ;
		proxy_redirect off;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		# proxy_set_header X-Forwarded- For $proxy_add_x_forwarded_for;
		# proxy_set_header X-Forwarded-Proto https;
	}

	location ~*/web/static/{
		proxy_buffering off ;
		proxy_pass http://127.0.0.1:8069;
	}

}

# This allows for someone to go to http and get redirected to https automatically

server {
	listen 80;
	server_name 10.0.1.43;
	add_header Strict-Transport-Security max-age=2592000;
	rewrite ^/.*$ https://$host$request_uri? permanent;
}
