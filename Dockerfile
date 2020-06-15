FROM python
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install mpv -y
RUN pip install -r requirements.txt && rm requirements.txt
CMD ["python3", "./main.py"]