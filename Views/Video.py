import streamlit as st
import cv2
import tempfile
import numpy as np
from ultralytics import YOLO

# Load YOLO models
model_road = YOLO("https://raw.githubusercontent.com/Mush-Man/Streamlit_WebApp_demo/main/best.pt")
model_bridge = YOLO("https://raw.githubusercontent.com/Mush-Man/Streamlit_WebApp_demo/main/best%20(1).pt")

# Helper Functions
def analyze_camera_feed(model, camera_url=None):
    """
    Analyze real-time camera feed.
    Supports both local webcam and external camera (e.g., mobile camera via URL).
    """
    st_frame = st.empty()

    # Open default webcam or an external camera
    cap = cv2.VideoCapture(camera_url if camera_url else 0)

    if not cap.isOpened():
        st.error("Camera not accessible. Please check permissions or camera availability.")
        return

    stop_button = st.button("Stop Analysis")

    while cap.isOpened() and not stop_button:
        ret, frame = cap.read()
        if not ret:
            st.warning("No frames received from camera. Stopping analysis.")
            break

        # Run YOLO model
        results = model.predict(frame, verbose=False)
        annotated_frame = results[0].plot() if results else frame

        # Convert frame for Streamlit display
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        st_frame.image(frame_rgb, channels="RGB", use_container_width=True)

    cap.release()
    st.success("Camera feed stopped.")

# Streamlit UI
st.title("Real-Time Defect Detection System")
st.subheader("Analyze structural defects using real-time camera or video uploads.")

# Input Source Selection
source_choice = st.radio("Select Input Source:", ["Real-Time Camera", "Video Upload"])

# Model Selection
model_choice = st.selectbox("Select the Model to Use:", ["Road Defect Model", "Bridge Defect Model"])
model = model_road if model_choice == "Road Defect Model" else model_bridge

# Real-Time Camera Option
if source_choice == "Real-Time Camera":
    st.info("Use the webcam or an external camera for real-time detection.")
    camera_url = st.text_input("Enter Camera URL (leave blank for local webcam):", "")
    
    if st.button("Start Real-Time Analysis"):
        analyze_camera_feed(model, camera_url)

# Video Upload Option
elif source_choice == "Video Upload":
    uploaded_video = st.file_uploader("Upload a Video File:", type=["mp4", "avi", "mov"])
    
    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(uploaded_video.read())
            video_path = temp_video.name

        st.info("Analyzing the uploaded video. Please wait...")

        # Analyze the video file
        cap = cv2.VideoCapture(video_path)
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            results = model.predict(frame, verbose=False)
            annotated_frame = results[0].plot() if results else frame
            out.write(annotated_frame)

        cap.release()
        out.release()

        st.success("Video analysis completed!")
        with open(output_path, "rb") as video_file:
            st.video(video_file.read())
            st.download_button("Download Annotated Video", data=video_file, file_name="annotated_video.mp4")
