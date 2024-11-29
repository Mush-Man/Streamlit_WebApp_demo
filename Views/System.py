import streamlit as st
import cv2
import tempfile
import os
import numpy as np
from ultralytics import YOLO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3
from PIL import Image
from datetime import datetime

# Load YOLO Models
@st.cache_resource
def load_yolo_models():
    try:
        model_1 = YOLO("https://drive.google.com/file/d/1MMNzrExJRw14OZTmcaMRk6dfuCfzsPwi/view?usp=drive_link")
        model_2 = YOLO("https://drive.google.com/file/d/1-5TdFXe7D4t4ewIqc3lTfFFbKXNn-nlV/view?usp=sharing")
        return model_1, model_2
    except Exception as e:
        st.error(f"Error loading YOLO models: {e}")
        return [], []

model_1, model_2 = load_yolo_models()

# Database Setup
def init_db():
    db_path = "bridge_road_management.db"
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
    with sqlite3.connect("bridge_road_management.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO inventory (name, location, type, built_year, last_inspection) VALUES (?, ?, ?, ?, ?)",
                     (name, location, type_, built_year, None))
        conn.commit()

# Fetch Inventory Records
def fetch_inventory():
    with sqlite3.connect("bridge_road_management.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM inventory")
        return c.fetchall()

# YOLO Detection Function
def detect_defects(image, models, selected_classes):
    if not models:
        st.error("No models selected.")
        return None, []

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

    # Save the annotated image temporarily
    temp_image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
    cv2.imwrite(temp_image_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    return temp_image_path, defects

# Generate PDF Report
def generate_pdf_report(inventory_id, defects, length, width, annotated_image_path):
    inventory = next((record for record in fetch_inventory() if record[0] == inventory_id), None)
    if not inventory:
        st.error("Inventory record not found.")
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add inspection details
    pdf.cell(200, 10, txt="Inspection Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Name: {inventory[1]}", ln=True)
    pdf.cell(200, 10, txt=f"Location: {inventory[2]}", ln=True)
    pdf.cell(200, 10, txt=f"Type: {inventory[3]}", ln=True)
    pdf.cell(200, 10, txt=f"Built Year: {inventory[4]}", ln=True)
    pdf.cell(200, 10, txt=f"Defects Detected: {', '.join(defects)}", ln=True)
    pdf.cell(200, 10, txt=f"Length: {length} meters", ln=True)
    pdf.cell(200, 10, txt=f"Width: {width} meters", ln=True)

    # Add annotated image
    if os.path.exists(annotated_image_path):
        pdf.cell(200, 10, txt="Annotated Image:", ln=True)
        pdf.image(annotated_image_path, x=10, y=None, w=190)

    # Save PDF
    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(pdf_path)
    return pdf_path

# Streamlit App
st.title("Bridge and Road Management System")
menu = ["Add Inventory", "View Inventory", "Condition Inspection"]
choice = st.sidebar.selectbox("Menu", menu)

# Add Inventory
if choice == "Add Inventory":
    st.subheader("Add Bridge or Road to Inventory")
    name = st.text_input("Name")
    location = st.text_input("Location")
    type_ = st.selectbox("Type", ["Bridge", "Road"])
    built_year = st.number_input("Year Built", min_value=1800, max_value=datetime.now().year, step=1)

    if st.button("Add to Inventory"):
        add_inventory(name, location, type_, built_year)
        st.success("Record added to inventory.")

# View Inventory
elif choice == "View Inventory":
    st.subheader("View Inventory Records")
    records = fetch_inventory()
    if records:
        for record in records:
            st.write(f"**ID:** {record[0]}")
            st.write(f"**Name:** {record[1]}")
            st.write(f"**Location:** {record[2]}")
            st.write(f"**Type:** {record[3]}")
            st.write(f"**Year Built:** {record[4]}")
            st.write(f"**Last Inspection:** {record[5]}")
            st.markdown("---")
    else:
        st.warning("No inventory records found.")

# Condition Inspection
elif choice == "Condition Inspection":
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

all_classes = []
if model_1:
  all_classes.extend(model_1.names.values())
if model_2:
  all_classes.extend(model_2.names.values())
all_classes = list(set(all_classes))
selected_classes = st.multiselect("Select Defects to Detect", all_classes)

if inspection_type == "Image Upload":
    uploaded_file = st.file_uploader("Upload Inspection Image", type=["jpg", "jpeg", "png"])
    if uploaded_file and selected_classes and st.button("Inspect Image"):
        image = Image.open(uploaded_file)
        image_np = np.array(image)

        temp_image_path, defects = detect_defects(image_np, models, selected_classes)
        if temp_image_path:
            st.image(temp_image_path, caption="Annotated Image", use_column_width=True)
            pdf_path = generate_pdf_report(inventory_id, defects, length, width, temp_image_path)
            if pdf_path:
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Inspection Report as PDF",
                        data=pdf_file,
                        file_name="inspection_report.pdf",
                        mime="application/pdf",
                    )
