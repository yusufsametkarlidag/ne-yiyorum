# nutrition_db.py
"""
Besin değerleri veritabanı
Her yemeğin base_amount'u kendi gerçek porsiyon ağırlığıdır
"""

NUTRITION_DATA = {
    'hamburger': {
        'name': 'Hamburger',
        'calories': 295,
        'protein': 17,
        'carbs': 24,
        'fat': 14,
        'fiber': 1.5,
        'portion_size': '1 adet (150g)',
        'emoji': '🍔',
        'category': 'Fast Food',
        'base_amount': 150  # Veriler 150g için
    },
    'pizza': {
        'name': 'Pizza',
        'calories': 266,
        'protein': 11,
        'carbs': 33,
        'fat': 10,
        'fiber': 2.5,
        'portion_size': '1 dilim (100g)',
        'emoji': '🍕',
        'category': 'Fast Food',
        'base_amount': 100
    },
    'hot_dog': {
        'name': 'Hot Dog',
        'calories': 290,
        'protein': 10,
        'carbs': 24,
        'fat': 17,
        'fiber': 1,
        'portion_size': '1 adet (100g)',
        'emoji': '🌭',
        'category': 'Fast Food',
        'base_amount': 100
    },
    'french_fries': {
        'name': 'French Fries',
        'calories': 312,
        'protein': 3.4,
        'carbs': 41,
        'fat': 15,
        'fiber': 3.8,
        'portion_size': '1 porsiyon (100g)',
        'emoji': '🍟',
        'category': 'Fast Food',
        'base_amount': 100
    },
    'chicken_wings': {
        'name': 'Chicken Wings',
        'calories': 290,
        'protein': 27,
        'carbs': 0,
        'fat': 19,
        'fiber': 0,
        'portion_size': '100g',
        'emoji': '🍗',
        'category': 'Protein',
        'base_amount': 100
    },
    'spaghetti_carbonara': {
        'name': 'Spaghetti Carbonara',
        'calories': 350,
        'protein': 13,
        'carbs': 47,
        'fat': 12,
        'fiber': 2,
        'portion_size': '1 porsiyon (200g)',
        'emoji': '🍝',
        'category': 'Italian',
        'base_amount': 200
    },
    'spaghetti_bolognese': {
        'name': 'Spaghetti Bolognese',
        'calories': 320,
        'protein': 14,
        'carbs': 48,
        'fat': 8,
        'fiber': 4,
        'portion_size': '1 porsiyon (200g)',
        'emoji': '🍝',
        'category': 'Italian',
        'base_amount': 200
    },
    'lasagna': {
        'name': 'Lasagna',
        'calories': 203,
        'protein': 12,
        'carbs': 21,
        'fat': 7.5,
        'fiber': 3,
        'portion_size': '1 dilim (150g)',
        'emoji': '🍝',
        'category': 'Italian',
        'base_amount': 150
    },
    'chicken_curry': {
        'name': 'Chicken Curry',
        'calories': 240,
        'protein': 20,
        'carbs': 16,
        'fat': 12,
        'fiber': 3,
        'portion_size': '1 porsiyon (200g)',
        'emoji': '🍛',
        'category': 'Asian',
        'base_amount': 200
    },
    'grilled_salmon': {
        'name': 'Grilled Salmon',
        'calories': 206,
        'protein': 22,
        'carbs': 0,
        'fat': 13,
        'fiber': 0,
        'portion_size': '1 fileto (100g)',
        'emoji': '🐟',
        'category': 'Seafood',
        'base_amount': 100
    },
    'sushi': {
        'name': 'Sushi',
        'calories': 143,
        'protein': 6,
        'carbs': 24,
        'fat': 3,
        'fiber': 1,
        'portion_size': '8 parça (100g)',
        'emoji': '🍣',
        'category': 'Japanese',
        'base_amount': 100
    },
    'ramen': {
        'name': 'Ramen',
        'calories': 436,
        'protein': 15,
        'carbs': 60,
        'fat': 15,
        'fiber': 4,
        'portion_size': '1 kase (400g)',
        'emoji': '🍜',
        'category': 'Japanese',
        'base_amount': 400
    },
    'fried_rice': {
        'name': 'Fried Rice',
        'calories': 245,
        'protein': 5.3,
        'carbs': 43.5,
        'fat': 6,
        'fiber': 1.5,
        'portion_size': '1 porsiyon (150g)',
        'emoji': '🍚',
        'category': 'Asian',
        'base_amount': 150
    },
    'pad_thai': {
        'name': 'Pad Thai',
        'calories': 380,
        'protein': 13,
        'carbs': 50,
        'fat': 14,
        'fiber': 3,
        'portion_size': '1 porsiyon (250g)',
        'emoji': '🍜',
        'category': 'Thai',
        'base_amount': 250
    },
    'spring_rolls': {
        'name': 'Spring Rolls',
        'calories': 140,
        'protein': 4,
        'carbs': 20,
        'fat': 5,
        'fiber': 2,
        'portion_size': '2 adet (100g)',
        'emoji': '🥟',
        'category': 'Asian',
        'base_amount': 100
    },
    'tacos': {
        'name': 'Tacos',
        'calories': 210,
        'protein': 10,
        'carbs': 21,
        'fat': 10,
        'fiber': 3,
        'portion_size': '1 adet (100g)',
        'emoji': '🌮',
        'category': 'Mexican',
        'base_amount': 100
    },
    'burrito': {
        'name': 'Burrito',
        'calories': 206,
        'protein': 10,
        'carbs': 25,
        'fat': 8,
        'fiber': 3.5,
        'portion_size': '1 adet (200g)',
        'emoji': '🌯',
        'category': 'Mexican',
        'base_amount': 200
    },
    'nachos': {
        'name': 'Nachos',
        'calories': 300,
        'protein': 7,
        'carbs': 36,
        'fat': 14,
        'fiber': 4,
        'portion_size': '1 porsiyon (100g)',
        'emoji': '🧀',
        'category': 'Mexican',
        'base_amount': 100
    },
    'caesar_salad': {
        'name': 'Caesar Salad',
        'calories': 285,
        'protein': 7.5,
        'carbs': 15,
        'fat': 22.5,
        'fiber': 3,
        'portion_size': '1 porsiyon (150g)',
        'emoji': '🥗',
        'category': 'Salad',
        'base_amount': 150
    },
    'greek_salad': {
        'name': 'Greek Salad',
        'calories': 135,
        'protein': 4.5,
        'carbs': 12,
        'fat': 9,
        'fiber': 3,
        'portion_size': '1 porsiyon (150g)',
        'emoji': '🥗',
        'category': 'Salad',
        'base_amount': 150
    },
    'caprese_salad': {
        'name': 'Caprese Salad',
        'calories': 240,
        'protein': 15,
        'carbs': 6,
        'fat': 18,
        'fiber': 1.5,
        'portion_size': '1 porsiyon (150g)',
        'emoji': '🥗',
        'category': 'Salad',
        'base_amount': 150
    },
    'onion_rings': {
        'name': 'Onion Rings',
        'calories': 411,
        'protein': 5,
        'carbs': 38,
        'fat': 27,
        'fiber': 2.7,
        'portion_size': '1 porsiyon (100g)',
        'emoji': '🧅',
        'category': 'Fast Food',
        'base_amount': 100
    },
    'garlic_bread': {
        'name': 'Garlic Bread',
        'calories': 350,
        'protein': 9,
        'carbs': 42,
        'fat': 16,
        'fiber': 2,
        'portion_size': '2 dilim (100g)',
        'emoji': '🥖',
        'category': 'Bread',
        'base_amount': 100
    },
    'bruschetta': {
        'name': 'Bruschetta',
        'calories': 170,
        'protein': 5,
        'carbs': 24,
        'fat': 6,
        'fiber': 2,
        'portion_size': '3 adet (100g)',
        'emoji': '🥖',
        'category': 'Appetizer',
        'base_amount': 100
    },
    'ice_cream': {
        'name': 'Ice Cream',
        'calories': 207,
        'protein': 3.5,
        'carbs': 24,
        'fat': 11,
        'fiber': 0.7,
        'portion_size': '1 top (100g)',
        'emoji': '🍦',
        'category': 'Dessert',
        'base_amount': 100
    },
    'cheesecake': {
        'name': 'Cheesecake',
        'calories': 321,
        'protein': 5.5,
        'carbs': 26,
        'fat': 23,
        'fiber': 0.5,
        'portion_size': '1 dilim (100g)',
        'emoji': '🍰',
        'category': 'Dessert',
        'base_amount': 100
    },
    'chocolate_cake': {
        'name': 'Chocolate Cake',
        'calories': 352,
        'protein': 5,
        'carbs': 51,
        'fat': 15,
        'fiber': 2,
        'portion_size': '1 dilim (100g)',
        'emoji': '🍫',
        'category': 'Dessert',
        'base_amount': 100
    },
    'donuts': {
        'name': 'Donuts',
        'calories': 452,
        'protein': 5,
        'carbs': 51,
        'fat': 25,
        'fiber': 1.4,
        'portion_size': '1 adet (100g)',
        'emoji': '🍩',
        'category': 'Dessert',
        'base_amount': 100
    },
    'baklava': {
        'name': 'Baklava',
        'calories': 428,
        'protein': 6,
        'carbs': 51,
        'fat': 23,
        'fiber': 2.7,
        'portion_size': '2 adet (100g)',
        'emoji': '🥮',
        'category': 'Dessert',
        'base_amount': 100
    },
    'hummus': {
        'name': 'Hummus',
        'calories': 166,
        'protein': 8,
        'carbs': 14,
        'fat': 10,
        'fiber': 6,
        'portion_size': '100g',
        'emoji': '🥙',
        'category': 'Dip',
        'base_amount': 100
    }
}

