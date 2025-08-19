moves CLI, moves uygulamasını kullanmak için hızlı, basit ve kullanımı kolay bir komut satırı arayüzüdür.

İşte CLI hiyerarşisi:

# Konuşmacı yönetimi

moves speaker add <name> <source-presentation> <source-transcript>
moves speaker edit <speaker> <source-presentation> <source-transcript>
moves speaker list
moves speaker show <speaker>
moves speaker process <speaker1> [<speaker2> ... <speakerN>] (--all)
moves speaker delete <speaker>

# Sunum kontrolü

moves presentation control <speaker>

# Ayarlar

moves settings list
moves settings set <key> <value>
moves settings unset <key>

---

Genel komut gereksinimleri şunlardır:

- Komutlar, doğru bir şekilde çalışabilmesi için gerekli tüm argümanları içermelidir.
- CLI, kullanıcı dostu bir deneyim sağlamak için anlamlı hata mesajları göstermelidir.
- Komutlar try-catch blokları ve if koşulları ile sarılmalıdır, bu en üst high-level hata yakalama sağlar ve alt modüllerin hatalarını daha önceden yakalamayı, eğer yakalanamazsa da alt modüldeki hatayı daha iyi yönetmeyi mümkün kılar.
- Typer kullanılmalıdır, type-safe için mümkün olduğunda en üstten parametre tip filtrelemesi yapılmalıdır.
- Her çıktı, çok abartılı formatlama olmayacak ama çok da basit olmayacak şekilde, renksiz, emojisiz ve sade bir metin formatında olmalıdır. Kullanıcıyı bilgilendirmeli, dengeli ve anlaşılır olmalıdır. Sade, minimal bir tasarım benimsenmelidir. Komutlar arası tutarlılık sağlanmalıdır.

---

Komut spesifik açıklamalar:

# speaker (Konuşmacı yönetimi)

Bu, sistemdeki konuşmacıları yönetmek için kullanılan komutları içerir:

- speaker add: Yeni bir konuşmacı ekler.
- speaker edit: Var olan bir konuşmacıyı düzenler.
- speaker list: Tüm konuşmacıları listeler.
- speaker show: Belirli bir konuşmacının ayrıntılarını gösterir.
- speaker process: Belirli bir konuşmacıyı işler.
- speaker delete: Belirli bir konuşmacıyı siler.

Alt komutlarının detayları şöyledir:

## speaker add

Yeni bir konuşmacı eklemek için kullanılır. Gerekli argümanlar şunlardır:

- `<name>`: [str] -> Konuşmacının adı.
- `<source-presentation>`: [Path] -> Konuşmacı sunum dosyası.
- `<source-transcript>`: [Path] -> Konuşmacının bağlı olduğu transkript dosyası.

İşleyiş:

1. speaker_manager'dan add fonksiyonu verilen parametrelerle çağrılır.

## speaker edit

Var olan bir konuşmacıyı düzenlemek için kullanılır. Gerekli argümanlar şunlardır:

- `<speaker>`: [str] -> Konuşmacının adı ve ID'si.
- `<source-presentation>`: Opsiyonel [Path] -> Konuşmacı sunum dosyası.
- `<source-transcript>`: Opsiyonel [Path] -> Konuşmacının bağlı olduğu transkript dosyası.

İşleyiş:

1. speaker_manager'dan resolve fonksiyonu <speaker> ile çağrılır, eğer tek bir Speaker eşleşirse devam edilir.
2. Parametrelere bakılır, eğer iki düzenlenebilir parametreden en az biri varsa devam edilir.
3. speaker_manager'dan edit, verilen parametrelerle çağrılır.

## speaker list

Sisteme kayıtlı tüm konuşmacıları listeler.

İşleyiş:

1. speaker_manager'dan list fonksiyonu çağrılır.

## speaker show

Var olan bir konuşmacının detaylarını görüntülemek için kullanılır. Gerekli argümanlar şunlardır:

