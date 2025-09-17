import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
import os
from pathlib import Path

st.set_page_config(page_title="Video → MP3", page_icon="🎧")
st.title("🎧 Convert video (.mov, .mp4, …) to MP3")

uploaded = st.file_uploader(
    "Upload a video file",
    type=["mov", "mp4", "m4v", "avi", "mkv"],
    accept_multiple_files=False
)

bitrate = st.selectbox("MP3 bitrate", ["320k", "192k", "128k"], index=1)

if uploaded:
    st.video(uploaded)

    if st.button("Convert to MP3"):
        with st.spinner("Extracting audio…"):
            # 1) Save uploaded file to a temp path
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded.name}") as tmp_in:
                tmp_in.write(uploaded.read())
                in_path = tmp_in.name

            # 2) Set mp3 output temp path
            safe_stem = Path(uploaded.name).stem.replace(" ", "_")
            out_path = os.path.join(tempfile.gettempdir(), f"{safe_stem}.mp3")

            clip = None
            try:
                clip = VideoFileClip(in_path)
                if clip.audio is None:
                    st.error("No audio track found in this video.")
                else:
                    # write_audiofile uses ffmpeg (bundled by imageio-ffmpeg)
                    clip.audio.write_audiofile(out_path, bitrate=bitrate, logger=None)
                    with open(out_path, "rb") as f:
                        st.success("Done! Download your MP3 below 👇")
                        st.download_button(
                            label=f"Download {safe_stem}.mp3",
                            data=f,
                            file_name=f"{safe_stem}.mp3",
                            mime="audio/mpeg",
                        )
            except Exception as e:
                st.error(f"Conversion failed: {e}")
            finally:
                # Clean up resources and temp files
                try:
                    if clip: clip.close()
                except:
                    pass
                for p in [in_path, out_path]:
                    try:
                        if os.path.exists(p):
                            os.remove(p)
                    except:
                        pass

st.caption("Powered by Streamlit + MoviePy (ffmpeg).")