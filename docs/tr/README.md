# moves Belgeleri

**moves**, canlı sunumlar sırasında sorunsuz ses kontrollü slayt geçişi sağlayan bir AI‑destekli sunum kontrol sistemidir. Sistem, konuşmacının ne söylediğine göre otomatik olarak sunum slaytlarını yönlendirmek için gelişmiş konuşma tanıma, doğal dil işleme ve makine öğrenimini kullanır.

## İçindekiler

- [Getting Started](./getting-started.md) - Kurulum, ayarlama ve ilk adımlar
- [Architecture Overview](./architecture.md) - Sistem tasarımı, bileşenler ve veri akışı
- [Core Components](./components/) - Sistem bileşenlerinin ayrıntılı belgeleri
  - [Presentation Controller](./components/presentation-controller.md) - Gerçek zamanlı ses yönlendirme motoru
  - [Speaker Manager](./components/speaker-manager.md) - Konuşmacı profili ve veri yönetimi
  - [Settings Editor](./components/settings-editor.md) - Yapılandırma yönetimi
  - [Section Producer](./components/section-producer.md) - AI‑destekli içerik üretimi
  - [Similarity Calculator](./components/similarity-calculator.md) - Konuşma eşleştirme algoritmaları
  - [Chunk Producer](./components/chunk-producer.md) - Metin bölütleme ve işleme
- [Data Models](./data-models.md) - Çekirdek veri yapıları ve tipleri
- [Command Line Interface](./cli.md) - Tam CLI referansı ve kullanım örnekleri
- [Configuration](./configuration.md) - Ayarlar, şablonlar ve ortam kurulumu
- [Machine Learning Models](./ml-models.md) - Gömme modelleri, STT ve AI entegrasyonu
- [Utilities](./utilities.md) - Destekleyici modüller ve yardımcı fonksiyonlar
- [Development Guide](./development.md) - Katkıda bulunma, test etme ve sistemi genişletme
- [Troubleshooting](./troubleshooting.md) - Yaygın sorunlar ve çözümler
- [API Reference](./api-reference.md) - İç API belgeleri

## Hızlı Başlangıç

```bash
# Bağımlılıkları kur
uv sync

# Bir konuşmacı profili ekle
uv run python app.py speaker add "John Doe" presentation.pdf transcript.pdf

# LLM ayarlarını yapılandır
uv run python app.py settings set model "gemini/gemini-2.0-flash"
uv run python app.py settings set key "your-api-key"

# AI yönlendirmesi için konuşmacı verilerini işle
uv run python app.py speaker process "John Doe"

# Ses kontrollü canlı sunumu başlat
uv run python app.py presentation control "John Doe"
```

## Temel Özellikler

- **Ses Kontrollü Geçiş**: Konuşma tanımaya dayalı gerçek zamanlı slayt geçişi
- **AI‑Destekli İçerik Eşlemesi**: Konuşmayı sunum içeriğiyle akıllı hizalama
- **Çok‑Modal Benzerlik**: Doğrusal ve fonetik eşleşmeyi birleştirerek hassas geçiş
- **Esnek Konuşmacı Yönetimi**: Birden çok konuşmacı ve sunum desteği
- **Gerçek Zamanlı Ses İşleme**: Düşük gecikmeli konuşma tanıma ve işleme
- **Hibrit Benzerlik Skoru**: Güçlü konuşma‑içerik eşleşmesi için gelişmiş algoritmalar
- **CLI Arayüzü**: Sistem yönetimi için kapsamlı komut satırı araçları

## Mimari Öne Çıkanlar

- **Modüler Tasarım**: Özel bileşenlerle net sorumluluk ayrımı
- **Gerçek Zamanlı İşleme**: Yanıt verebilir performans için çok iş parçacıklı mimari
- **Makine Öğrenimi Entegrasyonu**: Yerel STT modelleri ve bulut tabanlı LLM hizmetleri
- **Yapılandırılabilir Boru Hattı**: Esnek ayarlar ve özelleştirilebilir işleme parametreleri
- **Veri Kalıcılığı**: Konuşmacılar, bölümler ve ayarlar için yapılandırılmış veri depolama

## Sistem Gereksinimleri

