FROM python:3.12.2-slim

WORKDIR /app

COPY assets/base64_imgs/ /app/assets/base64_imgs
COPY assets/imgs/ /app/assets/imgs
COPY database.py /app
COPY main.py /app
COPY vectorize.py /app

COPY run.sh /app/run.sh

COPY requirements.txt /app

RUN pip3 install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# make sure the 'imgs' directory exists
RUN mkdir -p /app/assets/imgs

RUN chmod +x /app/run.sh

EXPOSE 5000

ENTRYPOINT ["/app/run.sh"]