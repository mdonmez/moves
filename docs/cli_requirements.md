# Moves CLI - Komut Satırı Arayüzü Gereksinimleri

Bu doküman, `app.py` dosyasında geliştirilecek olan `moves` komut satırı arayüzünün (CLI) tüm gereksinimlerini, komutlarını ve davranışlarını detaylandırmaktadır. Amaç, geliştiriciler için net, eksiksiz ve tutarlı bir referans kaynağı oluşturmaktır.

## 1. Giriş ve Amaç

`moves` CLI, kullanıcıların sunumlarını ve ilgili materyallerini (konuşmacı bilgileri, transkriptler vb.) verimli bir şekilde yönetmelerini sağlayan bir araçtır. Bu doküman, CLI'nin işlevselliğini ve `app.py` dosyasının oluşturulması sürecinde birincil referans olarak kullanılacaktır.

## 2. Genel Gereksinimler ve Kurulum

### 2.1. Teknik Gereksinimler
- **Kütüphane**: Komut satırı arayüzü `Typer` kütüphanesi kullanılarak geliştirilmelidir.
- **Hata Yönetimi**: Tüm komutlar, olası hataları yakalamak için `try-except` blokları ile sarmalanmalıdır. Kullanıcıya açık ve anlaşılır hata mesajları gösterilmelidir.
- **Çıktı Formatı**: Tüm çıktılar, renksiz, emojisiz ve sade bir metin formatında olmalıdır. Çıktılar, kullanıcıyı bilgilendirici, dengeli ve komutlar arası tutarlı olmalıdır.

### 2.2. Kurulum ve Bağımlılıklar
Gerekli Python kütüphaneleri bir `requirements.txt` dosyasında listelenmeli ve aşağıdaki komutla kurulabilmelidir:
```bash
pip install -r requirements.txt
```

## 3. Komut Referansı

CLI, `speaker`, `presentation` ve `settings` olmak üzere üç ana komut grubundan oluşur.

### 3.1. `speaker` Komut Grubu
Konuşmacı yönetimi ile ilgili işlemleri içerir.

---

#### **`speaker add`**
Yeni bir konuşmacı ekler.

- **Kullanım:** `python app.py speaker add <AD> <SUNUM_DOSYASI> <TRANSKRIPT_DOSYASI>`
- **Argümanlar:**
  | Argüman | Tip | Açıklama |
  |---|---|---|
  | `AD` | `str` | Konuşmacının adı (boşluk içeriyorsa tırnak içine alınmalıdır). |
  | `SUNUM_DOSYASI` | `Path` | Sunum dosyasının yolu (`.pptx`, `.pdf`). |
  | `TRANSKRIPT_DOSYASI`| `Path` | Transkript dosyasının yolu (`.txt`). |
- **Örnek:**
  ```bash
  python app.py speaker add "Ali Veli" "sunumlar/sunum.pptx" "transkriptler/metin.txt"
  ```
- **Başarılı Çıktı:**
  ```
  Başarılı: "Ali Veli" adlı konuşmacı eklendi (ID: <yeni_id>).
  ```
- **Hata Durumları:**
  - Dosya bulunamazsa: `Hata: Belirtilen dosya yolu bulunamadı: <dosya_yolu>`
  - Aynı isimde konuşmacı varsa: `Hata: "Ali Veli" adında bir konuşmacı zaten mevcut.`

---

#### **`speaker list`**
Sistemdeki tüm konuşmacıları listeler.

- **Kullanım:** `python app.py speaker list`
- **Başarılı Çıktı:**
  ```
  Sistemdeki Konuşmacılar
  ------------------------
  ID        AD
  --------  -----------
  <id_1>    Ali Veli
  <id_2>    Ayşe Yılmaz
  ------------------------
  Toplam: 2 Konuşmacı
  ```
- **Hata Durumları:**
  - Hiç konuşmacı yoksa: `Bilgi: Sistemde kayıtlı konuşmacı bulunmuyor.`

---

#### **`speaker process`**
Bir veya daha fazla konuşmacının verilerini işler.

- **Kullanım:** `python app.py speaker process [<KONUŞMACI_1> <KONUŞMACI_2>...] [--all]`
- **Argümanlar:**
  | Argüman | Tip | Açıklama |
  |---|---|---|
  | `KONUŞMACILAR` | `list[str]` | İşlenecek konuşmacıların ID veya adları (isteğe bağlı). |
- **Seçenekler:**
  | Seçenek | Açıklama |
  |---|---|
  | `--all` | Tüm konuşmacıları işlemek için kullanılır. |
- **Örnek:**
  ```bash
  python app.py speaker process "Ali Veli" <id_2> --all
  ```