- **Python**: 3.13+
- **Bağımlılıklar**: Tam liste için [pyproject.toml](../pyproject.toml) dosyasına bakın
- **Ses**: Konuşma tanıma için mikrofon girişi
- **Depolama**: Veri ve model depolama için yerel dosya sistemi
- **Ağ**: İşleme sırasında LLM API çağrıları için internet bağlantısı

## Proje Yapısı

```
moves/
├── app.py                           # Ana CLI uygulaması
├── pyproject.toml                   # Proje yapılandırması ve bağımlılıklar
├── src/
│   ├── core/                        # Çekirdek sistem bileşenleri
│   │   ├── presentation_controller.py  # Ses yönlendirme motoru
│   │   ├── speaker_manager.py         # Konuşmacı veri yönetimi
│   │   ├── settings_editor.py         # Yapılandırma yönetimi
│   │   └── components/                 # İşleme bileşenleri
│   │       ├── section_producer.py       # AI içerik üretimi
│   │       ├── similarity_calculator.py  # Konuşma eşleştirme
│   │       ├── chunk_producer.py         # Metin bölütleme
│   │       ├── ml_models/                # Ön‑eğitimli modeller
│   │       └── similarity_units/         # Eşleştirme algoritmaları
│   ├── data/                        # Veri modelleri ve şablonlar
│   │   ├── models.py                   # Çekirdek veri yapıları
│   │   ├── settings_template.yaml     # Varsayılan yapılandırma
│   │   └── llm_instruction.md         # AI işleme talimatları
│   └── utils/                       # Yardımcı modüller
│       ├── data_handler.py            # Dosya sistemi işlemleri
│       ├── text_normalizer.py         # Metin ön işleme
│       ├── logger.py                  # Kayıt (log) yardımcıları
│       └── id_generator.py           # Benzersiz kimlik oluşturma
└── docs/                           # Dokümantasyon (bu dizin)
```

## Kullanım Senaryoları

- **Canlı Sunumlar**: Eller serbest geçişle profesyonel sunumlar
- **Eğitim Ortamları**: Ders ve öğretim senaryoları
- **Konferans Konuşmaları**: Kesintisiz slayt kontrolüyle halka açık konuşmalar
- **Eğitim Oturumları**: Kurumsal ve akademik eğitim sunumları
- **Uzaktan Sunumlar**: Sanal toplantılar ve webinarlar

## Dokümantasyon Durumu

Bu dokümantasyon seti artık tamamlanmıştır ve moves uygulamasının kapsamlı bir kapsama sahiptir:

- ✅ **İndeks** - Bu genel bakış belgesi
- ✅ **Getting Started** - Kurulum ve temel kullanım
- ✅ **Architecture** - Sistem tasarımı ve bileşen özeti
- ✅ **Component Documentation** - Ayrıntılı bileşen dokümantasyonu
  - ✅ PresentationController - Ses kontrollü yönlendirme
  - ✅ SpeakerManager - Konuşmacı ve sunum yönetimi
  - ✅ SettingsEditor - Yapılandırma yönetimi
  - ✅ SectionProducer - AI‑destekli içerik işleme
  - ✅ SimilarityCalculator - Hibrit benzerlik eşleştirme
  - ✅ ChunkProducer - İçerik bölütleme
- ✅ **Data Models** - Çekirdek veri yapıları ve ilişkileri
- ✅ **CLI Reference** - Tam komut satırı arayüzü belgeleri
- ✅ **Configuration** - Ayarlar ve yapılandırma kılavuzu
- ✅ **Utilities** - Destekleyici modüller ve yardımcı fonksiyonlar
- ✅ **ML Models** - Makine öğrenimi entegrasyonu ve model yönetimi
- ✅ **API Reference** - Tam API dokümantasyonu
- ✅ **Development** - Geliştirici katkı rehberi
- ✅ **Troubleshooting** - Yaygın sorunlar ve çözümler

## Sonraki Adımlar

1. **Yeni Kullanıcılar**: [Getting Started Guide](./getting-started.md) ile başlayın
2. **Geliştiriciler**: [Architecture Overview](./architecture.md) sayfasını inceleyin
3. **Katkıda Bulunanlar**: [Development Guide](./development.md) bölümüne bakın
4. **Entegrasyon**: [API Reference](./api-reference.md) sayfasını kontrol edin
