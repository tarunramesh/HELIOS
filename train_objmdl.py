if __name__ == '__main__':
    import torch
    from ultralytics import YOLO

    model = YOLO('yolov8s.pt')
    model.train(data='dataset/data.yaml', epochs=100, batch=16, imgsz=640, device=0)

