from moviepy.editor import VideoFileClip, AudioFileClip

def add_audio_to_video(video_path, audio_path, output_path):
    # 1. تحميل ملف الفيديو
    video_clip = VideoFileClip(video_path)
    
    # 2. تحميل ملف الصوت
    audio_clip = AudioFileClip(audio_path)
    
    # 3. اختياري: إذا كان الصوت أطول من الفيديو وتريد قصه ليتناسب مع مدة الفيديو
    # audio_clip = audio_clip.subclip(0, video_clip.duration)
    
    # 4. دمج الصوت الجديد مع الفيديو (سيقوم هذا باستبدال الصوت القديم إن وجد)
    video_with_audio = video_clip.set_audio(audio_clip)
    
    # 5. حفظ الفيديو الجديد الناتج
    # يمكنك تغيير الـ codec بناءً على صيغة الفيديو المفضلة لديك
    video_with_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    # 6. إغلاق الملفات لتحرير الذاكرة
    video_clip.close()
    audio_clip.close()
    video_with_audio.close()

# --- مثال على الاستخدام ---
video_input = "my_video.mp4"      # اسم ملف الفيديو الخاص بك
audio_input = "my_audio.mp3"      # اسم ملف الصوت الخاص بك
video_output = "final_output.mp4" # اسم الفيديو الجديد الناتج

add_audio_to_video(video_input, audio_input, video_output)
print("تم إضافة الصوت إلى الفيديو بنجاح!")