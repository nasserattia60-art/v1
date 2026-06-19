import requests
from bs4 import BeautifulSoup

# 1. حدد رابط الموقع الذي تريد سحب البيانات منه
url = "https://example.com"

# 2. إرسال طلب لفتح الصفحة وجلب محتواها
response = requests.get(url)

# التأكد من أن الصفحة تعمل بنجاح (كود الحالة 200)
if response.status_code == 200:
    # 3. تمرير محتوى الصفحة إلى BeautifulSoup لتسهيل قراءته
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 4. أمثلة لاستخراج البيانات:
    
    # أ. جلب عنوان الصفحة بالكامل (العنصر <title>)
    page_title = soup.title.text
    print(f"عنوان الصفحة: {page_title}")
    print("-" * 30)
    
    # ب. جلب أول عنوان رئيسي في الصفحة (العنصر <h1>)
    first_h1 = soup.find('h1').text if soup.find('h1') else "لا يوجد عنوان h1"
    print(f"أول h1 في الصفحة: {first_h1}")
    print("-" * 30)
    
    # ج. جلب كل الروابط الموجودة في الصفحة (العناصر <a>) واصطياد رابطها (href)
    print("الروابط الموجودة في الصفحة:")
    links = soup.find_all('a')
    for link in links:
        link_href = link.get('href')
        link_text = link.text.strip()
        print(f"النص: {link_text} -> الرابط: {link_href}")

else:
    print(f"فشل في الاتصال بالموقع.