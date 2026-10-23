from ultralytics import YOLO

if __name__ == '__main__':  # ✅ Bu satır ÖNEMLİ!
    model = YOLO("yolov8n.pt")
    
    model.train(
        data='datasets/food101_yolo/data.yaml',
        epochs=50,       # 50 → 30 (daha hızlı)
        imgsz=640,
        batch=16,
        device=0,
        workers=0,       # ✅ 8 → 0 (Windows için)
        project='runs/detect',
        name='food101_model2'  # ✅ Yeni isim (eski hata vermemesi için)
    )
    
    print("✅ Eğitim tamamlandı!")
    print("📁 Model: runs/detect/food101_model2/weights/best.pt")
