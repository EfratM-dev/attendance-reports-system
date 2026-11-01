import os
from services.attendance_pipeline_service import AttendancePipelineService


def main():
    print("שלום רב! ברוכים הבאים למערכת ניהול ועיבוד דוחות נוכחות.")
    print("-" * 50)

    # קבלת נתיב הקובץ מהמשתמש
    file_path = "inputs/n_r_10_n.pdf"  #input("הכנס את נתיב קובץ הקלט (למשל inputs/a_r_9.pdf) [ברירת מחדל: inputs/a_r_25.pdf]: ").strip()
    if not file_path:
        file_path = "inputs/a_r_25.pdf"

    if not os.path.exists(file_path):
        print(f"אזהרה: הקובץ בנתיב {file_path} לא נמצא פיזית כרגע, יופעל עיבוד לנתיב שהוזן.")

    # קבלת פורמט הייצוא המבוקש מהמשתמש
    print("\nבחר את פורמט הייצוא הרצוי:")
    print("1. PDF (הקש pdf)")
    print("2. Excel (הקש excel או xlsx)")

    export_format = input("הכנס את הפורמט המבוקש [ברירת מחדל: pdf]: ").strip()
    if not export_format:
        export_format = "pdf"

    # קביעת סיומת הקובץ באמצעות if / elif לתמיכה בהרחבות עתידיות (כגון docx)
    format_lower = export_format.lower()
    if format_lower in ["excel", "xlsx"]:
        ext = ".xlsx"
    elif format_lower in ["pdf"]:
        ext = ".pdf"
    else:
        raise ValueError(f"פורמט ייצוא לא נתמך: {export_format}")

    # הגדרת תיקיית היעד לווידוא קיומה
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # אתחול והפעלת הצינור (Pipeline)
    pipeline = AttendancePipelineService()

    try:
        print('\nמעבד את הדו"ח, אנא המתן...')

        # דרישה 9: קובץ הפלט ייקרא באותו שם של קובץ הקלט בתוספת המילה output
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = os.path.join(output_dir, f"{base_name}_output{ext}")

        output_file = pipeline.process_and_export_report(file_path, export_format=export_format, output_path=output_filename)

        print("\nהפעולה בוצעה בהצלחה!")
        print(f"הקובץ המוכן נשמר בנתיב: {output_file}")

    except Exception as e:
        print(f"\nאירעה שגיאה במהלך עיבוד הדו\"ח: {e}")


if __name__ == "__main__":
    main()