- **Başarılı Çıktı:**
  ```
  İşlem başladı: 3 konuşmacı işleniyor...
  - "Ali Veli" başarıyla işlendi.
  - "Ayşe Yılmaz" başarıyla işlendi.
  - "Mehmet Kaya" başarıyla işlendi.
  İşlem tamamlandı.
  ```
- **Hata Durumları:**
  - LLM ayarları eksikse: `Hata: LLM modeli ve API anahtarı ayarlanmamış.`
  - Konuşmacı bulunamazsa: `Hata: "<ad>" ile eşleşen konuşmacı bulunamadı.`

---
*(Diğer `speaker` alt komutları - `edit`, `show`, `delete` - benzer detay seviyesinde bu yapıya uygun olarak tanımlanmalıdır.)*

### 3.2. `presentation` Komut Grubu
Sunum kontrolü ile ilgili işlemleri içerir.

---

#### **`presentation control`**
Belirtilen konuşmacı için sunum kontrolünü başlatır.

- **Kullanım:** `python app.py presentation control <KONUŞMACI>`
- **Argümanlar:**
  | Argüman | Tip | Açıklama |
  |---|---|---|
  | `KONUŞMACI` | `str` | Sunumu kontrol edilecek konuşmacının ID'si veya adı. |
- **Örnek:**
  ```bash
  python app.py presentation control "Ayşe Yılmaz"
  ```
- **Başarılı Çıktı:**
  ```
  Sunum kontrolü başlatılıyor: Ayşe Yılmaz
  Mikrofon: <varsayılan_mikrofon>
  Kontrolü sonlandırmak için CTRL+C tuşlarına basın.
  ```
- **Hata Durumları:**
  - Konuşmacı bulunamazsa: `Hata: "<ad>" ile eşleşen konuşmacı bulunamadı.`
  - `sections.json` dosyası eksikse: `Hata: Konuşmacı verileri işlenmemiş. Lütfen önce 'speaker process' komutunu çalıştırın.`

### 3.3. `settings` Komut Grubu
Uygulama ayarlarını yönetir.

---
*(`settings list`, `set`, `unset` komutları da yukarıdaki detaylı yapıda tanımlanmalıdır.)*


## 4. `app.py` İçin Uygulama Rehberi

Bu bölüm, yukarıdaki gereksinimlerin `app.py` dosyasında nasıl hayata geçirileceğine dair bir yol haritası sunar.

### 4.1. Proje Yapısı Önerisi
```
.
├── app.py                  # Ana CLI giriş noktası (Typer uygulaması)
├── requirements.txt        # Proje bağımlılıkları
└── moves/
    ├── __init__.py
    ├── speaker_manager.py    # Konuşmacı ile ilgili iş mantığı
    ├── settings_manager.py   # Ayarlar ile ilgili iş mantığı
    ├── presentation_controller.py # Sunum kontrolü mantığı
    └── ...                   # Diğer yardımcı modüller
```

### 4.2. `Typer` ile Komut Yapılandırması
`app.py`, komutları ve gruplarını tanımlamak için `Typer` kullanmalıdır. İş mantığı (`manager` modülleri) ile sunum katmanı (`app.py`) birbirinden ayrılmalıdır.

**`app.py` Örnek Yapısı:**
```python
import typer
from moves import speaker_manager

# Ana uygulama ve alt komut grupları oluşturulur
app = typer.Typer(help="Moves CLI - Sunum yönetim aracı.")
speaker_app = typer.Typer(name="speaker", help="Konuşmacı yönetimi komutları.")
app.add_typer(speaker_app)

@speaker_app.command("add")
def speaker_add(
    name: str = typer.Argument(..., help="Konuşmacının adı."),
    presentation_file: typer.Path = typer.Argument(..., help="Sunum dosyasının yolu."),
    transcript_file: typer.Path = typer.Argument(..., help="Transkript dosyasının yolu.")
):
    """Yeni bir konuşmacı ekler."""
    try:
        # İş mantığı manager modülünden çağrılır
        new_speaker = speaker_manager.add(name, presentation_file, transcript_file)
        # Çıktı bu katmanda formatlanır
        print(f"Başarılı: '{name}' adlı konuşmacı eklendi (ID: {new_speaker.id}).")
    except FileNotFoundError as e:
        print(f"Hata: Belirtilen dosya yolu bulunamadı: {e.filename}")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    app()
```
Bu yapı, `app.py` dosyasını sadece kullanıcı girdilerini ayrıştırmak ve sonuçları formatlamakla sorumlu tutar. Tüm temel işlemler (`dosya okuma/yazma`, `veri işleme`) ilgili `manager` sınıflarında gerçekleştirilir, bu da kodun test edilebilirliğini ve modülerliğini artırır.
