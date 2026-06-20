import asyncio
import edge_tts

# الإعدادات الافتراضية
DEFAULT_VOICE = "ar-SA-HamedNeural"  # صوت رجال ناضج من السعودية
DEFAULT_RATE = "-20%"                 # أبطأ بنسبة 20%
DEFAULT_PITCH = "-10Hz"              # نبرة أعمق

async def text_to_speech(
    text: str,
    output_file: str = "microsoft_arabic.mp3",
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH
):
    """
    تحويل النص إلى ملف صوت mp3 باستخدام edge-tts
    
    Parameters:
        text (str): النص المراد تحويله إلى صوت
        output_file (str): اسم ملف الصوت الناتج (افتراضي: microsoft_arabic.mp3)
        voice (str): اسم الصوت من Microsoft Edge TTS (افتراضي: ar-SA-HamedNeural)
        rate (str): سرعة الكلام، الموجب أسرع والسالب أبطأ (افتراضي: -20%)
        pitch (str): نبرة الصوت، الموجب أعلى والسالب أعمق (افتراضي: -10Hz)
    
    Returns:
        str: مسار ملف الصوت الناتج
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_file)
    print(f"✅ تم إنشاء الملف الصوتي: {output_file}")
    return output_file

# ✅ أمثلة للاستخدام من ملف خارجي:
# import asyncio
# from audio import text_to_speech
# 
# asyncio.run(text_to_speech("نص تجريبي", "test.mp3"))
# asyncio.run(text_to_speech("نص بصوت مختلف", voice="ar-EG-ShakirNeural", rate="+10%"))

if __name__ == "__main__":
    # للتشغيل المباشر للملف
    text = "أهلاً بك. هذا الصوت الاحترافي يتم توليده عبر خدمات مايكروسوفت الذكية مجاناً وبأعلى جودة."
    asyncio.run(text_to_speech(text, "microsoft_arabic.mp3"))
    print("تم إنشاء الصوت الاحترافي بنجاح!")