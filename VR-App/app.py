import streamlit as st
import os
import pandas as pd
import edge_tts
import tempfile
from vr_conversion import convert_to_360, create_dual_video, generate_vr_scene
from datetime import datetime
# Import our modules
from llm import generate_narration

from video import process_video

# Set page config
st.set_page_config(page_title="VR Video Narration Generator", layout="wide")

# Create necessary directories
os.makedirs("./Temp", exist_ok=True)
os.makedirs("./Temp/Normal", exist_ok=True)
os.makedirs("./Output", exist_ok=True)

# Initialize session state
if 'timestamp_data' not in st.session_state:
    st.session_state.timestamp_data = []
if 'narration' not in st.session_state:

    st.session_state.narration = ""
if 'processed_video' not in st.session_state:
    st.session_state.processed_video = None
if 'uploaded_video' not in st.session_state:
    st.session_state.uploaded_video = None
if 'voice' not in st.session_state:
    st.session_state.voice = 'en-CA-LiamNeural'
if 'conversion_mode' not in st.session_state:
    st.session_state.conversion_mode = "narration_only"

if 'vr_output' not in st.session_state:
    st.session_state.vr_output = None


def format_timestamp(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temp directory and return path."""
    temp_dir = "./Temp"
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def clear_temp_files():
    """Clear temporary files to save disk space."""
    normal_dir = "./Temp/Normal"
    for file in os.listdir(normal_dir):
        file_path = os.path.join(normal_dir, file)

        if os.path.isfile(file_path):
            os.remove(file_path)

st.title("🎬 VR Video Narration Generator")

# Sidebar for navigation and settings
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select Page", ["Admin Panel", "Preview"])
    
    st.header("TTS Settings")
    # Get available voices
    async def get_voices():
        return await edge_tts.list_voices()

    
    # Use cached voices if available

    if 'available_voices' not in st.session_state:
        try:

            import asyncio
            voices = asyncio.run(get_voices())
            english_voices = [v["Name"] for v in voices if v["Locale"].startswith("en")]
            st.session_state.available_voices = english_voices
        except Exception:
            st.session_state.available_voices = ["en-CA-LiamNeural", "en-GB-RyanNeural", "en-GB-LibbyNeural"]
    
    voice = st.selectbox(
        "Select Voice", 
        st.session_state.available_voices,
        index=st.session_state.available_voices.index(st.session_state.voice) 
        if st.session_state.voice in st.session_state.available_voices else 0
    )
    
    if voice != st.session_state.voice:
        st.session_state.voice = voice

    st.header("VR Settings")
    conversion_mode = st.radio(
        "Video Processing Mode",
        ["Narration Only", "Convert to YouTube 360°"],

        index=0
    )
    
    if conversion_mode == "Convert to YouTube 360°":

        st.session_state.conversion_mode = "convert_360"
        st.info("Videos will be converted to YouTube-compatible 360° format using equirectangular projection.")
    

    # YouTube recommended resolutions
        resolution_options = {
            "2.5K (2560×1280)": "2.5K",
            "4K (3840×1920)": "4K",

        }
        selected_resolution = st.selectbox(
            "Resolution",
            list(resolution_options.keys()),

            index=1  # Default to 4K
        )
        st.session_state.resolution = resolution_options[selected_resolution]
    
        fov = st.slider("Field of View (degrees)", min_value=90, max_value=180, value=180, step=10)
        st.session_state.fov = fov
    
        st.markdown("""
        ### YouTube 360° Video Requirements
        - **Format**: MP4 with H.264 video codec
        - **Audio**: AAC codec, stereo recommended
        - **Metadata**: Spatial metadata for 360° playback
        - **Resolution**: 4K (3840×1920) recommended for best quality

        """)
    else:

        st.session_state.conversion_mode = "narration_only"

if page == "Admin Panel":
    st.header("Admin Panel")
    
    # Video upload section
    st.subheader("Upload VR Video")

    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])

    
    if uploaded_file and uploaded_file != st.session_state.uploaded_video:
        st.session_state.uploaded_video = uploaded_file
        video_path = save_uploaded_file(uploaded_file)
        st.session_state.video_path = video_path
        st.video(video_path)
        st.success(f"Video uploaded: {uploaded_file.name}")
        

        # Reset state
        st.session_state.timestamp_data = []
        st.session_state.narration = ""
        st.session_state.processed_video = None
        

        # Clear temp files
        clear_temp_files()

    
    # Background music upload (optional)
    st.subheader("Upload Background Music (Optional)")
    bg_music = st.file_uploader("Choose background music", type=["mp3", "wav", "ogg"])
    
    if bg_music:
        bg_music_path = save_uploaded_file(bg_music)
        st.session_state.bg_music_path = bg_music_path
        st.audio(bg_music_path)
    else:
        st.session_state.bg_music_path = None
    
    # Timestamp editor

    st.subheader("Add Timestamped Descriptions")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        minutes = st.number_input("Minutes", min_value=0, max_value=59, step=1)
        seconds = st.number_input("Seconds", min_value=0, max_value=59, step=1)
        total_seconds = minutes * 60 + seconds
        timestamp = format_timestamp(total_seconds)
        st.text(f"Timestamp: {timestamp}")
    
    with col2:
        description = st.text_area("Description", height=100, 
                                  placeholder="E.g., The red panda slowly climbs down the tree, showcasing its remarkable agility in the dense bamboo forest.")

    
    with col3:
        if st.button("Add Timestamp"):
            if description:

                st.session_state.timestamp_data.append((timestamp, description))
                st.success(f"Added timestamp: {timestamp}")
    
    # Display and edit timestamps
    if st.session_state.timestamp_data:
        st.subheader("Timestamped Descriptions")
        
        # Convert to DataFrame for display
        df = pd.DataFrame(st.session_state.timestamp_data, columns=["Timestamp", "Description"])
        
        # Display as editable table

        edited_df = st.data_editor(df)
        

        # Update session state if data was edited
        if not df.equals(edited_df):
            st.session_state.timestamp_data = list(edited_df.itertuples(index=False, name=None))
        

        # Delete selected timestamps
        if st.button("Delete Selected Timestamps"):
            edited_df = edited_df.loc[~edited_df.index.isin(st.session_state.selected_rows)]
            st.session_state.timestamp_data = list(edited_df.itertuples(index=False, name=None))
            st.experimental_rerun()
        
        # Generate narration button
        if st.button("Generate David Attenborough Style Narration"):
            with st.spinner("Generating narration..."):
                try:
                    narration = generate_narration(st.session_state.timestamp_data)
                    st.session_state.narration = narration

                    st.success("Narration generated!")
                except Exception as e:
                    st.error(f"Error generating narration: {str(e)}")
    
    # Display and edit generated narration
    if st.session_state.narration:
        st.subheader("Generated Narration")
        narration = st.text_area("Edit narration if needed:", st.session_state.narration, height=300)
        

        # Update narration if edited
        if narration != st.session_state.narration:
            st.session_state.narration = narration

        
        # Process video button
        if st.button("Process Video with Narration"):
            if hasattr(st.session_state, 'video_path'):
                with st.spinner("Processing video... This may take a while."):
                    try:
                # Clear temp files first
                        clear_temp_files()
                
                # Update the audio.py module's voice setting
                        import audio
                        audio.voice = st.session_state.voice
                
                # Process based on selected mode
                        if st.session_state.conversion_mode == "narration_only":
                    # Original processing
                            processed_video = process_video(
                                st.session_state.video_path,
                                st.session_state.narration,
                                st.session_state.bg_music_path
                            )
                            st.session_state.processed_video = processed_video
                
                        elif st.session_state.conversion_mode == "convert_360":
                    # First add narration
                            narrated_video = process_video(
                                st.session_state.video_path,
                                st.session_state.narration,
                                st.session_state.bg_music_path
                            )
                    
                    # Then convert to YouTube 360
                            with st.spinner("Converting to YouTube 360° format..."):
                                vr_video = convert_to_360(
                                    narrated_video,
                                    projection_type="equirectangular",
                                    fov=st.session_state.fov
                                )
                                st.session_state.processed_video = vr_video
                
                        st.success("Video processed successfully!")
                
                # Show preview

                        st.subheader("Preview")
                        st.video(st.session_state.processed_video)

                
                        if st.session_state.conversion_mode == "convert_360":
                            st.info("Your video is now ready for YouTube 360° upload. When uploading to YouTube, be sure to check the '360° Video' option in the Advanced Settings.")
                    except Exception as e:
                        st.error(f"Error processing video: {str(e)}")
            else:
                st.warning("Please upload a video first.")

elif page == "Preview":
    st.header("Video Preview")
    
    if st.session_state.processed_video and os.path.exists(st.session_state.processed_video):
        # Determine if this is a 360 video
        is_360_video = False
        if st.session_state.conversion_mode == "convert_360":
            is_360_video = True

        
        # Standard video player
        st.video(st.session_state.processed_video)

        
        # YouTube 360 upload instructions
        if is_360_video:

            st.subheader("YouTube 360° Upload Instructions")
            st.info("Your video has been prepared for YouTube 360° playback.")
            
            st.markdown("""
            ### How to Upload to YouTube as 360° Video
            

            1. **Log in** to your YouTube account
            2. Click **Create** > **Upload Video**
            3. **Select** your processed 360° video file
            4. Fill in **title, description, and other details**
            5. Click **NEXT** until you reach the **Advanced Settings**
            6. Under **Advanced Settings**, check the box for **"This video is 360°"**
            7. Complete the upload process
            
            YouTube will automatically detect the 360° metadata, but checking the box ensures proper processing.
            """)
        
        # Display narration text
        if st.session_state.narration:
            st.subheader("Narration Text")
            st.text_area("", st.session_state.narration, height=200, disabled=True)
        
        # Add VR testing options expander with focus on YouTube
        with st.expander("YouTube 360° Viewing Guidelines"):
            st.markdown("""
            ### How to View Your YouTube 360° Video
            
            #### Desktop
            - Use the **YouTube player** in Chrome, Firefox, MS Edge, or Opera
            - Click and drag to look around or use WASD keys
            
            #### Mobile
            - Use the **YouTube app** on iOS or Android

            - Move your phone to look around or use finger to pan
            
            #### VR Headsets
            - Open the **YouTube VR app** on your headset
            - For Meta Quest, PSVR, or other headsets, find your video and enjoy the immersive experience
            
            YouTube offers the most reliable and widely compatible way to share 360° videos across all devices.
            """)
        
        # Download button with proper metadata
        with open(st.session_state.processed_video, "rb") as file:
            file_extension = os.path.splitext(st.session_state.processed_video)[1]

            download_filename = f"{'YT360_' if is_360_video else ''}narrated_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            

            st.download_button(
                label="Download Processed Video",
                data=file,
                file_name=download_filename,
                mime="video/mp4" if file_extension.lower() == ".mp4" else "video/quicktime"
            )
# Footer

st.markdown("---")
st.caption("VR Video Narration Generator © 2025")
