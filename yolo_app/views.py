import os
import cv2
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from ultralytics import YOLO

# Load YOLO Model once
model_path = "D:\\Road Safety Hackathon\\Accident-prediction.pt"
yolo = YOLO(model_path)

def process_video_stream(video_path):
    """
    Process the video and stream frames in real-time.
    """
    videoCap = cv2.VideoCapture(video_path)

    while videoCap.isOpened():
        ret, frame = videoCap.read()
        if not ret:
            break

        results = yolo.track(frame)

        for result in results:
            for box in result.boxes:
                if box.conf[0] > 0.4:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    color = (0, 255, 0)  # Green color
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    label = f"{result.names[int(box.cls[0])]} {box.conf[0]:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Convert frame to JPEG
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        # Yield frame as multipart response
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    videoCap.release()

def stream_video(request, filename):
    """
    Django view to stream the processed video frames.
    """
    video_path = os.path.join("media", filename)
    return StreamingHttpResponse(process_video_stream(video_path), content_type="multipart/x-mixed-replace; boundary=frame")

def upload_video(request):
    """
    Handle video upload and return a streaming endpoint.
    """
    if request.method == "POST" and request.FILES.get("video"):
        file_obj = request.FILES["video"]

        # ✅ Save uploaded video in media folder
        fs = FileSystemStorage(location="media/")
        saved_path = fs.save(file_obj.name, file_obj)
        saved_path = fs.path(saved_path)
        print(f"✅ Uploaded file saved at: {saved_path}")

        # ✅ Return live stream URL instead of waiting for processing
        return render(request, "index.html", {"stream_url": f"/stream/{file_obj.name}"})

    return render(request, "index.html")
