# שימוש בתמונת בסיס רשמית של פייתון
FROM python:3.13-slim

# הגדרת תיקיית העבודה בתוך הקונטיינר
WORKDIR /app

# העתקת קבצי התלויות
COPY requirements.txt .

# התקנת התלויות מתוך קובץ הדרישות
RUN pip install --no-cache-dir -r requirements.txt

# העתקת שאר קבצי הפרויקט לתוך הקונטיינר
COPY . .

# פקודת ההפעלה של היישום (יש להתאים לפי סוג הפרויקט, למשל פייתון ישיר או pytest)
CMD ["python", "app.py"]