def get_nutrition_info(food_name):
    """Yemek adına göre besin değerlerini döndürür"""
    food_key = food_name.lower().replace(' ', '_')
    return NUTRITION_DATA.get(food_key, None)

def calculate_macros_percentage(protein, carbs, fat):
    """Makro besinlerin yüzdelik oranını hesaplar"""
    total = protein * 4 + carbs * 4 + fat * 9
    if total == 0:
        return 0, 0, 0
    
    protein_pct = (protein * 4 / total) * 100
    carbs_pct = (carbs * 4 / total) * 100
    fat_pct = (fat * 9 / total) * 100
    
    return round(protein_pct), round(carbs_pct), round(fat_pct)

def calculate_portion(nutrition_data, multiplier):
    """
    Porsiyon miktarına göre besin değerlerini hesaplar
    
    Args:
        nutrition_data: Orijinal besin değerleri
        multiplier: Çarpan (base_amount'a göre hesaplanır)
    
    Returns:
        Güncellenmiş besin değerleri
    """
    if not nutrition_data:
        return None
    
    return {
        'name': nutrition_data['name'],
        'calories': round(nutrition_data['calories'] * multiplier),
        'protein': round(nutrition_data['protein'] * multiplier, 1),
        'carbs': round(nutrition_data['carbs'] * multiplier, 1),
        'fat': round(nutrition_data['fat'] * multiplier, 1),
        'fiber': round(nutrition_data['fiber'] * multiplier, 1),
        'portion_size': nutrition_data['portion_size'],
        'emoji': nutrition_data['emoji'],
        'category': nutrition_data['category'],
        'multiplier': multiplier
    }

