import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import random
import os
import time
import zipfile
import json
import colorsys
import threading
import hashlib
from datetime import datetime

class NexusForgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gelişmiş Şifre Tahmin")
        self.root.geometry("1300x850")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#050505")
        
        # Tema Renkleri
        self.ACCENT_COLOR = "#00d2ff" 
        self.TEXT_COLOR = "#e0e0e0"   
        self.BG_DARK = "#0a0a0a"      
        self.BG_PANEL = "#0d0d0d"     
        
        self.uretilen_liste = []
        
        self.arayuzu_insaa_et()

    def arayuzu_insaa_et(self):
        # --- ARKA PLAN ANİMASYONU ---
        self.canvas = tk.Canvas(self.root, bg="#050505", highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.toz_efekti_baslat()

        # --- ÜST BAR ---
        ust_bar = tk.Frame(self.root, bg=self.BG_DARK, height=60)
        ust_bar.pack(fill=tk.X, side=tk.TOP)
        
        baslik = tk.Label(ust_bar, text="ZGL", 
                          bg=self.BG_DARK, fg=self.ACCENT_COLOR, font=("Consolas", 20, "bold"))
        baslik.pack(pady=15)

        # --- ANA GÖVDE (Grid Sistemi) ---
        govde = tk.Frame(self.root, bg="#050505")
        govde.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        govde.columnconfigure(0, weight=1, uniform="col")
        govde.columnconfigure(1, weight=2, uniform="col")
        govde.columnconfigure(2, weight=1, uniform="col")
        govde.rowconfigure(0, weight=1)

        # ==========================================
        # 1. SÜTUN: DİNAMİK KONTROL PANELİ (SOL)
        # ==========================================
        self.sol_panel = tk.Frame(govde, bg=self.BG_PANEL, bd=1, relief="ridge")
        self.sol_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Sekme Butonları (Hacker Tarzı Custom Tabs)
        sekme_frame = tk.Frame(self.sol_panel, bg=self.BG_DARK)
        sekme_frame.pack(fill=tk.X)

        tk.Button(sekme_frame, text="⚡ KLASİK", command=lambda: self.sekme_degistir("klasik"), bg="#1a1a1a", fg=self.ACCENT_COLOR, font=("Consolas", 10, "bold"), bd=0, cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        tk.Button(sekme_frame, text="🕵️ OSINT", command=lambda: self.sekme_degistir("osint"), bg="#1a1a1a", fg=self.ACCENT_COLOR, font=("Consolas", 10, "bold"), bd=0, cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        tk.Button(sekme_frame, text="📂 TOPLU", command=lambda: self.sekme_degistir("toplu"), bg="#1a1a1a", fg=self.ACCENT_COLOR, font=("Consolas", 10, "bold"), bd=0, cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

        # İçerik Çerçevesi
        self.icerik_alani = tk.Frame(self.sol_panel, bg=self.BG_PANEL)
        self.icerik_alani.pack(fill=tk.BOTH, expand=True, pady=10)

        self.aktif_mod = "klasik"
        self.girdiler = {}
        self.sekme_degistir("klasik") # Varsayılan sekme

        # Ateşle Butonu (Ortak)
        uret_btn = tk.Button(self.sol_panel, text="SİSTEMİ ATEŞLE (TURBO) >>", command=self.thread_baslat, 
                             bg="#005566", fg="white", font=("Consolas", 14, "bold"), bd=0, cursor="hand2", activebackground=self.ACCENT_COLOR)
        uret_btn.pack(fill=tk.X, padx=20, pady=20, ipady=10)


        # ==========================================
        # 2. SÜTUN: ARAMA, İSTATİSTİK VE KONSOL (ORTA)
        # ==========================================
        orta_panel = tk.Frame(govde, bg="#050505")
        orta_panel.grid(row=0, column=1, sticky="nsew", padx=10)

        arama_frame = tk.Frame(orta_panel, bg="#050505")
        arama_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(arama_frame, text="🔍 Filtre:", bg="#050505", fg=self.ACCENT_COLOR, font=("Consolas", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.arama_kutusu = tk.Entry(arama_frame, bg="#1a1a1a", fg="white", font=("Consolas", 12), bd=1, insertbackground=self.ACCENT_COLOR)
        self.arama_kutusu.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=6)
        self.arama_kutusu.bind("<KeyRelease>", self.filtrele)

        self.istatistik_lbl = tk.Label(orta_panel, text="Durum: Bekleniyor | Toplam: 0 | Boyut: 0 KB", 
                                       bg="#121212", fg=self.ACCENT_COLOR, font=("Consolas", 11), pady=10)
        self.istatistik_lbl.pack(fill=tk.X, pady=(0, 10))

        self.konsol = scrolledtext.ScrolledText(orta_panel, bg=self.BG_DARK, fg="#00ff00", font=("Consolas", 11), bd=1, relief="sunken")
        self.konsol.pack(fill=tk.BOTH, expand=True)
        self.konsol.insert(tk.END, ">>> Multi-Threading Aktif. OSINT, Toplu İşlem ve Hash Desteği Hazır.\n")

        # ==========================================
        # 3. SÜTUN: HASH VE DIŞA AKTARIM (SAĞ)
        # ==========================================
        sag_panel = tk.Frame(govde, bg=self.BG_PANEL, bd=1, relief="ridge")
        sag_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        tk.Label(sag_panel, text="[ KRİPTO & İHRACAT ]", bg=self.BG_PANEL, fg=self.ACCENT_COLOR, font=("Consolas", 14, "bold")).pack(pady=20)

        # Hash Seçenekleri (Yeni Özellik)
        hash_frame = tk.Frame(sag_panel, bg=self.BG_PANEL)
        hash_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(hash_frame, text="Dışa Aktarım Formatı:", bg=self.BG_PANEL, fg=self.TEXT_COLOR, font=("Consolas", 10)).pack(anchor="w")
        
        self.hash_modu = tk.StringVar(value="duz")
        tk.Radiobutton(hash_frame, text="Düz Metin (Plain)", variable=self.hash_modu, value="duz", bg=self.BG_PANEL, fg=self.ACCENT_COLOR, selectcolor="#0a0a0a", font=("Consolas", 10)).pack(anchor="w", pady=2)
        tk.Radiobutton(hash_frame, text="MD5 Hash", variable=self.hash_modu, value="md5", bg=self.BG_PANEL, fg=self.ACCENT_COLOR, selectcolor="#0a0a0a", font=("Consolas", 10)).pack(anchor="w", pady=2)
        tk.Radiobutton(hash_frame, text="SHA-256 Hash", variable=self.hash_modu, value="sha256", bg=self.BG_PANEL, fg=self.ACCENT_COLOR, selectcolor="#0a0a0a", font=("Consolas", 10)).pack(anchor="w", pady=2)

        tk.Label(sag_panel, text="-----------------", bg=self.BG_PANEL, fg="#333").pack(pady=10)

        export_butonlari = [
            ("📄 TXT Formatında Al", self.export_txt),
            ("🗜️ ZIP Olarak Sıkıştır", self.export_zip),
            ("📊 JSON Olarak Aktar", self.export_json)
        ]

        for metin, komut in export_butonlari:
            tk.Button(sag_panel, text=metin, command=komut, bg="#1a1a1a", fg=self.TEXT_COLOR, font=("Consolas", 11), bd=1, cursor="hand2").pack(fill=tk.X, padx=20, pady=10, ipady=8)

    # --- SEKME YÖNETİMİ ---
    def alan_olustur(self, ebeveyn, metin, anahtar):
        tk.Label(ebeveyn, text=metin, bg=self.BG_PANEL, fg=self.TEXT_COLOR, font=("Consolas", 10)).pack(anchor="w", padx=20, pady=(10, 2))
        kutu = tk.Entry(ebeveyn, bg="#1a1a1a", fg=self.ACCENT_COLOR, font=("Consolas", 12), bd=1, insertbackground=self.ACCENT_COLOR)
        kutu.pack(fill=tk.X, padx=20, ipady=5)
        self.girdiler[anahtar] = kutu

    def sekme_degistir(self, mod):
        self.aktif_mod = mod
        for widget in self.icerik_alani.winfo_children():
            widget.destroy()
        self.girdiler.clear()

        if mod == "klasik":
            self.alan_olustur(self.icerik_alani, "Hedef Kelime:", "anahtar")
            self.alan_olustur(self.icerik_alani, "Sayılar (Virgülle):", "sayilar")
            self.alan_olustur(self.icerik_alani, "Semboller (!@*):", "semboller")
            self.alan_olustur(self.icerik_alani, "Yan Kelimeler:", "ekstralar")
            
        elif mod == "osint":
            tk.Label(self.icerik_alani, text="[ HEDEF PROFİLİ ]", bg=self.BG_PANEL, fg="#ffaa00", font=("Consolas", 12, "bold")).pack(pady=5)
            self.alan_olustur(self.icerik_alani, "Adı:", "ad")
            self.alan_olustur(self.icerik_alani, "Soyadı:", "soyad")
            self.alan_olustur(self.icerik_alani, "Doğum Yılı / Tarihi:", "tarih")
            self.alan_olustur(self.icerik_alani, "Evcil Hayvan / Takım:", "ekstra1")
            self.alan_olustur(self.icerik_alani, "Partner/Çocuk Adı:", "ekstra2")
            
        elif mod == "toplu":
            tk.Label(self.icerik_alani, text="[ TOPLU İŞLEM MODU ]", bg=self.BG_PANEL, fg="#ff0044", font=("Consolas", 12, "bold")).pack(pady=5)
            
            btn = tk.Button(self.icerik_alani, text="📂 Wordlist Dosyası Seç", command=self.dosya_sec, bg="#222", fg="white", font=("Consolas", 10))
            btn.pack(fill=tk.X, padx=20, pady=10, ipady=5)
            
            self.dosya_lbl = tk.Label(self.icerik_alani, text="Seçilen: Yok", bg=self.BG_PANEL, fg="#888", font=("Consolas", 9))
            self.dosya_lbl.pack(pady=5)
            self.secilen_dosya = ""
            
            tk.Label(self.icerik_alani, text="Bu dosyadaki kelimelere eklenecekler:", bg=self.BG_PANEL, fg=self.TEXT_COLOR, font=("Consolas", 9)).pack(pady=10)
            self.alan_olustur(self.icerik_alani, "Sayılar:", "sayilar")
            self.alan_olustur(self.icerik_alani, "Semboller:", "semboller")

    def dosya_sec(self):
        yol = filedialog.askopenfilename(filetypes=[("Text Dosyaları", "*.txt")])
        if yol:
            self.secilen_dosya = yol
            self.dosya_lbl.config(text=f"Seçilen: {os.path.basename(yol)}")

    # --- ARKA PLAN ANİMASYONU ---
    def toz_efekti_baslat(self):
        self.parcaciklar = []
        self.toz_hue = 0.5 
        for _ in range(90): 
            x = random.randint(0, 2500); y = random.randint(0, 1500)
            r = random.uniform(1.0, 2.5); hiz = random.uniform(0.2, 0.8)
            p_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="")
            self.parcaciklar.append({"id": p_id, "hiz": hiz, "r": r, "parlaklik": random.uniform(0.3, 0.6)})
        self.toz_hareket_ettir()

    def toz_hareket_ettir(self):
        self.toz_hue = (self.toz_hue + 0.005) % 1.0
        w, h = self.root.winfo_width(), self.root.winfo_height()
        
        for p in self.parcaciklar:
            self.canvas.move(p["id"], 0, -p["hiz"])
            coords = self.canvas.coords(p["id"])
            r, g, b = colorsys.hsv_to_rgb(self.toz_hue, 1.0, p["parlaklik"])
            self.canvas.itemconfig(p["id"], fill=f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
            
            if len(coords) == 4 and coords[3] < 0:
                nx = random.randint(0, w if w > 0 else 1500)
                self.canvas.coords(p["id"], nx-p["r"], h, nx+p["r"], h + (2*p["r"]))
        self.root.after(40, self.toz_hareket_ettir)

    def filtrele(self, event=None):
        hedef = self.arama_kutusu.get().lower()
        if not self.uretilen_liste: return
        sonuclar = self.uretilen_liste if not hedef else [s for s in self.uretilen_liste if hedef in s.lower()]
        self.konsol.delete(1.0, tk.END)
        self.konsol.insert(tk.END, "\n".join(sonuclar[:5000]))
        if len(sonuclar) > 5000: self.konsol.insert(tk.END, f"\n\n... ve {len(sonuclar)-5000} kayıt daha.")
        self.istatistik_lbl.config(text=f"Durum: Filtrelendi | Eşleşen: {len(sonuclar)} / Toplam: {len(self.uretilen_liste)}")

    # --- MÜHENDİSLİK (THREADING & ALGORİTMALAR) ---
    def mutasyon_uygula(self, kelime):
        return kelime.translate(str.maketrans("aeisobAEISOB", "@31$08@31$08"))

    def nexus_motoru(self, kw_list, nums, syms, extras=[]):
        havuz = set()
        n_list = [n.strip() for n in nums.split(',')] if nums else []
        s_list = list(syms) if syms else []
        e_list = [e.strip() for e in extras.split(',')] if extras else []

        for kw in kw_list:
            if not kw: continue
            cekirdek = [kw, kw.lower(), kw.upper(), kw.capitalize(), self.mutasyon_uygula(kw), kw[::-1]]
            for c in cekirdek:
                havuz.add(c)
                for n in n_list: havuz.update([c+n, n+c])
                for s in s_list: havuz.update([c+s, s+c])
                for e in e_list: havuz.update([c+e, e+c])
                for n in n_list:
                    for s in s_list:
                        havuz.update([c+s+n, s+c+n, n+c+s, c+n+s])
        return list(havuz)

    def osint_birlestirici(self, ad, soyad, tarih, ek1, ek2):
        parcalar = [p for p in [ad, soyad, tarih, ek1, ek2] if p]
        kombinasyonlar = set(parcalar)
        # İkili kombinasyonlar (örn: burak1990, 1990burak)
        for p1 in parcalar:
            for p2 in parcalar:
                if p1 != p2:
                    kombinasyonlar.add(p1+p2)
                    kombinasyonlar.add(p1+"."+p2)
                    kombinasyonlar.add(p1+"_"+p2)
        return list(kombinasyonlar)

    def thread_baslat(self):
        """Arayüzü dondurmadan işlemi arka planda başlatır"""
        self.istatistik_lbl.config(text="Durum: MOTORLAR ÇALIŞIYOR... Lütfen Bekleyin!")
        self.konsol.delete(1.0, tk.END)
        self.konsol.insert(tk.END, ">>> Turbo Mod devrede. İşlem arka planda yürütülüyor...\n")
        self.arama_kutusu.delete(0, tk.END)
        
        # İşlemi yeni bir iş parçacığına (thread) yolla
        threading.Thread(target=self._uretim_gorevi, daemon=True).start()

    def _uretim_gorevi(self):
        """Arka planda çalışan gerçek üretim algoritması"""
        baslangic = time.time()
        sonuclar = []

        if self.aktif_mod == "klasik":
            hedef = self.girdiler["anahtar"].get().strip()
            if not hedef: return self._hata_goster("Anahtar kelime boş olamaz!")
            sonuclar = self.nexus_motoru([hedef], self.girdiler["sayilar"].get(), self.girdiler["semboller"].get(), self.girdiler["ekstralar"].get())

        elif self.aktif_mod == "osint":
            hedef_listesi = self.osint_birlestirici(
                self.girdiler["ad"].get().strip(), self.girdiler["soyad"].get().strip(),
                self.girdiler["tarih"].get().strip(), self.girdiler["ekstra1"].get().strip(), self.girdiler["ekstra2"].get().strip()
            )
            if not hedef_listesi: return self._hata_goster("En az bir OSINT verisi girin!")
            # OSINT profiline standart hacker sembolleri ekle
            sonuclar = self.nexus_motoru(hedef_listesi, "123,1234,2026", "!@.")

        elif self.aktif_mod == "toplu":
            if not getattr(self, "secilen_dosya", None): return self._hata_goster("Lütfen önce bir .txt dosyası seçin!")
            try:
                with open(self.secilen_dosya, "r", encoding="utf-8") as f:
                    kelimeler = [satir.strip() for satir in f.readlines() if satir.strip()]
                # Toplu listedeki her kelimeye kuralları uygula
                sonuclar = self.nexus_motoru(kelimeler, self.girdiler["sayilar"].get(), self.girdiler["semboller"].get())
            except Exception as e:
                return self._hata_goster(f"Dosya okuma hatası: {e}")

        # Arayüz güncellemelerini ana iş parçacığına (root.after) geri yolla
        self.uretilen_liste = sorted(list(set(sonuclar)))
        gecen_sure = round(time.time() - baslangic, 3)
        self.root.after(0, self._islem_bitti, gecen_sure)

    def _hata_goster(self, mesaj):
        self.root.after(0, lambda: messagebox.showwarning("Uyarı", mesaj))
        self.root.after(0, lambda: self.istatistik_lbl.config(text="Durum: Bekleniyor..."))

    def _islem_bitti(self, gecen_sure):
        boyut = round((len(self.uretilen_liste) * 12) / 1024, 2)
        self.istatistik_lbl.config(text=f"Durum: Tamamlandı | Süre: {gecen_sure}s | Toplam: {len(self.uretilen_liste)} | Boyut: ~{boyut} KB")
        self.konsol.delete(1.0, tk.END)
        self.konsol.insert(tk.END, "\n".join(self.uretilen_liste[:5000]))
        if len(self.uretilen_liste) > 5000:
            self.konsol.insert(tk.END, f"\n\n... ve {len(self.uretilen_liste) - 5000} veri daha hafızada hazır.")

    # --- HASH & DIŞA AKTARIM ---
    def veriyi_hazirla(self):
        mod = self.hash_modu.get()
        if mod == "duz": return "\n".join(self.uretilen_liste)
        
        # Hash işlemi
        self.istatistik_lbl.config(text="Durum: Hashleniyor... Lütfen bekleyin.")
        self.root.update()
        
        hashli_liste = []
        for kelime in self.uretilen_liste:
            if mod == "md5": hashli_liste.append(hashlib.md5(kelime.encode()).hexdigest())
            elif mod == "sha256": hashli_liste.append(hashlib.sha256(kelime.encode()).hexdigest())
            
        self.istatistik_lbl.config(text="Durum: Hash İşlemi Tamamlandı.")
        return "\n".join(hashli_liste)

    def export_txt(self):
        if not self.uretilen_liste: return
        yol = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="Nexus_Export.txt")
        if yol:
            veri = self.veriyi_hazirla()
            with open(yol, 'w', encoding='utf-8') as f: f.write(veri)
            self._basarili_mesaji(yol)

    def export_zip(self):
        if not self.uretilen_liste: return
        yol = filedialog.asksaveasfilename(defaultextension=".zip", initialfile="Nexus_Export.zip")
        if yol:
            veri = self.veriyi_hazirla()
            gecici = "nexus_temp.txt"
            with open(gecici, "w", encoding="utf-8") as f: f.write(veri)
            with zipfile.ZipFile(yol, 'w', zipfile.ZIP_DEFLATED) as z: z.write(gecici, "wordlist.txt")
            os.remove(gecici)
            self._basarili_mesaji(yol)
            
    def export_json(self):
        if not self.uretilen_liste: return
        yol = filedialog.asksaveasfilename(defaultextension=".json", initialfile="Nexus_Veri.json")
        if yol:
            # JSON'da direkt listeyi aktarırız (Hashli veya düz)
            hash_mod = self.hash_modu.get()
            kayit_listesi = self.uretilen_liste
            
            if hash_mod != "duz":
                self.istatistik_lbl.config(text="Durum: JSON için Hashleniyor...")
                self.root.update()
                kayit_listesi = [hashlib.md5(k.encode()).hexdigest() if hash_mod=="md5" else hashlib.sha256(k.encode()).hexdigest() for k in self.uretilen_liste]

            veri = {
                "proje": "NexusForge",
                "format": "Düz Metin" if hash_mod=="duz" else hash_mod.upper(),
                "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "toplam_kayit": len(kayit_listesi),
                "varyasyonlar": kayit_listesi
            }
            with open(yol, 'w', encoding='utf-8') as f: json.dump(veri, f, indent=4)
            self.istatistik_lbl.config(text="Durum: Bekleniyor...")
            self._basarili_mesaji(yol)

    def _basarili_mesaji(self, yol):
        messagebox.showinfo("İşlem Tamam", f"Veri başarıyla dışa aktarıldı:\n{yol}")
        try: os.startfile(yol)
        except: pass

if __name__ == "__main__":
    app_root = tk.Tk()
    app = NexusForgeApp(app_root)
    app_root.mainloop()