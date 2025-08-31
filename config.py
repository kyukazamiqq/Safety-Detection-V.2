import os

class Config:
    """Konfigurasi aplikasi YOLO Safety Detection Dashboard"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    RESULTS_FOLDER = 'results'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Model Configuration
    MODEL_PATH = 'model/best.pt'
    
    # Detection Classes
    CLASSES = ['no helmet', 'no jacket', 'safe', 'unsafe']
    
    # Color mapping for each class (BGR format for OpenCV)
    CLASS_COLORS = {
        'no helmet': (0, 0, 255),      # Merah
        'no jacket': (0, 165, 255),    # Orange
        'safe': (0, 255, 0),           # Hijau
        'unsafe': (255, 0, 255)        # Magenta
    }
    
    # Statistics Configuration
    MAX_RECENT_DETECTIONS = 50
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # GPU Configuration (if available)
    USE_GPU = os.environ.get('USE_GPU', 'True').lower() == 'true'
    
    # Confidence threshold for detections
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 0.5))
    
    # NMS threshold
    NMS_THRESHOLD = float(os.environ.get('NMS_THRESHOLD', 0.4))

class DevelopmentConfig(Config):
    """Konfigurasi untuk development"""
    DEBUG = True

class ProductionConfig(Config):
    """Konfigurasi untuk production"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'

class TestingConfig(Config):
    """Konfigurasi untuk testing"""
    TESTING = True
    DEBUG = True

# Dictionary untuk memilih konfigurasi
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
