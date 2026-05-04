import os
import glob
from mcp.server.fastmcp import FastMCP

# SiberSelma MCP Sunucusunu Başlatıyoruz
mcp = FastMCP("SiberSelma")

# Obsidian Wiki klasörü
WIKI_DIR = os.path.join("docs", "wiki")

def ensure_wiki_dir():
    """Wiki klasörünün var olduğundan emin olur."""
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)
        # Örnek bir dosya oluşturalım
        with open(os.path.join(WIKI_DIR, "xss_ornek.md"), "w", encoding="utf-8") as f:
            f.write("# Cross-Site Scripting (XSS)\n\nXSS zafiyeti, kullanıcı girdilerinin filtrelenmeden ekrana basılmasıyla oluşur.\n\n## Çözüm\nGirdileri sanitize edin.")

import sqlite3

DB_PATH = "wiki.db"

@mcp.tool()
def search_cyber_wiki(query: str) -> str:
    """
    Obsidian (LLM Wiki) içerisindeki siber güvenlik notlarını tarar.
    
    Args:
        query: Aranacak siber güvenlik terimi veya zafiyet adı (örn: "XSS", "SQL Injection", "nmap")
    """
    if not os.path.exists(DB_PATH):
        return "Hata: Veritabanı bulunamadı. Lütfen önce 'python ingest.py' çalıştırarak dosyaları indeksleyin."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Çift tırnak ile kaçış (escape) yapıyoruz ki SQLite sorguyu tam bir metin olarak algılasın
        safe_query = f'"{query}"' 
        
        # FTS5 Match ve Snippet kullanımı: Eşleşen kelimenin etrafını kırpar ve 64 kelimelik bağlam getirir
        c.execute('''
            SELECT filepath, snippet(wiki_search, 1, '>>', '<<', '...', 64) 
            FROM wiki_search 
            WHERE wiki_search MATCH ? 
            ORDER BY rank 
            LIMIT 5
        ''', (safe_query,))
        
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            return f"'{query}' için wiki'de sonuç bulunamadı."
            
        results = []
        for row in rows:
            filepath, snippet_text = row
            results.append(f"=== Kaynak: {os.path.basename(filepath)} ===\n{snippet_text}\n")
            
        return "\n".join(results)
    except Exception as e:
        return f"Arama sırasında hata oluştu: {str(e)}"

@mcp.tool()
def analyze_project_vulnerabilities(directory_path: str) -> str:
    """
    Verilen projenin kod dosyalarını okuyarak asistan için statik analiz bağlamı (SAST) sağlar.
    
    Args:
        directory_path: Analiz edilecek projenin yerel sistemdeki tam yolu.
    """
    if not os.path.exists(directory_path):
        return f"Hata: {directory_path} dizini bulunamadı. Lütfen geçerli bir yol girin."
        
    # PLACEHOLDER: İlerleyen aşamalarda burası directory içerisindeki .py, .js, .ts dosyalarını
    # okuyup tehlikeli fonksiyonları (eval, exec, vb.) arayacak şekilde güncellenecek.
    return f"{directory_path} dizini için analiz modülü tetiklendi. (Not: Statik kod okuyucu modülü yakında eklenecektir.)"

@mcp.tool()
def get_remediation_plan(vulnerability_name: str) -> str:
    """
    Bulunan bir zafiyetin nasıl kapatılacağına (remediation) dair wiki'den çözüm planı getirir.
    
    Args:
        vulnerability_name: Çözümü aranan zafiyet (örn: "IDOR", "CSRF")
    """
    # Basitçe wiki'de 'çözüm' veya 'remediation' kelimeleriyle arama yap
    return search_cyber_wiki(f"{vulnerability_name} çözüm")

@mcp.tool()
def run_basic_pentest(target: str) -> str:
    """
    (GELECEK VİZYONU / PLACEHOLDER) Verilen hedef üzerinde temel sızma testleri veya hack taramaları gerçekleştirir.
    
    Args:
        target: IP adresi, domain veya hedef URL.
    """
    # UYARI: Bu kısım kullanıcının "ileride siteleri hacklemek ve pentest etmek" vizyonu için ayrılmıştır.
    return f"SiberSelma Pentest Modülü: {target} hedefi için tarama protokolü alındı. (Uyarı: Aktif sömürü/pentest komutları ileriki güncellemelerde eklenecektir.)"

if __name__ == "__main__":
    ensure_wiki_dir()
    print("SiberSelma MCP Sunucusu baslatiliyor...")
    print("Standart I/O uzerinden iletisim dinleniyor (Claude Code vb. icin hazir)")
    # MCP sunucusunu standart I/O üzerinden çalıştır. (SSE veya stdio desteği vardır, default stdio)
    mcp.run()
