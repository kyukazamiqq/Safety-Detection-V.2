from flask import Flask, render_template, request, jsonify, send_from_directory, Response, session, redirect, url_for
import os
import cv2
import numpy as np
from PIL import Image
import io
import base64
import json
from datetime import datetime
import uuid
from config import config

# Load configuration
config_name = os.environ.get('FLASK_CONFIG', 'default')
app = Flask(__name__)
app.config.from_object(config[config_name])

# Buat folder jika belum ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Kelas deteksi
CLASSES = app.config['CLASSES']
CLASS_COLORS = app.config['CLASS_COLORS']

# Global variable untuk menyimpan statistik
detection_stats = {
    'total_detections': 0,
    'class_counts': {cls: 0 for cls in CLASSES},
    'recent_detections': []
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_yolo_model():
    """Load YOLO model"""
    try:
        # Import YOLO dari ultralytics
        from ultralytics import YOLO
        model = YOLO(app.config['MODEL_PATH'])
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def detect_objects(image_path, model, confidence_threshold=None):
    """Deteksi objek menggunakan model YOLO"""
    try:
        if confidence_threshold is None:
            confidence_threshold = app.config['CONFIDENCE_THRESHOLD']
        
        results = model(image_path, conf=confidence_threshold, iou=app.config['NMS_THRESHOLD'])
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if class_id < len(CLASSES):
                        class_name = CLASSES[class_id]
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': confidence,
                            'class': class_name
                        })
        
        return detections
    except Exception as e:
        print(f"Error in detection: {e}")
        return []

def draw_detections(image_path, detections, output_path):
    """Gambar bounding box dan label pada gambar"""
    try:
        image = cv2.imread(image_path)
        
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            x1, y1, x2, y2 = bbox
            color = CLASS_COLORS.get(class_name, (0, 255, 255))
            
            # Gambar bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Gambar label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(image, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
            cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        cv2.imwrite(output_path, image)
        return True
    except Exception as e:
        print(f"Error drawing detections: {e}")
        return False

def update_stats(detections):
    """Update statistik deteksi"""
    global detection_stats
    
    detection_stats['total_detections'] += len(detections)
    
    for detection in detections:
        class_name = detection['class']
        if class_name in detection_stats['class_counts']:
            detection_stats['class_counts'][class_name] += 1
    
    # Tambah ke recent detections
    detection_record = {
        'timestamp': datetime.now().isoformat(),
        'detections': detections,
        'total': len(detections)
    }
    detection_stats['recent_detections'].append(detection_record)
    
    # Batasi recent detections
    if len(detection_stats['recent_detections']) > app.config['MAX_RECENT_DETECTIONS']:
        detection_stats['recent_detections'] = detection_stats['recent_detections'][-app.config['MAX_RECENT_DETECTIONS']:]

