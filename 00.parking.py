# تنظیمات اولیه برای اندازه پنجره برنامه با استفاده از ماژول Config
from kivy.config import Config 

Config.set('graphics', 'width', '290')  # عرض پنجره برنامه به 290 پیکسل
Config.set('graphics', 'height', '580')  # ارتفاع پنجره برنامه به 580 پیکسل
Config.set('graphics', 'resizable', '1')  # امکان تغییر اندازه پنجره فعال است

# --------------------------------------------------------------------------
from kivy.core.text import LabelBase

# ثبت فونت فارسی
LabelBase.register(name="fs", fn_regular="FiraCode-SemiBold.ttf")

# -----------------------------------------------------------------------------
import sqlite3
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

# -------------------------------------------------------------------------------

from datetime import datetime  # برای مقایسه زمان و تاریخ

# ----------------------------------------------------------------------
# بارگذاری فایل kv
Builder.load_file("00.parking_screen.kv")

# ------------------------------------------------------------------------------------

# اتصال به دیتابیس و ایجاد جداول
conn = sqlite3.connect("00.parking.dp")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS user(
                plate TEXT PRIMARY KEY,
                car TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS date(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT,
                date DATE,
                login TIME,
                logout TIME)''')

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
        if not all([car, plate, date, login, logout]):
            self.ids.lbl_print1.text = "Please fill in all fields!"
            self.ids.lbl_print2.text = ""
            return
        
        # اعتبارسنجی پلاک
        if len(plate) != 8 or plate.count('-') != 1:
            self.ids.lbl_print1.text = "The plate format is incorrect!\n      (Example:abc-1234)"
            self.ids.lbl_print2.text = ""
            return

        # اعتبارسنجی تاریخ
        valid_date = False
        for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
            try:
                parsed_date = datetime.strptime(date, fmt)
                valid_date = True
                break
            except ValueError:
                continue
            
        if not valid_date:
            self.ids.lbl_print1.text = "The date format is incorrect!\n    (Example:2025-01-01)"
            self.ids.lbl_print2.text = ""
            return
        
        # اعتبارسنجی ورود
        if len(login) != 5 or login.count(':') != 1:
            self.ids.lbl_print1.text = "The login format is incorrect!\n       (Example:00:00)"
            self.ids.lbl_print2.text = ""
            return

        # اعتبارسنجی خروج
        if len(logout) != 5 or logout.count(':') != 1:
            self.ids.lbl_print1.text = "The exit format is incorrect!\n      (Example:00:00)"
            self.ids.lbl_print2.text = ""
            return
        
        # تبدیل زمان‌ها به datetime
        try:
            login_dt = datetime.strptime(login, "%H:%M")
            logout_dt = datetime.strptime(logout, "%H:%M")
        except ValueError:
            self.ids.lbl_print1.text = "Invalid time format!"
            return
        
        # بررسی اینکه زمان خروج بعد از ورود باشد
        if login_dt >= logout_dt:
            self.ids.lbl_print1.text = "Enter the input correctly!"
            self.ids.lbl_print2.text = ""
            return

        conn = None
        try:
            # اتصال به دیتابیس
            conn = sqlite3.connect("00.parking.dp")
            cursor = conn.cursor()

            # بررسی وجود پلاک در جدول user
            cursor.execute("SELECT plate FROM user WHERE plate=?", (plate,))
            result_plak = cursor.fetchone()
            
            
            if not result_plak: # اگر پلاک وجود نداشت، آن را در جدول user ثبت کن
                cursor.execute("INSERT INTO user (plate, car) VALUES (?, ?)", (plate, car))
                conn.commit()
                self.ids.lbl_print1.text = "Information saved successfully!" # نمایش پیغام موفقیت
            else:
                self.ids.lbl_print1.text = "This plate has already been recorded"
                

             # بررسی آخرین زمان خروج برای همین پلاک
            cursor.execute("SELECT date, logout FROM date WHERE plate=? ORDER BY id DESC LIMIT 1", (plate,))
            last_record = cursor.fetchone()
                
            if last_record:
                db_date, db_logout = last_record
                
                try:
                    db_logout_dt = datetime.strptime(db_logout, "%H:%M")
                except ValueError:
                    db_logout_dt = None

                # مقایسه تاریخ و زمان
                if db_date == date and db_logout_dt and login_dt < db_logout_dt:
                    self.ids.lbl_print1.text = "This car cannot enter before\n     its exit time."
                    self.ids.lbl_print2.text = ""
                    return


            # بررسی اینکه آیا برای این تاریخ قبلاً ورودی ثبت شده؟
            cursor.execute("SELECT * FROM date WHERE plate=? AND date=?", (plate, date))
            existing_record = cursor.fetchone()

            
            # اگر هنوز وجود نداره، ثبت کن
            if existing_record:
                self.ids.lbl_print2.text = "This car already has a record \n     for this date!"
                return

            cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)",
                        (plate, date, login, logout))
            conn.commit()
            self.ids.lbl_print2.text = "Information saved successfully!"

        except sqlite3.IntegrityError:
            self.ids.lbl_print2.text = "This plate has already been recorded!"
        except Exception as e:
            self.ids.lbl_print2.text = f"Error: {str(e)}"
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

# ===============================================================

    def search(self):
        # گرفتن مقدار پلاک از ورودی
        plate = self.ids.tin_plate.text.strip()
        if not plate:
            self.ids.lbl_print1.text = "Please enter the license plate!"
            return

        try:          
            # جستجوی اطلاعات پلاک در جدول 
            conn = sqlite3.connect("00.parking.dp") # اتصال به دیتابیس user
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE plate=?", (plate,))
            result_user = cursor.fetchone()
            
            #print(f"{result_user}")

            if not result_user:
                self.ids.lbl_print1.text = "License plate not found!"
                self.ids.lbl_print2.text = ""
                return

            # جستجوی تمام تاریخ‌های مرتبط با پلاک در جدول date
            conn = sqlite3.connect("00.parking.dp")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM date WHERE plate=?", (plate,))
            results_date = cursor.fetchall()
            
            #print(f"{results_date}")

            if results_date:
                dates = "\n".join([f"date: {row[2:5]}" for row in results_date])
                self.ids.lbl_print1.text = f"car: {result_user[1]}, plate: {result_user[0]}"
                self.ids.lbl_print2.text = f"{dates}"
            else:
                self.ids.lbl_print1.text = "No date has been recorded for this license plate!"
                self.ids.lbl_print2.text = ""

        except Exception as e:
            self.ids.lbl_print1.text = f"error: {str(e)}"

        finally:
            if 'conn_user' in locals():
                conn.close()



class parking(App):
    def build(self):
        return MainWindow()



if __name__ == "__main__":
    parking().run()