# Inroduction

This is a Streamlit app for splitting a video into clips and adding generated with [Riffusion](https://github.com/riffusion/riffusion-hobby) music to one of them. It was created as a test task for [Reface](https://reface.ai/).

# Install

It's recommended to set up virtual Python enviroment: 

```
python -m venv .venv

# windows
.venv\Scritps\activate

# linux/mac
source .venv\bin\activate
```

Install python dependencies:

```
python -m pip install -r requirements.txt
```

Then clone and set up riffusion repository:

```
git clone https://github.com/ThorIgor/riffusion_test_task.git
python -m pip install riffusion_test_task/.
rm -r riffusion_test_task
```

Also, you need to install [ffmpeg](https://www.ffmpeg.org/) and add it to the PATH variable.

# Start app

```
python -m streamlit run app.py
```

# Implemantation notes

* For splitting video into clips I used ffmpeg. Because ffmpeg can't read mp4 files directly as bytes I have to create temporary files. For this, I used tempfile python library. Therefore it's not the most efficient implementation.

* [Riffusion repository](https://github.com/riffusion/riffusion-hobby) is no longer activly maintained (this message was commited when I was working on this project :sweat_smile: ). There are some dependency issues. I resolved only those that were required in this project and created [this repository](https://github.com/ThorIgor/riffusion_test_task).

