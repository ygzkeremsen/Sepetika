# Sepetika — İnternet Alışveriş Sitesi

Flask ve SQLite ile hazırlanmış Türkçe eğitim projesi. Misafir ürünleri inceler; üyeler sepet oluşturup sipariş verir; yönetici ürünleri ve kullanıcı onaylarını yönetir.

## Kurulum

- Python 3.10+ gerekir.
- Windows: `py -m venv .venv` ardından `.venv\Scripts\activate`
- macOS/Linux: `python3 -m venv .venv` ardından `source .venv/bin/activate`
- Bağımlılıkları kurun: `pip install -r requirements.txt`
- Başlatın: `python app.py`
- `http://127.0.0.1:5000` adresini açın.

SQLite veritabanı ilk çalıştırmada otomatik kurulur ve örnek ürünler eklenir.

## Demo hesabı

- Yönetici: `admin@magaza.local`
- Parola: `Admin123!`
- Üye hesabını kayıt ekranından oluşturun.

Bu hesap yerel demo içindir. Gerçek kullanım öncesi yönetici parolasını ve `SECRET_KEY` değerini değiştirin.

## İçerik ve kapsam

- `app.py`: Flask rotaları, veritabanı şeması ve iş kuralları
- `templates/`: HTML/Jinja sayfaları
- `static/style.css`: duyarlı arayüz
- `RAPOR.md`: dokümantasyon, ER diyagramı, algoritma ve akış şeması
- `SUNUM.md`: sınıf sunumu slayt taslağı
- `shop.db`: uygulama başlatıldığında oluşturulur

Misafir katalog görüntüler. Üye kayıt olur, giriş yapar, sepete ürün ekler, sipariş verir ve geçmişini görür. Yönetici ürün ekleyebilir, satış durumunu değiştirebilir, kullanıcı onayı verebilir ve siparişleri görüntüler. Sipariş sırasında stok kontrol edilir ve azaltılır. Parolalar özetlenir, SQL sorguları parametreli çalışır.

Ödeme gerçek tahsilat yapmaz; sipariş akışı simüle edilir. Gerçek yayına almadan önce CSRF koruması, HTTPS, parola sıfırlama, ödeme/adres entegrasyonu ve güvenli dağıtım yapılandırması eklenmelidir.
