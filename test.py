from ultralytics import YOLO
model = YOLO("yolov8m.pt")
with open("classes.txt", "w") as f:
    for i, name in model.names.items():
        f.write(name + "\n")