- `<speaker>`: [str] -> Konuşmacının adı ve ID'si.

İşleyiş:

1. speaker_manager'dan resolve fonksiyonu <speaker> ile çağrılır, eğer tek bir Speaker eşleşirse devam edilir.
2. Speaker nesnesinin detayları görüntülenir.

## speaker process

Var olan konuşmacı(lar)'ı işlemek için kullanılır. Gerekli argümanlar şunlardır:

- `<speakers>`: [list] -> İşlenecek konuşmacıların adı veya ID'si.
- `--all`: Tüm konuşmacıları işlemek için kullanılır.

İşleyiş:

1. settings_manager'dan llm_model ve llm_api_key alınmaya çalışır, başarılıysa devam edilir.
2. Eğer `--all` bayrağı verilmişse, speaker_manager'dan list fonksiyonu çağrılır ve tüm konuşmacılar işlenir speaker_manager'dan process fonksiyonu tüm konuşmacı listesiyle çağrılır.
3. <speakers> listesi boşluklarla ayrılmış bir şekilde liste formatına çevrilir, her bir liste elemanı için speaker_manager'dan resolve fonksiyonu çağrılır ve sonuç olarak bir list[Speaker] beklenir, ardından speaker_manager'dan process fonksiyonu bu liste ile çağrılır.

## speaker delete

Var olan bir konuşmacını silmek için kullanılır. Gerekli argümanlar şunlardır:

- `<speaker>`: [str] -> Silinecek konuşmacının adı ve ID'si.

İşleyiş:

1. speaker_manager'dan resolve fonksiyonu <speaker> ile çağrılır, eğer tek bir Speaker eşleşirse devam edilir.
2. speaker_manager'dan delete fonksiyonu çağrılır.

---

# presentation (Sunum işlemleri)

Bu, sistemdeki konuşmacıların sunumlarını yönetmek için kullanılan tek bir komut içerir:

- presentation control: Sunum kontrolü başlatır.

Alt komutlarının detayları şöyledir:

## presentation control

Sunum kontrolü başlatmak için kullanılır. Gerekli argümanlar şunlardır:

- `<speaker>`: [str] -> Sunumu kontrol edilecek kişinin adı veya ID'si.

İşleyiş:

1. settings_manager'dan varsa mikrofon değeri alınır.
2. speaker_manager'dan resolve fonksiyonu <speaker> ile çağrılır, eğer tek bir Speaker eşleşirse devam edilir.
3. Speaker için data_handler kullanılarak konuşmacının dizininde sections.json dosyası aranır, bulunursa devam edilir.
4. section_producer ile json dosyası list[Section] formatına dönüştürülür.
5. presentation_controller ile sunum kontrolü başlatılır.

---

# settings (Ayarlar yönetimi)

Bu, sistemdeki ayarları yönetmek için kullanılan komutları içerir:

- settings list: Tüm ayarları ve mikrofonları listeler.
- settings set: Belirli bir ayarı düzenler.
- settings unset: Belirli bir ayarı kaldırır.

Alt komutlarının detayları şöyledir:

## settings list

Tüm ayarları ve mikrofonları listeler.

İşleyiş:

1. settings_manager'dan list fonksiyonu çağrılır.
2. sounddevice'dan query devices kind input ile mikrofonlar alınır.
3. Mikrofonlar ve ayarlar bir arada listelenir.

## settings set

Belirli bir ayarı düzenler. Gerekli argümanlar şunlardır:

- `<key>`: [str] -> Düzenlenecek ayarın anahtarı.
- `<value>`: [str] -> Ayarın yeni değeri.

1. settings_manager'dan set fonksiyonu verilen parametrelerle çağrılır.

## settings unset

Belirli bir ayarı kaldırır. Gerekli argümanlar şunlardır:

- `<key>`: [str] -> Kaldırılacak ayarın anahtarı.

İşleyiş:

1. settings_manager'dan unset fonksiyonu verilen parametrelerle çağrılır.
