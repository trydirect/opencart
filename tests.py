#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import docker
import requests

client = docker.from_env()

# Testing Opencart build

time.sleep(20)  # we expect all containers are up and running in 20 secs

for c in client.containers.list():
    print("{}: {}" .format(c.name, c.status))
    if 'running' not in c.status:
        print(c.logs())

# # NGINX
php = client.containers.get('opencart')
php_out = php.exec_run("php-fpm7.1 -t").output.decode()

nginx = client.containers.get('opencart-nginx')
nginx_cfg = nginx.exec_run("/usr/sbin/nginx -T")

assert nginx.status == 'running'
# print(nginx_cfg.output.decode())
# print(nginx.logs())
assert "php-fpm entered RUNNING state" in php.logs()
assert "success: cron entered RUNNING state" in php.logs()
assert "nginx entered RUNNING state" in nginx.logs()
assert 'server_name _;' in nginx_cfg.output.decode()
assert "error_log /proc/self/fd/2" in nginx_cfg.output.decode()
assert 'the configuration file /etc/nginx/nginx.conf syntax is ok' in nginx_cfg.output.decode()
assert 'configuration file /etc/nginx/nginx.conf test is successful' in nginx_cfg.output.decode()
assert 'HTTP/1.1" 500' not in nginx.logs()


db = client.containers.get('opencart-db')
assert db.status == 'running'
cnf = db.exec_run("/usr/sbin/mysqld --verbose  --help")
db_log = db.logs()
# print(db_log)
assert "mysqld: ready for connections" in db_log.decode()
assert "Version: '5.7" in db_log.decode()

# check redirect to web installer
response = requests.get("http://localhost")
# print(response.text)
assert '<base href="http://localhost/install/" />' in response.text
assert 'License agreement' in response.text
