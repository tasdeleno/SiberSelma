import sqlite3
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'wiki.db')
WIKI_DIR = os.path.join(BASE_DIR, 'docs', 'wiki')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # SQLite FTS5 (Tam Metin Arama) tablosu oluştur
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS wiki_search USING fts5(
            filepath,
            content
        )
    ''')
    conn.commit()
    return conn

def ingest_with_dedup():
    """Deduplikasyon ile wiki dosyalarını indeksle: yeni/güncellenmiş ekle, silinenleri sil"""
    conn = init_db()
    c = conn.cursor()

    print(f"'{WIKI_DIR}' içerisindeki dosyalar taranıyor...")

    # Veritabanındaki mevcut dosyaları al
    c.execute('SELECT filepath FROM wiki_search')
    db_files = {os.path.normpath(row[0]) for row in c.fetchall()}

    # Dosya sistemindeki dosyaları al
    fs_files = {os.path.normpath(p) for p in glob.glob(f"{WIKI_DIR}/**/*.md", recursive=True)}

    # Silinmiş dosyaları tespit et (veritabanında ama dosya sisteminde yok)
    deleted_files = db_files - fs_files

    # Yeni dosyaları tespit et
    new_files = fs_files - db_files

    count_new = 0
    count_updated = 0
    count_deleted = len(deleted_files)

    try:
        # Silinmiş dosyaları sil
        for filepath in deleted_files:
            c.execute('DELETE FROM wiki_search WHERE filepath = ?', (filepath,))
            print(f"  [-] Silindi: {os.path.basename(filepath)}")

        # Mevcut dosyaları güncelle — FTS5'te UPDATE index'i güncellemez, DELETE+INSERT kullan
        for filepath in fs_files - new_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                c.execute('DELETE FROM wiki_search WHERE filepath = ?', (filepath,))
                c.execute('INSERT INTO wiki_search (filepath, content) VALUES (?, ?)', (filepath, content))
                count_updated += 1
            except Exception as e:
                print(f"  [!] Güncelleme hatası: {os.path.basename(filepath)} ({e})")

        # Yeni dosyaları ekle
        for filepath in new_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                c.execute('INSERT INTO wiki_search (filepath, content) VALUES (?, ?)', (filepath, content))
                count_new += 1
                print(f"  [+] Eklendi: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"  [!] Ekleme hatası: {os.path.basename(filepath)} ({e})")

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(f"\n[SUMMARY] Indexing Complete:")
    print(f"  [+] {count_new} yeni dosya eklendi")
    print(f"  [~] {count_updated} dosya guncellendi")
    print(f"  [-] {count_deleted} dosya silindi")
    print(f"  [*] Toplam: {len(fs_files)} dosya")
    print(f"\n[OK] SiberSelma sunucusu (server.py) hazir.")

if __name__ == "__main__":
    if not os.path.exists(WIKI_DIR):
        print(f"Hata: '{WIKI_DIR}' klasörü bulunamadı. Lütfen klasörün proje dizininde olduğundan emin olun.")
    else:
        ingest_with_dedup()
