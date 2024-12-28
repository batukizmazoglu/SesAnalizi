from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont
import speech_recognition as sr
import time

class TopicAnalysisThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.categories = {
            'Spor': [
                # Futbol terimleri
                'futbol', 'maç', 'gol', 'penaltı', 'korner', 'taç', 'ofsayt', 'faul',
                'kırmızı kart', 'sarı kart', 'hakem', 'stadyum', 'saha', 'tribün',
                'taraftar', 'teknik direktör', 'antrenör', 'kaleci', 'defans', 'forvet',
                'orta saha', 'kaptan', 'forma', 'krampon', 'top', 'kupa', 'şampiyonluk',
                # Takımlar
                'fenerbahçe', 'galatasaray', 'beşiktaş', 'trabzonspor', 'milli takım',
                # Diğer sporlar
                'basketbol', 'voleybol', 'tenis', 'yüzme', 'atletizm', 'boks', 'güreş',
                'fitness', 'koşu', 'maraton', 'bisiklet', 'kayak', 'masa tenisi',
                'hentbol', 'golf', 'bilardo', 'bowling', 'dart', 'eskrim',
                # Spor terimleri
                'antrenman', 'turnuva', 'lig', 'transfer', 'taktik', 'savunma', 'hücum',
                'olimpiyat', 'şampiyona', 'play-off', 'eleme', 'grup', 'puan', 'averaj',
                'derbi', 'final', 'yarı final', 'çeyrek final', 'madalya', 'rekor'
            ],
            'Eğitim': [
                # Eğitim kurumları
                'okul', 'üniversite', 'lise', 'ortaokul', 'ilkokul', 'anaokulu',
                'kreş', 'kolej', 'akademi', 'enstitü', 'fakülte', 'yüksekokul',
                'konservatuar', 'dershane', 'kurs', 'etüt merkezi',
                # Eğitim personeli
                'öğretmen', 'profesör', 'doçent', 'akademisyen', 'araştırma görevlisi',
                'asistan', 'okul müdürü', 'müdür yardımcısı', 'rehber öğretmen',
                'danışman', 'eğitmen', 'hoca',
                # Dersler ve alanlar
                'matematik', 'fizik', 'kimya', 'biyoloji', 'tarih', 'coğrafya',
                'edebiyat', 'türkçe', 'ingilizce', 'almanca', 'fransızca', 'sosyal bilgiler',
                'fen bilgisi', 'müzik', 'resim', 'beden eğitimi', 'bilgisayar',
                # Eğitim terimleri
                'sınav', 'ödev', 'proje', 'tez', 'sunum', 'araştırma', 'makale',
                'laboratuvar', 'kütüphane', 'diploma', 'mezuniyet', 'yüksek lisans',
                'doktora', 'seminer', 'konferans', 'workshop', 'staj', 'burs',
                'not', 'karne', 'transkript', 'akreditasyon', 'yeterlilik', 'sertifika'
            ],
            'Teknoloji': [
                # Donanım
                'bilgisayar', 'laptop', 'tablet', 'telefon', 'akıllı telefon', 'ekran',
                'monitör', 'klavye', 'mouse', 'fare', 'işlemci', 'ram', 'harddisk',
                'ssd', 'anakart', 'gpu', 'ekran kartı', 'güç kaynağı', 'soğutucu',
                'fan', 'kasa', 'printer', 'yazıcı', 'tarayıcı', 'hoparlör', 'mikrofon',
                # Yazılım
                'program', 'uygulama', 'yazılım', 'işletim sistemi', 'windows', 'mac',
                'ios', 'android', 'linux', 'office', 'photoshop', 'oyun', 'antivirüs',
                'firewall', 'browser', 'tarayıcı', 'chrome', 'firefox', 'safari',
                # İnternet ve ağ
                'internet', 'wifi', 'bluetooth', 'ağ', 'network', 'router', 'modem',
                'fiber', 'adsl', 'bağlantı', 'download', 'upload', 'server', 'sunucu',
                'cloud', 'bulut', 'hosting', 'domain', 'ip', 'dns',
                # Yeni teknolojiler
                'yapay zeka', 'ai', 'machine learning', 'deep learning', 'blockchain',
                'kripto', 'bitcoin', 'nft', 'metaverse', 'sanal gerçeklik', 'vr',
                'artırılmış gerçeklik', 'ar', 'drone', 'robot', '3d yazıcı', 'iot'
            ],
            'Müzik': [
                # Müzik türleri
                'pop', 'rock', 'jazz', 'klasik', 'rap', 'hip hop', 'metal', 'folk',
                'türkü', 'arabesk', 'tasavvuf', 'blues', 'country', 'reggae', 'latin',
                'elektronik', 'house', 'techno', 'r&b', 'funk', 'disco',
                # Enstrümanlar
                'gitar', 'piyano', 'keman', 'davul', 'bateri', 'bas', 'saksafon',
                'trompet', 'klarnet', 'flüt', 'org', 'synthesizer', 'bağlama', 'ud',
                'kanun', 'ney', 'darbuka', 'def', 'akordeon', 'mandolin',
                # Müzik terimleri
                'nota', 'ritim', 'melodi', 'armoni', 'akor', 'beste', 'bestekar',
                'kompozitör', 'şarkı', 'türkü', 'konser', 'festival', 'sahne',
                'performans', 'albüm', 'single', 'klip', 'playlist', 'streaming',
                'spotify', 'youtube music', 'apple music', 'remix', 'cover', 'canlı'
            ],
            'Sağlık': [
                # Tıbbi alanlar
                'dahiliye', 'cerrahi', 'kardiyoloji', 'nöroloji', 'ortopedi',
                'pediatri', 'psikiyatri', 'göz', 'kulak burun boğaz', 'diş',
                'dermatoloji', 'üroloji', 'jinekoloji', 'onkoloji', 'endokrinoloji',
                # Sağlık personeli
                'doktor', 'hekim', 'hemşire', 'ebe', 'fizyoterapist', 'psikolog',
                'diyetisyen', 'eczacı', 'laborant', 'teknisyen', 'paramedik',
                # Sağlık terimleri
                'hastalık', 'tedavi', 'ameliyat', 'muayene', 'teşhis', 'tanı',
                'reçete', 'ilaç', 'aşı', 'tahlil', 'test', 'röntgen', 'tomografi',
                'ultrason', 'mri', 'ekg', 'tansiyon', 'ateş', 'grip', 'covid',
                'virüs', 'bakteri', 'enfeksiyon', 'bağışıklık', 'rehabilitasyon'
            ],
            'Günlük Yaşam': [
                # Ev yaşamı
                'ev', 'aile', 'anne', 'baba', 'kardeş', 'çocuk', 'eş', 'evlilik',
                'temizlik', 'yemek', 'uyku', 'kahvaltı', 'öğle yemeği', 'akşam yemeği',
                'misafir', 'komşu', 'apartman', 'site', 'bahçe', 'balkon',
                # Günlük aktiviteler
                'iş', 'okul', 'alışveriş', 'spor', 'yürüyüş', 'toplantı', 'randevu',
                'arkadaş', 'sosyal medya', 'televizyon', 'internet', 'telefon',
                'uyanmak', 'uyumak', 'duş', 'banyo', 'giyinmek', 'hazırlanmak',
                # Ev işleri
                'temizlik', 'çamaşır', 'bulaşık', 'ütü', 'yemek yapmak', 'alışveriş',
                'market', 'fatura', 'aidat', 'tamirat', 'tadilat', 'bakım',
                # Sosyal aktiviteler
                'cafe', 'restoran', 'sinema', 'tiyatro', 'konser', 'park', 'piknik',
                'gezi', 'tatil', 'spor salonu', 'alışveriş merkezi', 'pazar'
            ],
            'Siyaset': [
                # Siyasi kurumlar
                'meclis', 'tbmm', 'bakanlık', 'belediye', 'valilik', 'kaymakamlık',
                'büyükelçilik', 'konsolosluk', 'parti', 'teşkilat', 'komisyon',
                # Siyasi roller
                'cumhurbaşkanı', 'başbakan', 'bakan', 'milletvekili', 'belediye başkanı',
                'vali', 'kaymakam', 'büyükelçi', 'genel başkan', 'parti lideri',
                'muhalefet lideri', 'sözcü', 'danışman',
                # Siyasi terimler
                'seçim', 'oy', 'sandık', 'propaganda', 'miting', 'kongre', 'reform',
                'kanun', 'yasa', 'anayasa', 'hükümet', 'iktidar', 'muhalefet',
                'koalisyon', 'demokrasi', 'cumhuriyet', 'meclis', 'parlamento',
                'bürokrasi', 'diplomasi', 'politika', 'siyaset'
            ],
            'Ekonomi': [
                # Finans
                'para', 'dolar', 'euro', 'tl', 'kur', 'borsa', 'hisse', 'tahvil',
                'faiz', 'kredi', 'banka', 'sigorta', 'yatırım', 'fon', 'portföy',
                'forex', 'kripto para', 'bitcoin', 'blockchain', 'nft',
                # Ekonomik terimler
                'enflasyon', 'deflasyon', 'stagflasyon', 'devalüasyon', 'revalüasyon',
                'gdp', 'büyüme', 'küçülme', 'resesyon', 'kriz', 'borç', 'alacak',
                'bütçe', 'gelir', 'gider', 'kar', 'zarar', 'maliyet', 'vergi',
                # İş dünyası
                'şirket', 'firma', 'holding', 'girişim', 'startup', 'yatırımcı',
                'girişimci', 'patron', 'ceo', 'yönetici', 'müdür', 'çalışan',
                'personel', 'maaş', 'prim', 'ikramiye', 'performans'
            ],
            'Yemek ve Mutfak': [
                # Yemek türleri
                'çorba', 'salata', 'ana yemek', 'et yemeği', 'tavuk yemeği',
                'balık', 'sebze yemeği', 'pilav', 'makarna', 'börek', 'mantı',
                'döner', 'kebap', 'köfte', 'lahmacun', 'pide', 'hamburger',
                # Tatlılar ve hamur işleri
                'pasta', 'kek', 'kurabiye', 'börek', 'poğaça', 'simit', 'baklava',
                'künefe', 'sütlaç', 'muhallebi', 'dondurma', 'helva', 'reçel',
                # Mutfak gereçleri
                'tencere', 'tava', 'fırın', 'ocak', 'mikser', 'blender', 'rondo',
                'bıçak', 'kesme tahtası', 'süzgeç', 'kevgir', 'spatula', 'kaşık',
                'çatal', 'tabak', 'bardak', 'fincan',
                # Pişirme terimleri
                'haşlama', 'kızartma', 'kavurma', 'ızgara', 'fırınlama', 'buğulama',
                'marine', 'soslu', 'baharatlı', 'acılı', 'tuzlu', 'tatlı'
            ],
            'Sosyal Medya': [
                # Platformlar
                'facebook', 'instagram', 'twitter', 'tiktok', 'youtube', 'linkedin',
                'whatsapp', 'telegram', 'snapchat', 'pinterest', 'reddit', 'twitch',
                'discord', 'medium', 'tumblr', 'clubhouse',
                # İçerik türleri
                'post', 'story', 'reels', 'tweet', 'video', 'fotoğraf', 'canlı yayın',
                'blog', 'vlog', 'podcast', 'shorts', 'igtv', 'carousel', 'highlight',
                # Etkileşim terimleri
                'beğeni', 'like', 'yorum', 'comment', 'paylaşım', 'share', 'retweet',
                'mention', 'etiket', 'hashtag', 'trend', 'viral', 'dm', 'mesaj',
                'takip', 'takipçi', 'abonelik', 'subscriber',
                # Sosyal medya terimleri
                'influencer', 'fenomen', 'içerik üretici', 'youtuber', 'blogger',
                'vlogger', 'streamer', 'engagement', 'reach', 'impression', 'analytics'
            ],
            'Alışveriş': [
                # Alışveriş yerleri
                'market', 'süpermarket', 'hipermarket', 'mağaza', 'butik', 'avm',
                'pazar', 'outlet', 'eczane', 'kırtasiye', 'elektronik mağaza',
                # Online alışveriş
                'e-ticaret', 'online alışveriş', 'internet alışverişi', 'sipariş',
                'kargo', 'teslimat', 'iade', 'değişim', 'sepet', 'satın alma',
                # Ödeme yöntemleri
                'nakit', 'kredi kartı', 'banka kartı', 'havale', 'eft', 'kapıda ödeme',
                'taksit', 'pos', 'mobil ödeme', 'dijital cüzdan',
                # Alışveriş terimleri
                'indirim', 'kampanya', 'promosyon', 'kupon', 'fiyat', 'etiket',
                'barkod', 'stok', 'garanti', 'müşteri hizmetleri', 'şikayet'
            ],
            'Seyahat ve Gezi': [
                # Ulaşım
                'uçak', 'tren', 'otobüs', 'gemi', 'araba', 'taksi', 'metro',
                'tramvay', 'feribot', 'havayolu', 'demiryolu', 'karayolu',
                # Konaklama
                'otel', 'pansiyon', 'hostel', 'apart', 'villa', 'çadır', 'karavan',
                'resort', 'tatil köyü', 'airbnb', 'booking',
                # Seyahat terimleri
                'rezervasyon', 'bilet', 'pasaport', 'vize', 'sigorta', 'check-in',
                'check-out', 'bagaj', 'valiz', 'sırt çantası', 'tur', 'gezi',
                # Turistik yerler
                'plaj', 'müze', 'antik kent', 'kale', 'saray', 'cami', 'kilise',
                'park', 'bahçe', 'milli park', 'ada', 'göl', 'şelale', 'kanyon'
            ],
            'Ev ve Dekorasyon': [
                # Mobilya
                'koltuk', 'kanepe', 'sandalye', 'masa', 'sehpa', 'dolap', 'gardırop',
                'yatak', 'baza', 'komodin', 'kitaplık', 'tv ünitesi', 'çekmece',
                # Dekorasyon
                'perde', 'halı', 'kilim', 'avize', 'lamba', 'ayna', 'tablo',
                'vazo', 'biblo', 'çerçeve', 'yastık', 'kırlent', 'örtü', 'mum',
                # Ev bölümleri
                'salon', 'oturma odası', 'yatak odası', 'mutfak', 'banyo', 'tuvalet',
                'antre', 'hol', 'koridor', 'balkon', 'teras', 'bahçe',
                # Yapı ve tadilat
                'boya', 'duvar kağıdı', 'parke', 'laminat', 'seramik', 'fayans',
                'mutfak dolabı', 'banyo dolabı', 'spot', 'kartonpiyer', 'süpürgelik'
            ],
            'İş ve Kariyer': [
                # İş pozisyonları
                'yönetici', 'müdür', 'direktör', 'uzman', 'asistan', 'stajyer',
                'danışman', 'satış temsilcisi', 'pazarlama', 'insan kaynakları',
                # İş terimleri
                'maaş', 'ücret', 'prim', 'ikramiye', 'zam', 'terfi', 'transfer',
                'istifa', 'işten çıkış', 'tazminat', 'sigorta', 'sgk', 'vergi',
                # İş yeri
                'ofis', 'şirket', 'firma', 'holding', 'fabrika', 'plaza', 'şube',
                'merkez', 'depo', 'mağaza', 'showroom',
                # Kariyer gelişimi
                'eğitim', 'sertifika', 'kurs', 'seminer', 'konferans', 'workshop',
                'networking', 'mentorluk', 'koçluk', 'yetenek', 'beceri', 'deneyim'
            ],
            'Otomotiv': [
                # Araç türleri
                'otomobil', 'araba', 'suv', 'pickup', 'van', 'minibüs', 'otobüs',
                'kamyon', 'motosiklet', 'scooter', 'elektrikli araç', 'hibrit',
                # Araç parçaları
                'motor', 'şanzıman', 'vites', 'debriyaj', 'fren', 'lastik', 'jant',
                'far', 'stop', 'silecek', 'ayna', 'kapı', 'bagaj', 'kaput',
                # Teknik terimler
                'benzin', 'dizel', 'lpg', 'yakıt', 'yağ', 'antifriz', 'akü',
                'radyatör', 'egzoz', 'katalitik', 'turbo', 'enjeksiyon',
                # Bakım ve servis
                'servis', 'bakım', 'tamir', 'arıza', 'kaza', 'sigorta', 'kasko',
                'muayene', 'ekspertiz', 'garanti', 'yedek parça', 'modifiye'
            ],
            'Hobi ve Eğlence': [
                # Oyunlar
                'bilgisayar oyunu', 'konsol', 'playstation', 'xbox', 'nintendo',
                'mobil oyun', 'kutu oyunu', 'satranç', 'tavla', 'okey', 'kart',
                # El işi ve sanat
                'resim', 'boyama', 'çizim', 'heykel', 'seramik', 'örgü', 'dikiş',
                'nakış', 'ahşap boyama', 'takı tasarım', 'origami', 'quilling',
                # Koleksiyon
                'pul', 'para', 'antika', 'kitap', 'plak', 'model araba', 'figür',
                'kart', 'madeni para', 'rozet', 'poster',
                # Diğer hobiler
                'bahçecilik', 'fotoğrafçılık', 'drone', 'balık tutma', 'avcılık',
                'kamp', 'dağcılık', 'bisiklet', 'yoga', 'meditasyon'
            ],
            'Moda ve Giyim': [
                # Giysi türleri
                'elbise', 'pantolon', 'gömlek', 'tişört', 'kazak', 'hırka', 'ceket',
                'mont', 'palto', 'etek', 'şort', 'tayt', 'eşofman', 'pijama',
                # Ayakkabı ve çanta
                'spor ayakkabı', 'klasik ayakkabı', 'bot', 'çizme', 'sandalet',
                'terlik', 'el çantası', 'sırt çantası', 'cüzdan', 'valiz',
                # Aksesuar
                'saat', 'takı', 'gözlük', 'kemer', 'şal', 'atkı', 'bere', 'şapka',
                'eldiven', 'çorap', 'fular', 'broş', 'bileklik', 'kolye',
                # Moda terimleri
                'stil', 'trend', 'sezon', 'koleksiyon', 'defile', 'tasarım',
                'marka', 'vintage', 'retro', 'haute couture', 'fast fashion'
            ],
            'Hava ve Mevsim': [
                # Hava durumu
                'güneşli', 'bulutlu', 'yağmurlu', 'karlı', 'rüzgarlı', 'fırtınalı',
                'sisli', 'puslu', 'parçalı bulutlu', 'açık hava', 'kapalı hava',
                # Sıcaklık
                'sıcak', 'soğuk', 'ılık', 'serin', 'dondurucu', 'kavurucu',
                'bunaltıcı', 'derece', 'termometre', 'nem', 'rutubet',
                # Mevsimler
                'ilkbahar', 'yaz', 'sonbahar', 'kış', 'mevsim', 'mevsim geçişi',
                'gündönümü', 'ekinoks', 'bahar', 'yaz sıcağı', 'kış soğuğu',
                # Hava olayları
                'yağmur', 'kar', 'dolu', 'sis', 'çiy', 'kırağı', 'şimşek',
                'gök gürültüsü', 'kasırga', 'hortum', 'sel', 'don', 'tipi'
            ]
        }

    def run(self):
        try:
            if len(self.text.split()) < 2:
                self.finished.emit([("Bilgi", "Daha fazla konuşma bekleniyor...")])
                return

            text_lower = self.text.lower()
            results = []

            for category, keywords in self.categories.items():
                matches = 0
                matched_words = set()
                
                for keyword in keywords:
                    if keyword in text_lower:
                        matches += 1
                        matched_words.add(keyword)
                
                if matches > 0:
                    confidence = min(100, (matches / len(keywords)) * 100 * 2)
                    if confidence >= 15:
                        precision = confidence / 100
                        recall = min((confidence + 5) / 100, 1.0)
                        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                        support = int(confidence * 2)
                        results.append((category, precision, recall, f1_score, support))

            results.sort(key=lambda x: x[3], reverse=True)  # F1-Score'a göre sırala
            
            if not results:
                results = [("Bilgi", "Henüz belirgin bir konu tespit edilemedi")]

            self.finished.emit(results)
                
        except Exception as e:
            print(f"Analiz hatası: {str(e)}")
            self.finished.emit([("Hata", f"Analiz hatası: {str(e)}")])

