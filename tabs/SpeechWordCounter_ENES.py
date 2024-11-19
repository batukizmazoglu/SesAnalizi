import speech_recognition as sr
import threading

# Kelime sayısını takip eden bir global değişken
word_count = 0

# Ses tanıma ve kelime sayma fonksiyonu
def recognize_and_count():
    global word_count
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Sisteme konuşabilirsiniz...")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)  # Arka plan gürültüsünü ayarla
        while True:
            print("Dinleniyor...")
            try:
                # Mikrofon verisini al
                audio = recognizer.listen(source, timeout=5)

                # Speech-to-text
                text = recognizer.recognize_google(audio, language="tr-TR")
                print(f"Metin: {text}")

                # Kelime sayısını hesapla
                words = text.split()
                word_count += len(words)
                print(f"Toplam Kelime Sayısı: {word_count}")

            except sr.UnknownValueError:
                print("Anlaşılamadı, tekrar deneyin.")
            except sr.RequestError as e:
                print(f"API hatası: {e}")
            except Exception as e:
                print(f"Beklenmeyen hata: {e}")

# Anlık kelime sayımı için threading (isteğe bağlı)
thread = threading.Thread(target=recognize_and_count)
thread.start()
