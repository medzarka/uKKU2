#!/bin/bash
sudo systemctl stop gunicorn
sudo systemctl stop nginx
sudo systemctl start gunicorn
sudo systemctl start nginx