import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QFrame, QScrollArea, QMessageBox, QInputDialog, QProgressBar)
from PyQt5.QtCore import Qt
from database import VeritabaniYonetici

class OkulSistemiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = VeritabaniYonetici()
        self.setWindowTitle("Okul Devamsızlık ve Not Analiz Sistemi")
        self.resize(1100, 750)
        self.giris_ekrani_olustur()

    def giris_ekrani_olustur(self):
        self.merkez = QWidget(); self.setCentralWidget(self.merkez)
        self.merkez.setStyleSheet("background-color: #3949ab;")
        layout = QVBoxLayout(self.merkez); layout.addStretch()

        lbl = QLabel("Okul Devamsızlık ve Not Analiz Sistemi")
        lbl.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        lbl.setAlignment(Qt.AlignCenter); layout.addWidget(lbl)
        
        layout.addSpacing(60)
        btn_layout = QHBoxLayout()
        self.ana_buton_ekle(btn_layout, "👨‍🏫 Öğretmen Girişi", "#ff8a65", True)
        self.ana_buton_ekle(btn_layout, "👨‍🎓 Öğrenci Girişi", "#4fc3f7", False)
        layout.addLayout(btn_layout); layout.addStretch()

    def ana_buton_ekle(self, layout, metin, renk, is_teacher):
        btn = QPushButton(metin); btn.setFixedSize(350, 220); btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"background-color: white; border: 6px solid {renk}; border-radius: 25px; font-size: 16px; font-weight: bold; color: #333;")
        btn.clicked.connect(lambda: self.giris_dialog_ac(is_teacher)); layout.addWidget(btn)

    def giris_dialog_ac(self, is_teacher):
        numara, ok = QInputDialog.getText(self, "Sistem Girişi", "Numaranızı giriniz (Örn: 123):")
        if ok and numara:
            ogrenci = self.db_manager.ogrenci_bul(numara)
            if ogrenci: self.obs_panel(ogrenci, is_teacher)
            else: QMessageBox.warning(self, "Hata", "Öğrenci bulunamadı!")

    def obs_panel(self, veri, is_teacher):
        self.obs_widget = QWidget(); self.setCentralWidget(self.obs_widget)
        self.obs_widget.setStyleSheet("background-color: #f0f2f5;")
        ana_lay = QHBoxLayout(self.obs_widget); ana_lay.setContentsMargins(0, 0, 0, 0)

        s_color = "#f70000f8" if is_teacher else "#1a237e"
        self.sidebar = QFrame(); self.sidebar.setFixedWidth(260); self.sidebar.setStyleSheet(f"background-color: {s_color}; border: none;")
        s_lay = QVBoxLayout(self.sidebar)
        
        title = QLabel("YÖNETİM" if is_teacher else "ÖĞRENCİ")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin: 30px 0;"); title.setAlignment(Qt.AlignCenter); s_lay.addWidget(title)

        self.nav_btn(s_lay, "🏠 Ana Sayfa", lambda: self.sayfa_yukle("ana", veri, is_teacher))
        if is_teacher:
            self.nav_btn(s_lay, "➕ Yeni Öğrenci Ekle", lambda: self.sayfa_yukle("ekle", veri, is_teacher))
            self.nav_btn(s_lay, "📝 Not Giriş Ekranı", lambda: self.sayfa_yukle("edit", veri, is_teacher))
            self.nav_btn(s_lay, "🗑️ Öğrenciyi Sil", lambda: self.sil_onay(veri))
        else:
            self.nav_btn(s_lay, "📝 Sınav Notlarım", lambda: self.sayfa_yukle("notlar", veri, is_teacher))
            self.nav_btn(s_lay, "🕒 Devamsızlık Durumu", lambda: self.sayfa_yukle("devam", veri, is_teacher))
        
        s_lay.addStretch(); self.nav_btn(s_lay, "🚪 Güvenli Çıkış", self.giris_ekrani_olustur); ana_lay.addWidget(self.sidebar)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setStyleSheet("border: none;")
        self.content_w = QWidget(); self.content_lay = QVBoxLayout(self.content_w); self.content_lay.setContentsMargins(30, 30, 30, 30); self.scroll.setWidget(self.content_w); ana_lay.addWidget(self.scroll)
        self.sayfa_yukle("ana", veri, is_teacher)

    def nav_btn(self, lay, txt, fonk):
        b = QPushButton(txt); b.setCursor(Qt.PointingHandCursor); b.setStyleSheet("color: white; text-align: left; padding: 15px; border: none; font-size: 14px;")
        b.clicked.connect(fonk); lay.addWidget(b)

    def sayfa_yukle(self, sayfa, veri, is_t):
        while self.content_lay.count():
            item = self.content_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        header = QLabel(f"İşlem: {veri['ad']} {veri['soyad']} ({veri['numara']})")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #222;"); self.content_lay.addWidget(header)

        if sayfa == "ana":
            clr = "#e64a19" if is_t else "#4caf50"
            info = QLabel("Sisteme Başarıyla Giriş Yapıldı. " + ("Yönetici Modu" if is_t else "Öğrenci Modu"))
            info.setStyleSheet(f"background-color: {clr}; color: white; padding: 25px; border-radius: 12px; font-weight: bold;"); self.content_lay.addWidget(info); self.content_lay.addStretch()

        elif sayfa == "notlar" or sayfa == "devam":
            for d in veri['dersler']:
                card = QFrame(); card.setStyleSheet("background: white; border: 1px solid #ddd; border-radius: 12px; padding: 15px; margin-bottom: 10px;")
                cl = QHBoxLayout(card)
                ders_lbl = QLabel(f"<b>{d['ad']}</b>"); ders_lbl.setStyleSheet("color: #222;"); cl.addWidget(ders_lbl, stretch=1)
                
                if sayfa == "notlar":
                    not_lbl = QLabel(f"Vize: {d['vize']} | Final: {d['final']}"); not_lbl.setStyleSheet("color: #333;"); cl.addWidget(not_lbl)
                else:
                    dev_lbl = QLabel(f"{d['devam']} Gün Devam"); dev_lbl.setStyleSheet("color: #333;"); cl.addWidget(dev_lbl)
                    bar = QProgressBar(); bar.setRange(0, 10); bar.setValue(d['devam']); bar.setFixedWidth(120)
                    bar.setTextVisible(False) # BURASI O YÜZDE YAZISINI SİLİYOR
                    bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {'#e74c3c' if d['devam'] > 5 else '#2ecc71'}; border-radius: 5px; }}")
                    cl.addWidget(bar)
                self.content_lay.addWidget(card)
            self.content_lay.addStretch()

        elif sayfa == "edit":
            self.inputs = []
            for d in veri['dersler']:
                row_f = QFrame(); row_f.setStyleSheet("background-color: #fff; border-radius: 8px; margin-bottom: 5px;")
                row = QHBoxLayout(row_f)
                d_name = QLabel(d['ad']); d_name.setStyleSheet("color: #000; font-weight: bold;"); row.addWidget(d_name, stretch=2)
                v = QLineEdit(str(d['vize'])); f = QLineEdit(str(d['final'])); dv = QLineEdit(str(d['devam']))
                v.setStyleSheet("color: #000; background: #eee;"); f.setStyleSheet("color: #000; background: #eee;"); dv.setStyleSheet("color: #000; background: #eee;")
                v.setFixedWidth(50); f.setFixedWidth(50); dv.setFixedWidth(50)
                row.addWidget(QLabel("V:")); row.addWidget(v); row.addWidget(QLabel("F:")); row.addWidget(f); row.addWidget(QLabel("D:")); row.addWidget(dv)
                self.inputs.append({'v': v, 'f': f, 'd': dv, 'ad': d['ad']}); self.content_lay.addWidget(row_f)
            
            btn = QPushButton("DEĞİŞİKLİKLERİ KAYDET"); btn.setStyleSheet("background: #bf360c; color: white; padding: 15px; font-weight: bold; margin-top: 10px;")
            btn.clicked.connect(lambda: self.kaydet_islem(veri)); self.content_lay.addWidget(btn)

        elif sayfa == "ekle":
            self.e_ad = QLineEdit(); self.e_so = QLineEdit(); self.e_nu = QLineEdit()
            for e in [self.e_ad, self.e_so, self.e_nu]: e.setStyleSheet("color: #000; background: #fff; padding: 10px; margin-bottom: 5px;")
            self.e_ad.setPlaceholderText("Ad"); self.e_so.setPlaceholderText("Soyad"); self.e_nu.setPlaceholderText("Numara")
            btn = QPushButton("ÖĞRENCİYİ SİSTEME EKLE"); btn.setStyleSheet("background: #27ae60; color: white; padding: 15px; font-weight: bold;"); btn.clicked.connect(self.ekle_islem)
            for w in [self.e_ad, self.e_so, self.e_nu, btn]: self.content_lay.addWidget(w)
            self.content_lay.addStretch()

    def kaydet_islem(self, veri):
        try:
            yeni = [{"ad": i['ad'], "vize": int(i['v'].text()), "final": int(i['f'].text()), "devam": int(i['d'].text())} for i in self.inputs]
            self.db_manager.ogrenci_guncelle(veri['numara'], yeni); QMessageBox.information(self, "Başarılı", "Veriler veritabanına işlendi.")
        except: QMessageBox.warning(self, "Hata", "Lütfen sadece sayı giriniz!")

    def ekle_islem(self):
        if self.db_manager.yeni_ogrenci_kaydet(self.e_ad.text(), self.e_so.text(), self.e_nu.text()):
            QMessageBox.information(self, "Başarılı", "Öğrenci eklendi.")
        else: QMessageBox.warning(self, "Hata", "Bu numara zaten kayıtlı!")

    def sil_onay(self, veri):
        if QMessageBox.question(self, "Onay", f"{veri['ad']} silinsin mi?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db_manager.ogrenci_sil(veri['numara']); self.giris_ekrani_olustur()

if __name__ == "__main__":
    app = QApplication(sys.argv); ex = OkulSistemiApp(); ex.show(); sys.exit(app.exec_())

    