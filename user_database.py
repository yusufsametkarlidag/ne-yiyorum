import sqlite3
import hashlib
from datetime import datetime, date

class UserDatabase:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_name)
    
    def create_tables(self):
        """Tabloları oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            gender TEXT,
            activity_level TEXT,
            goal TEXT,
            daily_calorie_target REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Yemek kayıtları tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            food_name TEXT,
            portion REAL,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            fiber REAL,
            date DATE,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Şifreyi hashle"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, age, weight, height, gender, activity_level, goal):
        """Yeni kullanıcı kaydet"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Kalori hedefini hesapla
            daily_calorie = self.calculate_daily_calorie(
                weight, height, age, gender, activity_level, goal
            )
            
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
            INSERT INTO users (username, password, age, weight, height, gender, 
                             activity_level, goal, daily_calorie_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, age, weight, height, gender, 
                  activity_level, goal, daily_calorie))
            
            conn.commit()
            conn.close()
            return True, "Kayıt başarılı!"
        except sqlite3.IntegrityError:
            return False, "Bu kullanıcı adı zaten alınmış!"
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def login_user(self, username, password):
        """Kullanıcı girişi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        hashed_password = self.hash_password(password)
        
        cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {
                'id': user[0],
                'username': user[1],
                'age': user[3],
                'weight': user[4],
                'height': user[5],
                'gender': user[6],
                'activity_level': user[7],
                'goal': user[8],
                'daily_calorie_target': user[9]
            }
        else:
            return False, None
    
    def calculate_daily_calorie(self, weight, height, age, gender, activity_level, goal):
        """Günlük kalori hedefini hesapla"""
        # BMR hesapla (Mifflin-St Jeor)
        if gender == 'Erkek':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Aktivite çarpanı
        activity_multipliers = {
            'Sedanter': 1.2,
            'Az Aktif': 1.375,
            'Orta Aktif': 1.55,
            'Çok Aktif': 1.725
        }
        
        tdee = bmr * activity_multipliers[activity_level]
        
        # Hedefe göre ayarla
        if goal == 'Kilo Ver':
            return tdee - 500  # 500 kalori açık
        elif goal == 'Kilo Al':
            return tdee + 300  # 300 kalori fazla
        else:  # Kilonu Koru
            return tdee
    
    def add_meal_log(self, user_id, username, food_name, portion, calories, protein, carbs, fat, fiber):
        """Yemek kaydı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today()
        
        cursor.execute('''
        INSERT INTO meal_logs (user_id, username, food_name, portion, calories, 
                              protein, carbs, fat, fiber, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, food_name, portion, calories, protein, carbs, fat, fiber, today))
        
        conn.commit()
        conn.close()
    
    def get_today_meals(self, user_id):
        """Bugünün yemeklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today()
        
        cursor.execute('''
        SELECT * FROM meal_logs WHERE user_id = ? AND date = ?
        ORDER BY timestamp DESC
        ''', (user_id, today))
        
        meals = cursor.fetchall()
        conn.close()
        
        return meals
    
    def get_today_totals(self, user_id):
        """Bugünün toplam değerlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today()
        
        cursor.execute('''
        SELECT 
            COALESCE(SUM(calories), 0) as total_calories,
            COALESCE(SUM(protein), 0) as total_protein,
            COALESCE(SUM(carbs), 0) as total_carbs,
            COALESCE(SUM(fat), 0) as total_fat,
            COALESCE(SUM(fiber), 0) as total_fiber
        FROM meal_logs 
        WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_calories': result[0],
            'total_protein': result[1],
            'total_carbs': result[2],
            'total_fat': result[3],
            'total_fiber': result[4]
        }
    
    def get_weekly_stats(self, user_id):
        """Haftalık istatistikler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        seven_days_ago = date.today() - datetime.timedelta(days=7)
        
        cursor.execute('''
        SELECT date, SUM(calories) as daily_calories
        FROM meal_logs
        WHERE user_id = ? AND date >= ?
        GROUP BY date
        ORDER BY date
        ''', (user_id, seven_days_ago))
        
        results = cursor.fetchall()
        conn.close()
        
        return results