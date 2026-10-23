# Ne Yiyorum? — Görüntü İşleme Tabanlı Beslenme Takip Sistemi

Yemek fotoğrafından besin değeri çıkaran ve günlük kalori takibi yapan masaüstü/web uygulaması.
Kullanıcı bir fotoğraf yüklüyor, sistem yemeği tanıyıp kalori ve makro besin değerlerini hesaplıyor,
kişisel hedefe göre günlük takibi tutuyor.

**Tekirdağ Namık Kemal Üniversitesi — Bilgisayar Mühendisliği Bitirme Projesi, 2025/2026**

---

## Ne yapar?

| | |
|---|---|
| **Yemek tanıma** | YOLOv8 ile 30 kategoride **%93,4 doğruluk**, görüntü başına ~5 ms |
| **Besin hesabı** | Tanınan yemeğe göre kalori, protein, karbonhidrat, yağ |
| **Kişisel hedef** | Yaş, kilo, boy, aktivite seviyesine göre BMR/TDEE hesabı |
| **Takip** | Günlük ve haftalık raporlar, Plotly ile interaktif grafikler |
| **Kullanıcı sistemi** | SQLite tabanlı kayıt/giriş, SHA-256 ile parola özetleme |
| **Yönetim** | Admin paneli, light/dark tema |

---

## Teknik tarafı

**Model.** Food-101 veri seti YOLOv8 formatına dönüştürülüp (`convert_food101_to_yolo.py`) 30 kategorilik
bir alt küme üzerinde eğitildi (`train.py`). Doğruluk %93,4, çıkarım süresi görüntü başına ~5 ms.

**Besin veritabanı.** Tanınan sınıfı porsiyon bazlı besin değerlerine eşleyen katman (`nutrition_db.py`),
kullanıcının girdiği porsiyon miktarına göre ölçekleniyor.

**Kullanıcı katmanı.** Kayıt, giriş ve profil yönetimi SQLite üzerinde; parolalar düz metin saklanmıyor,
SHA-256 özeti tutuluyor (`user_database.py`). Kullanıcı profilinden BMR ve TDEE hesaplanıp günlük kalori
hedefi çıkarılıyor.

**Arayüz.** Streamlit ile tek sayfalık uygulama (`app.py`): fotoğraf yükleme, anlık tanıma sonucu,
günlük özet, haftalık grafik, tema değiştirme ve admin paneli.

---

## Kurulum

```bash
pip install streamlit ultralytics plotly pandas pillow
streamlit run app.py
```

Modeli yeniden eğitmek için:

```bash
python convert_food101_to_yolo.py   # Food-101 → YOLO formatı
python train.py                      # eğitim
```

---

## Proje yapısı

```
app.py                        Streamlit arayüzü, tanıma akışı, raporlar
nutrition_db.py               Besin değeri veritabanı ve porsiyon hesabı
user_database.py              Kullanıcı kaydı, giriş, BMR/TDEE
train.py                      YOLOv8 eğitim betiği
convert_food101_to_yolo.py    Veri seti dönüştürücü
```

---

## Ekip

Üç kişilik bitirme projesi ekibiyle sunuldu: **Emir**, **İlayda** ve **Yusuf Samet Karlıdağ**.
Uygulamanın geliştirmesini (model eğitimi, besin veritabanı, kullanıcı katmanı ve arayüz) ben yürüttüm.

Ekip arkadaşımın hesabındaki ilk sürüm: [ilaydayrdmc/Ne-Yiyorum](https://github.com/ilaydayrdmc/Ne-Yiyorum)