@app.route('/')
def dashboard():
    """Halaman dashboard utama"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', 
                         classes=CLASSES, 
                         stats=detection_stats,
                         colors=CLASS_COLORS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman login sederhana (frontend) dan set sesi login"""
    if request.method == 'POST':
        # Validasi sederhana: terima jika kedua field diisi
        username = request.form.get('email') or request.form.get('username')
        password = request.form.get('password')
        if username and password:
            session['logged_in'] = True
            session['user'] = username
            return redirect(url_for('dashboard'))
        # Jika gagal, render ulang dengan pesan sederhana (opsional)
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Hapus sesi dan kembali ke login"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint untuk upload dan deteksi gambar"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    confidence_threshold = request.form.get('confidence_threshold', type=float)
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load model dan deteksi
        model = load_yolo_model()
        if model is None:
            return jsonify({'error': 'Failed to load model'}), 500
        
        detections = detect_objects(filepath, model, confidence_threshold)
        
        # Update statistik
        update_stats(detections)
        
        # Gambar detections pada gambar
        result_filename = f"result_{filename}"
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        draw_detections(filepath, detections, result_path)
        
        # Convert gambar ke base64 untuk ditampilkan
        with open(result_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'detections': detections,
            'image': img_data,
            'filename': result_filename,
            'total_detections': len(detections)
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/stats')
def get_stats():
    """Endpoint untuk mendapatkan statistik real-time"""
    return jsonify(detection_stats)

@app.route('/reset', methods=['POST'])
def reset_stats():
    """Endpoint untuk reset statistik"""
    global detection_stats
    
    # Reset statistik ke kondisi awal
    detection_stats = {
        'total_detections': 0,
        'class_counts': {cls: 0 for cls in CLASSES},
        'recent_detections': []
    }
    
    # Hapus semua file di folder uploads dan results
    try:
        import shutil
        # Hapus isi folder uploads
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        # Hapus isi folder results
        for filename in os.listdir(app.config['RESULTS_FOLDER']):
            file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        return jsonify({
            'success': True,
            'message': 'Statistik berhasil direset dan file dibersihkan'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error saat reset: {str(e)}'
        }), 500

@app.route('/results/<filename>')
def get_result(filename):
    """Serve hasil deteksi"""
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

@app.route('/uploads/<filename>')
def get_upload(filename):
    """Serve file upload"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/video-inference', methods=['POST'])
def video_inference():
    """Endpoint untuk video inference"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    video_file = request.files['video']
    confidence_threshold = request.form.get('confidence_threshold', type=float)
    
    if video_file.filename == '':
        return jsonify({'error': 'No selected video'}), 400
    
    # Check if it's a video file
    allowed_video_extensions = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'}
    if not ('.' in video_file.filename and 
            video_file.filename.rsplit('.', 1)[1].lower() in allowed_video_extensions):
        return jsonify({'error': 'Invalid video file type'}), 400
    
    try:
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{video_file.filename}"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(video_path)
        
        # Load model
        model = load_yolo_model()
        if model is None:
            return jsonify({'error': 'Failed to load model'}), 500
        
        # Process video
        output_filename = f"result_{filename}"
        output_path = os.path.join(app.config['RESULTS_FOLDER'], output_filename)
        
        # Process video with YOLO
        results = model(video_path, conf=confidence_threshold or app.config['CONFIDENCE_THRESHOLD'], 
                       iou=app.config['NMS_THRESHOLD'], save=True, project=app.config['RESULTS_FOLDER'])
        
        # Get the output video path
        output_video_path = None
        for result in results:
            if hasattr(result, 'save_dir'):
                output_video_path = os.path.join(result.save_dir, 'result.mp4')
                break
        
        if output_video_path and os.path.exists(output_video_path):
            # Convert video to base64 for preview (first frame)
            import cv2
            cap = cv2.VideoCapture(output_video_path)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Save first frame as image
                preview_path = output_video_path.replace('.mp4', '_preview.jpg')
                cv2.imwrite(preview_path, frame)
                
                with open(preview_path, 'rb') as img_file:
                    preview_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                return jsonify({
                    'success': True,
                    'video_filename': output_filename,
                    'preview': preview_data,
                    'message': 'Video processing completed'
                })
        
        return jsonify({'error': 'Failed to process video'}), 500
        
    except Exception as e:
        print(f"Error in video inference: {e}")
        return jsonify({'error': f'Error processing video: {str(e)}'}), 500

@app.route('/stream')
def stream():
    """Halaman streaming real-time"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('stream.html', classes=CLASSES, colors=CLASS_COLORS)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generate video frames for streaming"""
    # Load model
    model = load_yolo_model()
    if model is None:
        return
    
    # Initialize camera (0 for default camera, or specify camera index)
    camera_index = int(os.environ.get('CAMERA_INDEX', 0))
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run detection on frame
            results = model(frame, conf=app.config['CONFIDENCE_THRESHOLD'], 
                          iou=app.config['NMS_THRESHOLD'])
            
            # Draw detections on frame
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        if class_id < len(CLASSES):
                            class_name = CLASSES[class_id]
                            color = CLASS_COLORS.get(class_name, (0, 255, 255))
                            
                            # Draw bounding box
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                            
                            # Draw label
                            label = f"{class_name}: {confidence:.2f}"
                            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                            cv2.rectangle(frame, (int(x1), int(y1) - label_size[1] - 10), 
                                        (int(x1) + label_size[0], int(y1)), color, -1)
                            cv2.putText(frame, label, (int(x1), int(y1) - 5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    finally:
        cap.release()

if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
