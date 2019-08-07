FROM python:3.6

RUN apt update && apt install -y --no-install-recommends \
    vim \
    libsndfile1

RUN mkdir /var/FaceCatch

WORKDIR /var/FaceCatch

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.doubanio.com/simple

WORKDIR /var/FaceCatch/

CMD ["python","-m","app"]
