# تنظیمات اولیه برای اندازه پنجره برنامه با استفاده از ماژول Config
from kivy.config import Config 

Config.set('graphics', 'width', '290')  # عرض پنجره برنامه به 290 پیکسل
Config.set('graphics', 'height', '580')  # ارتفاع پنجره برنامه به 580 پیکسل
Config.set('graphics', 'resizable', '1')  # امکان تغییر اندازه پنجره فعال است

# ----------------------------------------------------------------------
import arabic_reshaper
from bidi.algorithm import get_display

def fix_text(text):
    """تبدیل متن فارسی به فرم درست برای نمایش در Kivy"""
    reshaped_text = arabic_reshaper.reshape(text)  # اصلاح شکل حروف
    return get_display(reshaped_text)  # مرتب کردن جهت متن راست به چپ

# --------------------------------------------------------------------------
from kivy.core.text import LabelBase

# ثبت فونت فارسی
LabelBase.register(name="fs", fn_regular="FiraCode-SemiBold.ttf")

# -----------------------------------------------------------------------------
import sqlite3
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

# ----------------------------------------------------------------------
# بارگذاری فایل kv
Builder.load_file("00.parking_screen.kv")

# ------------------------------------------------------------------------------------

# اتصال به دیتابیس‌ها و ایجاد جداول
conn = sqlite3.connect("00.parking.dp")  # اتصال به دیتابیس و ایجاد شی از آن
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS user(
                plate TEXT PRIMARY KEY,
                car TEXT)''')  # plak به عنوان PRIMARY KEY تعریف شده است

conn = sqlite3.connect("00.parking.dp")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS date(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT,
                date DATE,
                login TIME,
                logout TIME)''')  # تاریخ به صورت TEXT ذخیره می‌شود و id به عنوان PRIMARY KEY
conn.commit()
conn.close()


# -----------------------------------------------------------------------------
class MainWindow(FloatLayout):
    
    def save(self):
        # گرفتن مقادیر ورودی
        car = self.ids.tin_car.text.strip()
        plate = self.ids.tin_plate.text.strip()
        date = self.ids.tin_date.text.strip()
        login = self.ids.tin_login.text.strip()
        logout = self.ids.tin_exit.text.strip()
        
        # بررسی اعتبار ورودی‌ها
        if not car or not plate or not date or not login or not logout:
            self.ids.lbl_print1.text = "Please fill in all fields!"
            return
        
        # اعتبارسنجی پلاک
        if len(plate) != 8 or plate.count('-') != 1:
            self.ids.lbl_print1.text = "The plate format is incorrect!\n      (Example:abc-1234)"
            return

        # اعتبارسنجی تاریخ
        if len(date) != 10 or date.count('-') != 2:
            self.ids.lbl_print1.text = "The date format is incorrect!\n    (Example:2025-01-01)"
            return
        
        # اعتبارسنجی ورود
        if len(login) != 5 or login.count(':') != 1:
            self.ids.lbl_print1.text = "The login format is incorrect!\n       (Example:00:00)"
            return

        # اعتبارسنجی خروج
        if len(logout) != 5 or logout.count(':') != 1:
            self.ids.lbl_print1.text = "The exit format is incorrect!\n      (Example:00:00)"
            return
        # درستی ورود نسبت به خروج 
        if login >= logout:
            self.ids.lbl_print1.text = "Enter the input correctly!"
            return
    
        try:
            # اتصال به دیتابیس user
            conn = sqlite3.connect("00.parking.dp")
            cursor = conn.cursor()

            # بررسی وجود پلاک در جدول user
            cursor.execute("SELECT * FROM user WHERE plate=?", (plate,))
            result_plak = cursor.fetchone()
            
            if not result_plak: # اگر پلاک وجود نداشت، آن را در جدول user ثبت کن
                cursor.execute("INSERT INTO user (plate, car) VALUES (?, ?)", (plate, car))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print1.text = "Information saved successfully!"
            else:
                self.ids.lbl_print1.text = "This plate has already been recorded"
                # return
                

# ???????????????????????????????????????????????????????????            
            #  برسی دور نزدن 
            cursor.execute("SELECT * FROM date WHERE date=?", (date,))
            result = cursor.fetchall()
            print(f"{result}")
            
            result_date = result[-3]
            result_logout = result[-1]
            
            print(f"{result_date}")
            print(f"{result_logout}")
                        
            if result_date == date and result_logout >= login: # اگر تاریخ بود و خروجی کوچبک یا مساوی ورودی بود 
                self.ids.lbl_print1.text = "mano dor nazan"
                return
            

# ??????????????????????????????????????????????????????????????????

            
            # بررسی وجود ورود در جدول date
            cursor.execute("SELECT * FROM date WHERE login=?", (login,))
            result_login = cursor.fetchone()
            
            if result_plak and not result_login:  # اگر پلاک بود و ورود وجود نداشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"
            
            elif not result_plak and result_login:  # اگر پلاک نبود و ورود وجود داشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"
            
            elif not result_plak and not result_login:  # اگر پلاک نبود و ورود وجود نداشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"  
                 
            else:
                self.ids.lbl_print2.text = "This car is in the parking lot!"
                return   
            
                        

        except sqlite3.IntegrityError:
            # اگر پلاک تکراری باشد (در جدول user)
            self.ids.lbl_print2.text = "This plate has already been recorded!"

        except Exception as e:
            # مدیریت سایر خطاها
            self.ids.lbl_print2.text = f"error: {str(e)}"

        finally:
            # بستن اتصال به دیتابیس‌ها
            if 'conn_user' in locals():
                conn.close()
            


# ===============================================================

    def search(self):
        # گرفتن مقدار پلاک از ورودی
        plate = self.ids.tin_plate.text.strip()
        if not plate:
            self.ids.lbl_print.text = "Please enter the license plate!"
            return

        try:
            # جستجوی اطلاعات پلاک در جدول 
            conn = sqlite3.connect("00.parking.dp")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE plate=?", (plate,))
            result_user = cursor.fetchone()

            if not result_user:
                self.ids.lbl_print.text = "License plate not found!"
                return

            # جستجوی تمام تاریخ‌های مرتبط با پلاک در جدول date
            conn = sqlite3.connect("00.parking.dp")
            cursor = conn.cursor()
            cursor.execute("SELECT date FROM date WHERE plate=?", (plate,))
            results_date = cursor.fetchall()

            if results_date:
                dates = "\n".join([f"date: {row[0]}" for row in results_date])
                self.ids.lbl_print.text = f"car: {result_user[1]}, plate: {result_user[0]}\n{dates}"
            else:
                self.ids.lbl_print.text = "No date has been recorded for this license plate!"

        except Exception as e:
            self.ids.lbl_print.text = f"error: {str(e)}"

        finally:
            if 'conn_user' in locals():
                conn.close()





class parking(App):
    def build(self):
        return MainWindow()

    def fix_text(self, text):
        """تابع را به Kivy معرفی می‌کنیم"""
        return fix_text(text)


if __name__ == "__main__":
    parking().run()