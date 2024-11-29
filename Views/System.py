import streamlit as st
import cv2
import tempfile
import os
import numpy as np
from ultralytics import YOLO
from fpdf import FPDF
import sqlite3
from PIL import Image
from datetime import datetime

# Load YOLO Models
@st.cache_resource
def load_yolo_models():
    try:
        model_1 = YOLO("https://drive.google.com/uc?id=1MMNzrExJRw14OZTmcaMRk6dfuCfzsPwi&export=download")
        model_2 = YOLO("https://drive.google.com/uc?id=1-5TdFXe7D4t4ewIqc3lTfFFbKXNn-nlV&export=download")
        model_1 = YOLO(model_1_path)
        model_2 = YOLO(model_2_path)
        return model_1, model_2
    except Exception as e:
        st.error(f"Error loading YOLO models: {e}")
        return None, None

model_1, model_2 = load_yolo_models()

if not (model_1 and model_2):
    st.error("Failed to load YOLO models. Please check the paths or environment.")
    st.stop()

# Database Setup
def init_db():
    db_path = os.path.join(tempfile.gettempdir(), "bridge_road_management.db")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        location TEXT,
                        type TEXT,
                        built_year INTEGER,
                        last_inspection TEXT
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS inspections (
                        id INTEGER PRIMARY KEY,
                        inventory_id INTEGER,
                        date TEXT,
                        defects TEXT,
                        severity TEXT,
                        length REAL,
                        width REAL,
                        image_path TEXT,
                        FOREIGN KEY (inventory_id) REFERENCES inventory (id)
                     )''')
        conn.commit()

init_db()

# Add Inventory Record
def add_inventory(name, location, type_, built_year):
    db_path = os.path.join(tempfile.gettempdir(), "bridge_road_management.db")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO inventory (name, location, type, built_year, last_inspection) VALUES (?, ?, ?, ?, ?)",
                  (name, location, type_, built_year, None))
        conn.commit()

# Fetch Inventory Records
def fetch_inventory():
    db_path = os.path.join(tempfile.gettempdir(), "bridge_road_management.db")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM inventory")
        return c.fetchall()

# YOLO Detection Function
def detect_defects(image, models, selected_classes):
    defects = []
    annotated_image = image.copy()

    for model in models:
        results = model(image)
        detections = results[0].boxes.data.cpu().numpy()
        class_names = model.names

        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection
            cls_name = class_names.get(int(cls), "Unknown")
            if cls_name in selected_classes:
                label = f"{cls_name} ({conf:.2f})"
                defects.append(cls_name)
                cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(annotated_image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    temp_image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
    cv2.imwrite(temp_image_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    return temp_image_path, defects

# Streamlit App
st.title("Bridge and Road Management System")
menu = ["Add Inventory", "View Inventory", "Condition Inspection"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Condition Inspection":
    st.subheader("Condition Inspection")
    inventory_id = st.number_input("Enter Inventory ID for Inspection", min_value=1, step=1)

    inspection_type = st.selectbox("Inspection Type", ["Image Upload"])
    model_choice = st.multiselect("Select Models", ["Model 1", "Model 2"])
    length = st.number_input("Enter Length (meters):", min_value=0.0, step=0.1)
    width = st.number_input("Enter Width (meters):", min_value=0.0, step=0.1)

    models = []
    if "Model 1" in model_choice:
        models.append(model_1)
    if "Model 2" in model_choice:
        models.append(model_2)

    all_classes = list(set(model_1.names.values()).union(set(model_2.names.values())))
    selected_classes = st.multiselect("Select Defects to Detect", all_classes)

    if inspection_type == "Image Upload":
        uploaded_file = st.file_uploader("Upload Inspection Image", type=["jpg", "jpeg", "png"])
        if uploaded_file and selected_classes and st.button("Inspect Image"):
            image = Image.open(uploaded_file)
            image_np = np.array(image)

            temp_image_path, defects = detect_defects(image_np, models, selected_classes)
            if temp_image_path:
                st.image(temp_image_path, caption="Annotated Image", use_column_width=True)


