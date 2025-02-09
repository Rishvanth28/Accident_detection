import os
import cv2
import subprocess
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from ultralytics import YOLO

def convert_to_mp4(input_path):
    """
    Converts the processed video to MP4 format using FFmpeg.
    """
    output_path = input_path.rsplit(".", 1)[0] + ".mp4"  # Ensure MP4 format
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k", output_path
    ]
    
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return output_path  # Return the converted MP4 file path

def upload_video(request):
    if request.method == "POST" and request.FILES.get("video"):
        file_obj = request.FILES["video"]

        # ✅ Save uploaded video in media folder
        fs = FileSystemStorage(location="media/")
        saved_path = fs.save(file_obj.name, file_obj)
        saved_path = fs.path(saved_path)
        print(f"✅ Uploaded file saved at: {saved_path}")

        # Load YOLO model
        model_path = "D:\\Road Safety Hackathon\\Accident-prediction.pt"
        yolo = YOLO(model_path)

        # Process video
        videoCap = cv2.VideoCapture(saved_path)
        frame_width = int(videoCap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(videoCap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(videoCap.get(cv2.CAP_PROP_FPS))

        # ✅ Save processed video
        processed_filename = f"processed_{os.path.splitext(file_obj.name)[0]}.avi"  # Save as AVI first
        output_path = os.path.join("media/", processed_filename)
        print(f"📂 Processed video will be saved at: {output_path}")

        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Save as AVI initially
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        frame_count = 0
        while True:
            ret, frame = videoCap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 4 != 0:  # Skip frames for faster processing
                continue

            results = yolo.track(frame)

            for result in results:
                for box in result.boxes:
                    if box.conf[0] > 0.4:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        color = (0, 255, 0)  # Green color
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        label = f"{result.names[int(box.cls[0])]} {box.conf[0]:.2f}"
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            out.write(frame)

        videoCap.release()
        out.release()

        print(f"🎥 Processed video stored at: {output_path}")

        # ✅ Convert to MP4
        mp4_output_path = convert_to_mp4(output_path)

        # Render HTML template with processed video URL
        return render(request, "index.html", {"processed_video_url": f"/media/{os.path.basename(mp4_output_path)}"})

    return render(request, "index.html")
