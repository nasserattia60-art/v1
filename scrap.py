import csv
import requests
from bs4 import BeautifulSoup
import os

# 1. حدد رابط الموقع الذي تريد سحب البيانات منه
url = "http://حكم.net/%d8%ad%d9%83%d9%85-%d8%b9%d9%86-%d8%a7%d9%84%d8%ae%d8%b3%d8%a7%d8%b1%d8%a9"

# 2. إرسال طلب لفتح الصفحة وجلب محتواها
response = requests.get(url)

# ضبط الترميز بناءً على المحتوى الفعلي للصفحة (يدعم العربية)
response.encoding = response.apparent_encoding

# التأكد من أن الصفحة تعمل بنجاح (كود الحالة 200)
if response.status_code == 200:
    # 3. تمرير محتوى الصفحة إلى BeautifulSoup لتسهيل قراءته
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 4. إيجاد جميع عناصر blockquote (متعددة)
    blockquotes = soup.find_all('blockquote')
    
    # 5. إنشاء القائمة لتجميع البيانات الجديدة
    new_quotes_list = []

    for blockquote in blockquotes:
        quote_text = blockquote.find('p').text.strip() if blockquote.find('p') else "لم يتم العثور على الحكمة"
        author_element = blockquote.find('cite', class_='author')
        author_name = author_element.text.strip() if author_element else "كاتب مجهول"
        
        # إضافة البيانات كقاموس داخل القائمة
        new_quotes_list.append({
            'الحكمة': quote_text,
            'الكاتب': author_name
        })

    # 6. قراءة الملف الموجود والتحقق من التكرارات
    csv_file_path = "quotes_pandas.csv"
    existing_quotes = set()

    # التحقق من وجود الملف أولاً
    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode='r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # استخدام tuple من (الحكمة, الكاتب) كمفتاح في set للتحقق من التكرار
                existing_quotes.add((row['الحكمة'], row['الكاتب']))

    # 7. إضافة الاقتباسات الجديدة فقط (الغير موجودة مسبقاً)
    added_count = 0
    for quote in new_quotes_list:
        key = (quote['الحكمة'], quote['الكاتب'])
        if key not in existing_quotes:
            existing_quotes.add(key)
            with open(csv_file_path, mode='a', encoding='utf-8-sig', newline='') as file:
                fieldnames = ['الحكمة', 'الكاتب']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                # كتابة الهيدر فقط إذا كان الملف جديداً (فارغ)
                if not os.path.exists(csv_file_path) or os.path.getsize(csv_file_path) == 0:
                    writer.writeheader()
                writer.writerow(quote)
            added_count += 1

    print(f"تم الحفظ بنجاح في: {csv_file_path}")
    print(f"عدد الاقتباسات الجديدة المضافة: {added_count}")
    print(f"عدد الاقتباسات الموجودة مسبقاً: {len(existing_quotes) - added_count}")
else:
    print(f"فشل في تحميل الصفحة، كود الحالة: {response.status_code}")