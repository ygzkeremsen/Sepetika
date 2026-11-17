# Sepetika — Sunum Taslağı

## 1. Kapak
**Sepetika: İnternet Alışveriş Sitesi**  
[Üniversite] · [Bölüm] · [Ders kodu ve adı]  
[Öğretim üyesi] · [Öğrenci adı soyadı ve numarası]  
Veriliş: 26 Ekim 2026 · Teslim: 23 Kasım 2026

## 2. Problem ve amaç
- Ürünleri çevrimiçi görüntüleme ve sipariş verme
- Misafir, üye ve yönetici rollerini ayırma
- Ürün ve sipariş kayıtlarını veritabanında tutma

## 3. Gereksinimler
- Misafir: katalog görüntüleme
- Üye: kayıt, giriş, sepet ve sipariş geçmişi
- Yönetici: ürün, kullanıcı onayı ve sipariş yönetimi

## 4. Teknoloji ve mimari
- Python, Flask, SQLite, HTML/Jinja ve CSS
- Tarayıcı → Flask uygulaması → SQLite

## 5. Veritabanı
- users: hesap ve rol
- products: fiyat, stok ve satış durumu
- orders / order_items: sipariş ve ürün kalemleri
- ER çizimini RAPOR.md Bölüm 6'dan ekleyin

## 6. Alışveriş deneyimi
- Ürün listeleme ve miktar seçimi
- Sepette stok kontrolü ve toplam hesabı
- Sipariş kaydı ve stok güncellemesi
- Ödeme eğitim demosunda simüle edilir

## 7. Yönetim paneli
- Ürün ekleme ve satışa açma/kapatma
- Kullanıcı onayı
- Siparişleri görüntüleme
- Yönetici dışı erişim engeli

## 8. Sipariş algoritması
Giriş kontrolü → sepet kontrolü → stok doğrulama → sipariş kaydı → stok azaltma → sepeti temizleme. Akış şemasını RAPOR.md Bölüm 7'den ekleyin.

## 9. Canlı demo
Ürünleri gösterin; üye hesabı açın; sepete ürün ekleyip sipariş verin; sipariş geçmişini açın; yönetici olarak ürünü satıştan kaldırın.

## 10. Sonuç
- Temel roller ve alışveriş akışı uygulandı.
- Veriler SQLite'ta kalıcı tutuluyor.
- Geliştirme: ürün düzenleme, arama, güvenlik ve ödeme entegrasyonu.

**Not ağırlıkları:** Proje %40 · Vize %30 · Final %30
