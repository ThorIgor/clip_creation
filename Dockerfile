FROM python:3.9

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y ffmpeg

RUN git clone https://github.com/ThorIgor/riffusion_test_task.git
RUN python -m pip install --timeout 2000 riffusion_test_task/.
RUN rm -r riffusion_test_task

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py"]