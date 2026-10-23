import os
import shutil
from pathlib import Path
import random

def convert_food101_to_yolo():
    """Food-101'i YOLO formatına dönüştür"""
    
    # Seçili 30 yemek
    selected_foods = [
        'hamburger', 'pizza', 'hot_dog', 'french_fries', 'chicken_wings',
        'spaghetti_carbonara', 'spaghetti_bolognese', 'lasagna', 
        'chicken_curry', 'grilled_salmon',
        'sushi', 'ramen', 'fried_rice', 'pad_thai', 'spring_rolls',
        'tacos', 'burrito', 'nachos',
        'caesar_salad', 'greek_salad', 'caprese_salad',
        'onion_rings', 'garlic_bread', 'bruschetta',
        'ice_cream', 'cheesecake', 'chocolate_cake', 'donuts',
        'baklava', 'hummus'
    ]
    
    print(f"📊 {len(selected_foods)} yemek seçildi")
    
    # Çıktı klasörleri
    output_dir = "datasets/food101_yolo"
    for split in ['train', 'val', 'test']:
        Path(f"{output_dir}/{split}/images").mkdir(parents=True, exist_ok=True)
        Path(f"{output_dir}/{split}/labels").mkdir(parents=True, exist_ok=True)
    
    # Her yemek için işlem
    for class_idx, food_name in enumerate(selected_foods):
        print(f"🔄 İşleniyor: {food_name} ({class_idx + 1}/{len(selected_foods)})")
        
        food_dir = f"food-101/images/{food_name}"
        
        if not os.path.exists(food_dir):
            print(f"⚠️ {food_name} bulunamadı, atlanıyor...")
            continue
        
        images = [f for f in os.listdir(food_dir) if f.endswith('.jpg')]
        random.shuffle(images)
        
        # 70% train, 20% val, 10% test
        train_split = int(len(images) * 0.7)
        val_split = int(len(images) * 0.9)
        
        splits = {
            'train': images[:train_split],
            'val': images[train_split:val_split],
            'test': images[val_split:]
        }
        
        for split, split_images in splits.items():
            for img_name in split_images:
                # Görüntüyü kopyala
                src = f"{food_dir}/{img_name}"
                dst = f"{output_dir}/{split}/images/{food_name}_{img_name}"
                shutil.copy2(src, dst)
                
                # Label oluştur
                label_content = f"{class_idx} 0.5 0.5 0.9 0.9\n"
                label_name = img_name.replace('.jpg', '.txt')
                label_path = f"{output_dir}/{split}/labels/{food_name}_{label_name}"
                
                with open(label_path, 'w') as f:
                    f.write(label_content)
        
        print(f"✅ {food_name}: {len(images)} görüntü")
    
    # data.yaml oluştur
    with open(f"{output_dir}/data.yaml", 'w') as f:
        f.write(f"path: {os.path.abspath(output_dir)}\n")
        f.write("train: train/images\n")
        f.write("val: val/images\n")
        f.write("test: test/images\n\n")
        f.write(f"nc: {len(selected_foods)}\n\n")
        f.write("names:\n")
        for i, food in enumerate(selected_foods):
            f.write(f"  {i}: {food}\n")
    
    print("\n" + "="*50)
    print("✅ DÖNÜŞTÜRME TAMAMLANDI!")
    print(f"📁 Konum: {output_dir}/data.yaml")
    print("="*50)

if __name__ == "__main__":
    convert_food101_to_yolo()