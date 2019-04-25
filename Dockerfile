FROM python:3.6

RUN mkdir /var/www

WORKDIR /var/www

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.doubanio.com/simple

WORKDIR /var/www

CMD ["uwsgi","--ini","/var/www/uwsgi.ini"]