# Porsiyon tipleri
PORTION_TYPES = {
    'hamburger': {'type': 'gram', 'default': 150, 'max': 500, 'unit_weight': 1},
    'pizza': {'type': 'dilim', 'default': 1, 'max': 8, 'unit_weight': 100},
    'hot_dog': {'type': 'gram', 'default': 100, 'max': 400, 'unit_weight': 1},
    'french_fries': {'type': 'gram', 'default': 100, 'max': 300, 'unit_weight': 1},
    'chicken_wings': {'type': 'gram', 'default': 100, 'max': 500, 'unit_weight': 1},
    'spaghetti_carbonara': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 200},
    'spaghetti_bolognese': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 200},
    'lasagna': {'type': 'dilim', 'default': 1, 'max': 4, 'unit_weight': 150},
    'chicken_curry': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 200},
    'grilled_salmon': {'type': 'gram', 'default': 100, 'max': 500, 'unit_weight': 1},
    'sushi': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 100},
    'ramen': {'type': 'kase', 'default': 1, 'max': 2, 'unit_weight': 400},
    'fried_rice': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 150},
    'pad_thai': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 250},
    'spring_rolls': {'type': 'adet', 'default': 2, 'max': 10, 'unit_weight': 50},
    'tacos': {'type': 'adet', 'default': 2, 'max': 8, 'unit_weight': 100},
    'burrito': {'type': 'gram', 'default': 200, 'max': 500, 'unit_weight': 1},
    'nachos': {'type': 'gram', 'default': 100, 'max': 300, 'unit_weight': 1},
    'caesar_salad': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 150},
    'greek_salad': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 150},
    'caprese_salad': {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 150},
    'onion_rings': {'type': 'gram', 'default': 100, 'max': 300, 'unit_weight': 1},
    'garlic_bread': {'type': 'dilim', 'default': 2, 'max': 8, 'unit_weight': 50},
    'bruschetta': {'type': 'adet', 'default': 3, 'max': 10, 'unit_weight': 33},
    'ice_cream': {'type': 'top', 'default': 1, 'max': 5, 'unit_weight': 100},
    'cheesecake': {'type': 'dilim', 'default': 1, 'max': 4, 'unit_weight': 100},
    'chocolate_cake': {'type': 'dilim', 'default': 1, 'max': 4, 'unit_weight': 100},
    'donuts': {'type': 'adet', 'default': 1, 'max': 5, 'unit_weight': 100},
    'baklava': {'type': 'adet', 'default': 2, 'max': 10, 'unit_weight': 50},
    'hummus': {'type': 'gram', 'default': 100, 'max': 300, 'unit_weight': 1}
}

def get_portion_info(food_name):
    """Yemek için porsiyon bilgisi döndürür"""
    food_key = food_name.lower().replace(' ', '_')
    return PORTION_TYPES.get(food_key, {'type': 'porsiyon', 'default': 1, 'max': 3, 'unit_weight': 100})