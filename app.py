import streamlit as st
from PIL import Image
import sqlite3
import os
from ultralytics import YOLO

# Connect to (or create) a SQLite database
conn = sqlite3.connect('annotate.db')
cursor = conn.cursor()

# Create a table to store image paths and number of bounding boxes if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        num_bounding_boxes INTEGER
    )
''')
conn.commit()

# Function to detect objects in the image using YOLO model
def detect(img_path, save_dir='static/detected_images'):
    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    # Load the YOLO model
    model = YOLO('best.pt')
    
    # Run the detection on the image
    results = model.predict(source=img_path, save=False)

    # Filter results with confidence less than 0.5
    filtered_results = results[0].boxes[results[0].boxes.conf >= 0.5]

    # Save the annotated image
    save_path = os.path.join(save_dir, os.path.basename(img_path))
    annotated_image = results[0].plot()
    Image.fromarray(annotated_image).save(save_path)

    # Calculate the number of bounding boxes
    num_bounding_boxes = len(filtered_results)
    print(f"Number of bounding boxes: {num_bounding_boxes}")  # Debugging statement

    # Insert image path and number of bounding boxes into the database
    cursor.execute("INSERT INTO images (path, num_bounding_boxes) VALUES (?, ?)", (save_path, num_bounding_boxes))
    conn.commit()

    return save_path, num_bounding_boxes

# Function to clear the saved detected images
def clear():
    for item in os.listdir('static/detected_images'):
        os.remove(os.path.join('static/detected_images', item))

# Streamlit application title
st.title("YOLO Image Detection")

# Upload image widget
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# If an image is uploaded
if uploaded_file is not None:
    # Convert the uploaded file to an image
    image = Image.open(uploaded_file)
    
    # Save the image to a temporary location
    temp_image_path = "temp_image.jpg"
    image.save(temp_image_path)

    # Run the detect function on the image
    processed_image, bbox_count = detect(temp_image_path)
    
    # Display the original uploaded image
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    # Display the processed image with bounding boxes
    st.image(processed_image, caption='Processed Image', use_column_width=True)
    
    # Determine if the number of bounding boxes suggests illegal content
    legal = 'likely illegal' if bbox_count > 3 else 'likely legal'
    # Display the number of bounding boxes and legality status
    st.write(f"Number of bounding boxes detected: {bbox_count}\n {legal}")