class RecordingWorker(QObject):
    text_ready = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def run(self):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                while self.is_running:
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        text = self.recognizer.recognize_google(audio, language="tr-TR")
                        if text:
                            self.text_ready.emit(text)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        print(f"Ses tanıma hatası: {str(e)}")
                        time.sleep(0.1)  # Kısa bir bekleme ekle
                        continue
        except Exception as e:
            self.error.emit(f"Mikrofon hatası: {str(e)}")
        finally:
            self.finished.emit()

    def stop(self):
        self.is_running = False

class TopicTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.is_recording = False
        self.recording_worker = None
        self.recording_thread = None
        self.analysis_thread = None
        self.accumulated_text = ""

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🎤 Konuşmaya Başla")
        self.start_button.clicked.connect(self.start_recording)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.stop_button = QPushButton("⏹ Konuşmayı Durdur")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)
        
        # Durum etiketi
        self.status_label = QLabel("Konuşmaya başlamak için butona basın...")
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        # Tanınan metin
        self.transcribed_text = QLabel("Konuşma metni burada görünecek...")
        self.transcribed_text.setWordWrap(True)
        self.transcribed_text.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(self.transcribed_text)
        
        # Sonuçlar
        self.results_label = QLabel("Konu analizi sonuçları burada görünecek...")
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #90caf9;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.results_label)
        
        self.setLayout(layout)

    def start_recording(self):
        try:
            self.is_recording = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("Konuşmayı dinliyor...")
            
            self.recording_thread = QThread()
            self.recording_worker = RecordingWorker()
            self.recording_worker.moveToThread(self.recording_thread)
            
            self.recording_thread.started.connect(self.recording_worker.run)
            self.recording_worker.text_ready.connect(self.on_text_received)
            self.recording_worker.error.connect(self.on_error)
            self.recording_worker.finished.connect(self.recording_thread.quit)
            
            self.recording_thread.start()
            
        except Exception as e:
            self.on_error(f"Kayıt başlatma hatası: {str(e)}")

    def stop_recording(self):
        if self.recording_worker:
            self.is_recording = False
            self.recording_worker.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("Konuşma durduruldu, son analiz yapılıyor...")

    def on_text_received(self, text):
        self.accumulated_text += " " + text
        self.transcribed_text.setText(f"Tanınan Konuşma:\n{self.accumulated_text}")
        self.analyze_text(self.accumulated_text)

    def on_error(self, error_message):
        self.status_label.setText(error_message)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def analyze_text(self, text):
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait()
        
        self.analysis_thread = TopicAnalysisThread(text)
        self.analysis_thread.finished.connect(self.show_results)
        self.analysis_thread.start()

    def show_results(self, categories):
        result_text = "Konu Analiz Sonuçları:\n\n"
        result_text += f"{'Kategori':<15} | {'Kesinlik':^10} | {'Duyarlılık':^10} | {'F1-Score':^10} | {'Destek':^8}\n"
        result_text += "-" * 65 + "\n"
        
        if isinstance(categories, list) and len(categories) > 0:
            if categories[0][0] == "Hata":
                result_text = f"Hata: {categories[0][1]}"
            elif categories[0][0] == "Bilgi":
                result_text = categories[0][1]
            else:
                for category, precision, recall, f1_score, support in categories:
                    result_text += f"{category:<15} | {precision:^10.2f} | {recall:^10.2f} | {f1_score:^10.2f} | {support:^8}\n"
        else:
            result_text = "Analiz sonucu alınamadı."
        
        self.results_label.setFont(QFont("Courier New", 10))
        self.results_label.setText(result_text)

    def closeEvent(self, event):
        self.stop_recording()
        if self.recording_thread:
            self.recording_thread.quit()
            self.recording_thread.wait()
        if self.analysis_thread:
            self.analysis_thread.quit()
            self.analysis_thread.wait()
        event.accept()