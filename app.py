import streamlit as st
st.set_page_config(layout="wide")
import numpy as np
import io

import typing as T

from riffusion.spectrogram_params import SpectrogramParams
from riffusion.streamlit import util as streamlit_util

from utils.create_clips import get_video_duration, split_video, add_audio_to_clip, create_zip_from_bytes

with st.sidebar:
    device = streamlit_util.select_device(st.sidebar)
    checkpoint = streamlit_util.select_checkpoint(st.sidebar)
    num_inference_steps = T.cast(int, st.number_input("Inference steps", value=30))
    guidance = st.number_input(
        "Guidance", value=7.0, help="How much the model listens to the text prompt"
    )
    scheduler = st.selectbox(
        "Scheduler",
        options=streamlit_util.SCHEDULER_OPTIONS,
        index=0,
        help="Which diffusion scheduler to use",
    )

cols = st.columns([0.3, 0.3, 0.4])

cols[0].write("<h2>Video</h2>", unsafe_allow_html=True)
uploaded_file = cols[0].file_uploader("Upload a video", type=("mp4", "webm", "mkv"))
clip_count = cols[0].number_input("Clips count", min_value=1)
create_clip = cols[0].button("Create clips", disabled = not uploaded_file)

if 'clip_with_music' not in st.session_state:
    st.session_state['clip_with_music'] = 1
if clip_count < st.session_state['clip_with_music']:
    st.session_state['clip_with_music'] = clip_count

cols[1].write("<h2>Audio</h2>", unsafe_allow_html=True)
prompt = cols[1].text_area("Prompt", placeholder="Cool sound")
neg_prompt = cols[1].text_area("Negative Prompt", placeholder="Terrible sound")
clip_with_music = cols[1].selectbox("Clip to add generated music", [i+1 for i in range(clip_count)], index = st.session_state['clip_with_music']-1)
columns_out = cols[1].number_input("Output columns", min_value=1, max_value=10, value = 3)

st.session_state['clip_with_music'] = clip_with_music


cols[2].write("<h2>Output</h2>", unsafe_allow_html=True)
out_cols = cols[2].columns(columns_out)
if create_clip or 'create_clip' in st.session_state:
    st.session_state['create_clip'] = False

    if create_clip:
        st.session_state['create_clip'] = True
        extension = uploaded_file.name.split(".")[-1]
        uploaded_file = uploaded_file.getvalue()

        width = int(get_video_duration(uploaded_file)*100/clip_count)
        width = width - width%8 + 8

        image = streamlit_util.run_txt2img(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance=guidance,
            negative_prompt=neg_prompt,
            seed=np.random.randint(low = 0, high=1000),
            width=width,
            height=512,
            checkpoint=checkpoint,
            device=device,
            scheduler=scheduler,
        )

        params = SpectrogramParams(
            min_frequency=0,
            max_frequency=10000,
            stereo=False,
        )

        segment = streamlit_util.audio_segment_from_spectrogram_image(
            image=image,
            params=params,
            device=device,
        )

        audio_bytes = io.BytesIO()
        segment.export(audio_bytes, format="mp3")

        if clip_count > 1:
            clips = split_video(uploaded_file, extension, clip_count)
        else:
            clips = [uploaded_file]


        clips[clip_with_music-1] = add_audio_to_clip(clips[clip_with_music-1], audio_bytes.read())
        st.session_state['clips'] = clips

    if 'clips' in st.seesion_state:
        
        for i, clip in enumerate(st.session_state['clips']):
            out_cols[i%columns_out].video(clip, format="video/mp4")
        
        cols[2].download_button(
            "clips.zip",
            data=create_zip_from_bytes(st.session_state['clips']),
            file_name="clips.zip",
            mime="application/zip",
        )

