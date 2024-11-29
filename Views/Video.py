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
    cap = cv2.VideoCapture(video_path)
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        if len(results) > 0:  # Check if any detections were found
            annotated_frame = results[0].plot()  # Use the plot() method
            out.write(annotated_frame)
        else:
            # Handle the case where no detections were found
            st.info("No defects detected in this frame.")

    cap.release()
    out.release()
    return output_path

def analyze_camera_feed(model):
    st.info("Using real-time camera feed...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Camera not accessible.")
        return None

    stop_button = st.button("Stop Analysis", key="stop_analysis_button")  # Add unique key

    while not stop_button:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        if len(results) > 0:
            annotated_frame = results[0].plot()
        else:
            annotated_frame = frame  # Display original frame if no detections

        # Display the live frame
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, channels="RGB", use_container_width=True)

    cap.release()
    return True

def generate_pdf_report(defects_summary, pdf_path):
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
        if analyze_camera_feed(model):
            st.success("Camera feed analyzed successfully!")

# Generate PDF report
if st.button("Generate Report"):
    st.info("Generating defect report...")
    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

    # **Implement logic to extract defect information from model output**
    defects_summary = ["Defect 1: Example", "Defect 2: Example"]  # Replace with actual defects

    generate_pdf_report(defects_summary, pdf_path)
    download_file(pdf_path, "Download PDF Report")
