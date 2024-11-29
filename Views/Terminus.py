import streamlit as st
import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO
import tempfile
import os

# Path to your YOLO model
MODEL_PATH = "https://drive.google.com/file/d/1MMNzrExJRw14OZTmcaMRk6dfuCfzsPwi/view?usp=sharing"  # Update this to the path of your .pt model
model = YOLO(MODEL_PATH)  # Load the YOLO model

# Streamlit UI
st.title("Terminus Object Detection")
st.write("Upload an image or video, or use the real-time camera for object detection.")

# Class selection
class_names = list(model.names.values())
selected_classes = st.multiselect("Select classes to detect", class_names, default=class_names)

def filter_results(results, selected_classes):
    """Filter detection results based on selected classes."""
    filtered_boxes = []
    for result in results[0].boxes:
        label = model.names[int(result.cls)]
        if label in selected_classes:
            filtered_boxes.append(result)
    return filtered_boxes

def process_image(image):
    """Process and annotate an image."""
    img_array = np.array(image)
    results = model.predict(img_array)
    filtered_boxes = filter_results(results, selected_classes)

    annotated_image = img_array.copy()
    for result in filtered_boxes:
        box = result.xyxy[0].numpy()
        label = model.names[int(result.cls)]
        confidence = result.conf.numpy()

        x_min, y_min, x_max, y_max = map(int, box)
        cv2.rectangle(annotated_image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(
            annotated_image,
            f"{label}: {confidence[0]:.2f}",
            (x_min, y_min - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )
    return cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

def process_video(video_path, output_path):
    """Process and annotate a video."""
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model.predict(frame)
        filtered_boxes = filter_results(results, selected_classes)

        for result in filtered_boxes:
            box = result.xyxy[0].numpy()
            label = model.names[int(result.cls)]
            confidence = result.conf.numpy()

            x_min, y_min, x_max, y_max = map(int, box)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{label}: {confidence[0]:.2f}",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        if out is None:
            height, width, _ = frame.shape
            out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))
        out.write(frame)

    cap.release()
    out.release()

def run_camera_streamlit(selected_classes):
    """Run real-time detection using the built-in camera and display in Streamlit."""
    cap = cv2.VideoCapture(0)  # Open the default camera
    st_frame = st.empty()  # Placeholder for displaying frames in Streamlit

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO model on the frame
        results = model.predict(frame)
        filtered_boxes = filter_results(results, selected_classes)

        # Annotate the frame
        for result in filtered_boxes:
            box = result.xyxy[0].numpy()
            label = model.names[int(result.cls)]
            confidence = result.conf.numpy()

            x_min, y_min, x_max, y_max = map(int, box)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{label}: {confidence[0]:.2f}",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        # Convert the frame to RGB format (required for Streamlit)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Display the frame in Streamlit
        st_frame.image(frame_rgb, channels="RGB", use_container_width=True)

    cap.release()

# Option for input type
option = st.selectbox("Choose an option", ["Image", "Video", "Real-Time Camera"])

if option == "Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_container_width=True)
        annotated_image = process_image(img)

        st.image(annotated_image, caption="Processed Image with Detections", use_container_width=True)

        # Save and download the annotated image
        annotated_image_pil = Image.fromarray(annotated_image)
        annotated_image_pil.save("annotated_image.jpg")
        with open("annotated_image.jpg", "rb") as file:
            st.download_button(label="Download Annotated Image", data=file, file_name="annotated_image.jpg")

elif option == "Video":
    uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        video_path = tfile.name

        output_video_path = "annotated_video.mp4"
        st.write("Processing video...")
        process_video(video_path, output_video_path)
        st.write("Video processing completed!")

        # Show the processed video
        with open(output_video_path, "rb") as video_file:
            st.video(video_file.read())

        # Save and download the annotated video
        with open(output_video_path, "rb") as video_file:
            st.download_button(label="Download Annotated Video", data=video_file, file_name="annotated_video.mp4")

elif option == "Real-Time Camera":
    st.write("Click the button below to start the camera.")
    if st.button("Start Camera"):
        run_camera_streamlit(selected_classes)
