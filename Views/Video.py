import streamlit as st
import cv2
import tempfile
import os
import numpy as np
from ultralytics import YOLO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load YOLO models
model_road = YOLO("https://raw.githubusercontent.com/Mush-Man/Streamlit_WebApp_demo/main/best.pt")
model_bridge = YOLO("https://raw.githubusercontent.com/Mush-Man/Streamlit_WebApp_demo/main/best%20(1).pt")

# Helper Functions
def analyze_video(video_path, model):
    """Analyze a video file using the YOLO model."""
    cap = cv2.VideoCapture(video_path)
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS) or 20  # Default to 20 if FPS is unavailable
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, verbose=False)  # Disable verbose logging
        annotated_frame = results[0].plot() if results else frame  # Annotate if detections exist
        out.write(annotated_frame)

    cap.release()
    out.release()
    return output_path

def analyze_camera_feed(model):
    """Analyze real-time camera feed."""
    st.info("Using real-time camera feed...")
    cap = cv2.VideoCapture(0)  # Default camera

    if not cap.isOpened():
        st.error("Camera not accessible. Check your hardware or permissions.")
        return

    stop_button = st.button("Stop Analysis")
    st_frame = st.empty()

    while cap.isOpened() and not stop_button:
        ret, frame = cap.read()
        if not ret:
            st.warning("No frames received from camera. Stopping analysis.")
            break

        results = model.predict(frame, verbose=False)
        annotated_frame = results[0].plot() if results else frame

        # Display the annotated frame
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        st_frame.image(frame_rgb, channels="RGB")

    cap.release()
    st.success("Camera feed stopped.")

def generate_pdf_report(defects_summary, pdf_path):
    """Generate a PDF report of detected defects."""
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Infrastructure Management System - Defect Report")
    c.drawString(100, 735, "-----------------------------------------------")
    y_position = 700
    for defect in defects_summary:
        c.drawString(100, y_position, defect)
        y_position -= 20
    c.save()

def download_file(file_path, label):
    """Provide a download link for the given file."""
    with open(file_path, "rb") as file:
        btn = st.download_button(
            label=label,
            data=file,
            file_name=os.path.basename(file_path),
            mime="application/octet-stream",
        )
    return btn

# Streamlit UI
st.title("Infrastructure Management System")
st.subheader("Detect structural defects in roads, bridges, and other infrastructure.")

# File upload or real-time camera feed
data_mode = st.radio("Select data source:", ("Upload a video", "Use real-time camera"))

if data_mode == "Upload a video":
    uploaded_file = st.file_uploader("Upload a video file:", type=["mp4", "avi", "mov"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            uploaded_video_path = temp_file.name

        model_choice = st.selectbox("Choose the model to use:", ("Road Defect Model", "Bridge Defect Model"))
        model = model_road if model_choice == "Road Defect Model" else model_bridge

        if st.button("Analyze Video"):
            st.info("Analyzing video. Please wait...")
            with st.spinner('Analyzing...'):
                annotated_video_path = analyze_video(uploaded_video_path, model)
            st.success("Analysis complete! The annotated video is ready.")
            download_file(annotated_video_path, "Download Annotated Video")

elif data_mode == "Use real-time camera":
    model_choice = st.selectbox("Choose the model to use:", ("Road Defect Model", "Bridge Defect Model"))
    model = model_road if model_choice == "Road Defect Model" else model_bridge

    if st.button("Start Camera Analysis"):
        st.info("Initializing camera...")
        analyze_camera_feed(model)

# Generate PDF report
if st.button("Generate Report"):
    st.info("Generating defect report...")
    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

    # Placeholder for defect extraction logic
    defects_summary = ["Defect 1: Crack on road", "Defect 2: Spalling on bridge"]  # Replace with actual data

    generate_pdf_report(defects_summary, pdf_path)
    download_file(pdf_path, "Download PDF Report")
