import torch
import os
from PIL import Image
import sqlite3
from ultralytics import YOLO

# Import SQLite library
# Set up SQLite connection and cursor
conn = sqlite3.connect('annotate.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        num_bounding_boxes INTEGER
    )
''')
conn.commit()

def detect(img_path, save_dir='static/detected_images'):
    os.makedirs(save_dir, exist_ok=True)
    model = YOLO('best.pt')
    results = model.predict(source=img_path, save=False)

    # Filter results with confidence less than 0.5
    filtered_results = results[0].boxes[results[0].boxes.conf >= 0.5]

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

def clear():
    for item in os.listdir('static/detected_images'):
        os.remove(os.path.join('static/detected_images', item))

if __name__ == "__main__":
    img_path, num_bounding_boxes = detect(input("Enter the path: "))
    print(f"Image saved at: {img_path}")
    print(f"Number of bounding boxes: {num_bounding_boxes}")

    # Close the database connection when done
    conn.close()