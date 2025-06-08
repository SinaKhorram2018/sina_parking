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
            self.ids.lbl_print2.text = ""
            return
        
        # اعتبارسنجی پلاک
        if len(plate) != 8 or plate.count('-') != 1:
            self.ids.lbl_print1.text = "The plate format is incorrect!\n      (Example:abc-1234)"
            self.ids.lbl_print2.text = ""
            return

        # اعتبارسنجی تاریخ
        if len(date) != 10 or date.count('-') != 2:
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
        # درستی ورود نسبت به خروج 
        if login >= logout:
            self.ids.lbl_print1.text = "Enter the input correctly!"
            self.ids.lbl_print2.text = ""
            return
    
        try:
            # اتصال به دیتابیس user
            conn = sqlite3.connect("00.parking.dp")
            cursor = conn.cursor()

            # بررسی وجود پلاک در جدول user
            cursor.execute("SELECT plate FROM user WHERE plate=?", (plate,))
            result_plak = cursor.fetchone()
            
            
            if not result_plak: # اگر پلاک وجود نداشت، آن را در جدول user ثبت کن
                cursor.execute("INSERT INTO user (plate, car) VALUES (?, ?)", (plate, car))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print1.text = "Information saved successfully!"
            else:
                self.ids.lbl_print1.text = "This plate has already been recorded"
                # return
                

            #  برسی اینکه این ماشین قبل از ساعت خروجش نمیتوانه ورودی داشته باشه
            if result_plak:  # فقط اگر پلاک وجود داشته باشد
                r_plate = result_plak[0]
                
                # بررسی تاریخ
                cursor.execute("SELECT date FROM date WHERE date=?", (date,))
                result_date = cursor.fetchone()
                
                # بررسی آخرین زمان خروج برای همین پلاک
                cursor.execute("SELECT logout FROM date WHERE plate=? ORDER BY logout DESC LIMIT 1", (plate,))
                result_logout = cursor.fetchone()
                
                if result_date:
                    r_date = result_date[0]
                else:
                    r_date = None
                    
                if result_logout:
                    r_logout = result_logout[0]
                else:
                    r_logout = None

                # حالا مقایسه کن
                if r_plate == plate and r_date == date and r_logout >= login:
                    self.ids.lbl_print1.text = "This car cannot enter before\n     its departure time."
                    self.ids.lbl_print2.text = ""
                    return


            # بررسی وجود ورود در جدول date
            cursor.execute("SELECT login FROM date WHERE login=?", (login,))
            result_login = cursor.fetchone()
            
            # بررسی تاریخ
            cursor.execute("SELECT date FROM date WHERE date=?", (date,))
            result_date = cursor.fetchone()
            
            if result_date and result_plak and not result_login:  # اگر پلاک بود و ورود وجود نداشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"
            
            elif result_date and not result_plak and result_login:  # اگر پلاک نبود و ورود وجود داشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"
            
            elif result_date and not result_plak and not result_login:  # اگر پلاک نبود و ورود وجود نداشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"  
             
            elif not result_date and result_plak and result_login:  # اگر پلاک نبود و ورود وجود نداشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!" 
            
            elif not result_date and not result_plak and result_login:  # اگر پلاک نبود و ورود وجود نداشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"     
                
            elif not result_date and result_plak and not result_login:  # اگر پلاک نبود و ورود وجود نداشت، آن را در جدول date ثبت کن
                cursor.execute("INSERT INTO date (plate, date, login, logout) VALUES (?, ?, ?, ?)", (plate, date, login, logout))
                conn.commit()
                # نمایش پیغام موفقیت
                self.ids.lbl_print2.text = "Information saved successfully!"  
                 
            elif not result_date and not result_plak and not result_login:  # اگر پلاک نبود و ورود وجود نداشت، آن را در جدول date ثبت کن
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
        pass



class parking(App):
    def build(self):
        return MainWindow()



if __name__ == "__main__":
    parking().run()