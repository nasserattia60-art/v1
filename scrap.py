import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. حدد رابط الموقع الذي تريد سحب البيانات منه
url = input("أدخل رابط الموقع الذي يحتوي على الاقتباسات: ")

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
    
    # 5. إنشاء القائمة لتجميع البيانات
    quotes_list = []

    for blockquote in blockquotes:
        quote_text = blockquote.find('p').text.strip() if blockquote.find('p') else "لم يتم العثور على الحكمة"
        author_element = blockquote.find('cite', class_='author')
        author_name = author_element.text.strip() if author_element else "كاتب مجهول"
        
        # إضافة البيانات كقاموس داخل القائمة
        quotes_list.append({
            'id': len(quotes_list) + 1,
            'الحكمة': quote_text,
            'الكاتب': author_name,
            'used': False,
            "date": pd.Timestamp.now()

        })

    # 6. تحويل القائمة إلى Pandas DataFrame
    df = pd.DataFrame(quotes_list)

   
    csv_file_path = "quotes_pandas.csv"
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

    print(f"تم الحفظ بنجاح باستخدام Pandas في: {csv_file_path}")
    print(f"عدد الاقتباسات المستخرجة: {len(quotes_list)}")
else:
    print(f"فشل في تحميل الصفحة، كود الحالة: {response.status_code}")