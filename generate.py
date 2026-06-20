import asyncio
import csv
import os
import subprocess
from datetime import datetime
import edge_tts

# الإعدادات الافتراضية
CSV_FILE = "quotes_pandas.csv"
VIDEO_BG = "background.mp4"
OUTPUT_DIR = "output"

# ضبط النبرة والسرعة (لصوت ناضج هاديء)
RATE = "-20%"
PITCH = "-10Hz"
VOICE = "ar-SA-HamedNeural"


# ------- دوال CSV -------

def get_next_quote(csv_file: str = CSV_FILE):
    """
    يقرأ CSV ويجيب أول اقتباس لم يستخدم بعد (used=False)
    
    Parameters:
        csv_file (str): مسار ملف CSV
    
    Returns:
        tuple: (quote_dict, all_rows) أو (None, rows) إذا لم يتبق اقتباس
    """
    rows = []
    with open(csv_file, mode='r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    for row in rows:
        if row['used'].strip() == 'False':
            return row, rows
    
    return None, rows


def mark_as_used(quote_id: str, rows: list, csv_file: str = CSV_FILE):
    """
    يحدث عمود used في CSV إلى True بعد معالجة الاقتباس
    
    Parameters:
        quote_id (str): رقم الاقتباس
        rows (list): قائمة بكل الصفوف من CSV
        csv_file (str): مسار ملف CSV
    """
    for row in rows:
        if row['id'] == quote_id:
            row['used'] = 'True'
            row['date'] = datetime.now().isoformat()
            break
    
    with open(csv_file, mode='w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['id', 'الحكمة', 'الكاتب', 'used', 'date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ------- دوال الصوت -------

async def text_to_speech(
    text: str,
    output_audio: str,
    voice: str = VOICE,
    rate: str = RATE,
    pitch: str = PITCH
):
    """
    يحول النص إلى ملف صوت mp3 باستخدام edge-tts
    
    Parameters:
        text (str): النص المراد تحويله
        output_audio (str): مسار ملف الصوت الناتج
        voice (str): اسم الصوت
        rate (str): سرعة الكلام
        pitch (str): نبرة الصوت
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_audio)
    print(f"  ✅ تم إنشاء الملف الصوتي: {output_audio}")


# ------- دوال الفيديو -------

def merge_audio_to_video(audio_file: str, video_bg: str, output_video: str):
    """
    يدمج الصوت مع فيديو الخلفية وينتج فيديو نهائي
    
    Parameters:
        audio_file (str): مسار ملف الصوت
        video_bg (str): مسار فيديو الخلفية
        output_video (str): مسار الفيديو الناتج
    
    Returns:
        bool: True إذا نجح الدمج، False إذا فشل
    """
    cmd = [
        'ffmpeg', '-y',
        '-i', video_bg,
        '-i', audio_file,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-map', '0:v:0',
        '-map', '1:a:0',
        output_video
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ تم إنشاء الفيديو النهائي: {output_video}")
        return True
    else:
        print(f"  ❌ فشل دمج الفيديو: {result.stderr}")
        return False


async def process_quote(
    quote_id: str,
    quote_text: str,
    author: str,
    output_dir: str = OUTPUT_DIR,
    video_bg: str = VIDEO_BG
):
    """
    يعالج اقتباس واحد: يحوله إلى صوت ثم يدمجه مع الفيديو
    
    Parameters:
        quote_id (str): رقم الاقتباس
        quote_text (str): نص الاقتباس
        author (str): اسم الكاتب
        output_dir (str): مجلد الإخراج
        video_bg (str): مسار فيديو الخلفية
    
    Returns:
        tuple: (audio_file, video_file) مسارات الملفات الناتجة
    """
    os.makedirs(output_dir, exist_ok=True)
    
    full_text = f"{quote_text}. قالها: {author}"
    
    audio_file = os.path.join(output_dir, f"{quote_id}.mp3")
    video_file = os.path.join(output_dir, f"{quote_id}.mp4")
    
    print(f"\n--- جاري معالجة الاقتباس رقم {quote_id} ---")
    print(f"النص: {quote_text}")
    print(f"الكاتب: {author}")
    
    # 1. تحويل النص إلى صوت
    print("  • جاري توليد الصوت...")
    await text_to_speech(full_text, audio_file)
    
    # 2. دمج الصوت مع الفيديو
    print("  • جاري دمج الصوت مع الفيديو...")
    merge_audio_to_video(audio_file, video_bg, video_file)
    
    return audio_file, video_file


async def process_next_quote(
    csv_file: str = CSV_FILE,
    video_bg: str = VIDEO_BG,
    output_dir: str = OUTPUT_DIR
):
    """
    يجلب الاقتباس التالي غير المستخدم، يولّد صوتاً وفيديو، ويحدث CSV
    
    Parameters:
        csv_file (str): مسار ملف CSV
        video_bg (str): مسار فيديو الخلفية
        output_dir (str): مجلد الإخراج
    
    Returns:
        dict or None: معلومات الاقتباس المعالج، أو None إذا لم يتبق اقتباس
    """
    # التأكد من وجود مجلد output
    os.makedirs(output_dir, exist_ok=True)
    
    # التأكد من وجود ملف الفيديو الأساسي
    if not os.path.exists(video_bg):
        print(f"⚠  ملف الفيديو '{video_bg}' غير موجود. فضلاً أضف الفيديو في المجلد.")
        return None
    
    # جلب الاقتباس التالي
    quote, all_rows = get_next_quote(csv_file)
    
    if quote is None:
        print("✅ تمت معالجة جميع الاقتباسات من قبل!")
        return None
    
    quote_id = quote['id']
    quote_text = quote['الحكمة']
    author = quote['الكاتب']
    
    # معالجة الاقتباس
    audio_file, video_file = await process_quote(quote_id, quote_text, author, output_dir, video_bg)
    
    # تحديث CSV
    mark_as_used(quote_id, all_rows, csv_file)
    
    print(f"\n✅ تمت معالجة الاقتباس رقم {quote_id} بنجاح!")
    print(f"  • ملف الصوت: {audio_file}")
    print(f"  • ملف الفيديو: {video_file}")
    
    return {
        "id": quote_id,
        "text": quote_text,
        "author": author,
        "audio": audio_file,
        "video": video_file
    }


async def process_all_quotes(
    csv_file: str = CSV_FILE,
    video_bg: str = VIDEO_BG,
    output_dir: str = OUTPUT_DIR
):
    """
    يعالج جميع الاقتباسات غير المستخدمة بالتسلسل
    
    Parameters:
        csv_file (str): مسار ملف CSV
        video_bg (str): مسار فيديو الخلفية
        output_dir (str): مجلد الإخراج
    
    Returns:
        int: عدد الاقتباسات التي تمت معالجتها
    """
    count = 0
    while True:
        result = await process_next_quote(csv_file, video_bg, output_dir)
        if result is None:
            break
        count += 1
    
    if count > 0:
        print(f"\n🎉 تمت معالجة {count} اقتباس(ات) بنجاح!")
    else:
        print("لا توجد اقتباسات جديدة للمعالجة.")
    
    return count


# ✅ أمثلة للاستخدام من ملف خارجي:
# import asyncio
# from generate import process_next_quote, process_all_quotes
# 
# # لمعالجة اقتباس واحد فقط:
# asyncio.run(process_next_quote())
# 
# # لمعالجة جميع الاقتباسات:
# asyncio.run(process_all_quotes())
#
# # لمعالجة باقي الاقتباسات دفعة واحدة:
# asyncio.run(process_all_quotes(output_dir="output"))


if __name__ == "__main__":
    # للتشغيل المباشر: يعالج اقتباس واحد فقط
    asyncio.run(process_next_quote())