"""
AlfredX v2.1: Cinematic Main Window — FINAL BUILD
Exact match to alfredx_v2_cinematic.html
All engines wired with proper thread safety via pyqtSignal.
Multi-line input, typing indicator, TTS, voice, wake word, memory.
+ Language toggle, clear chat, keyboard shortcuts, settings persistence.
"""
from core.language_switcher import LanguageSwitcher
from core.global_hotkey import GlobalHotkey
from core.chat_history import chat_db
from PyQt5.QtCore import Qt
import math, time, random, os, threading, json, re, subprocess, webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect, QSpacerItem, QFileDialog,
    QDialog, QTextEdit, QTextBrowser, QMessageBox, QApplication, QShortcut
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QTimer, QRectF, QPointF, QSize, QObject
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPainterPath, QLinearGradient,
    QRadialGradient, QPen, QBrush, QPolygonF, QCursor, QKeySequence,
    QTextCursor, QTextOption
)

try:
    import psutil
    PSUTIL_OK = True
except ImportError:
    PSUTIL_OK = False

GOLD="#c9a227";GOLD_BRIGHT="#ffd700";GOLD_DIM="#8b6914"
BLUE="#00d4ff";BLUE_DIM="#0088aa";RED="#ff3333";GREEN="#00ff88"
DARK="#000000";DARK_BLUE="#0a0a1a";PANEL_BG="rgba(5,10,25,217)"
FM="Segoe UI";FC="Consolas";FH="Segoe UI"
SETTINGS_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","data","alfredx_settings.json")

class _SignalBridge(QObject):
    ai_response=pyqtSignal(str);voice_heard=pyqtSignal(str)
    voice_error=pyqtSignal(str);tts_done=pyqtSignal()
    wake_detected=pyqtSignal();reminder_fired=pyqtSignal(str)

class TechFrame(QFrame):
    # style: "header" | "footer" | "panel"
    def __init__(self, style="panel", parent=None):
        super().__init__(parent)
        self._style = style
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # panel bg
        bg = QColor(5, 10, 25, 217)

        # clip shapes like HTML
        if self._style == "header":
            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w * 0.98, h)
            path.lineTo(w * 0.02, h)
            path.closeSubpath()
        elif self._style == "footer":
            path = QPainterPath()
            path.moveTo(w * 0.02, 0)
            path.lineTo(w * 0.98, 0)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.closeSubpath()
        else:
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, w, h), 4, 4)

        # fill
        p.fillPath(path, bg)

        # border
        p.setPen(QPen(QColor(201, 162, 39, 80), 1))
        p.drawPath(path)

        # top glow line (header/panels)
        if self._style in ("header", "panel"):
            g = QLinearGradient(0, 0, w, 0)
            g.setColorAt(0, QColor(0, 0, 0, 0))
            g.setColorAt(0.2, QColor(201, 162, 39, 180))
            g.setColorAt(0.5, QColor(0, 212, 255, 220))
            g.setColorAt(0.8, QColor(201, 162, 39, 180))
            g.setColorAt(1, QColor(0, 0, 0, 0))
            p.fillRect(QRectF(0, 0, w, 2), g)

        p.end()
        super().paintEvent(e)

def make_panel(title_text=None, status_text=None):
    f=QFrame();f.setObjectName("Panel")
    f.setStyleSheet(f"QFrame#Panel{{background:{PANEL_BG};border:1px solid rgba(201,162,39,40);border-radius:4px;}}")
    lay=QVBoxLayout(f);lay.setContentsMargins(0,0,0,0);lay.setSpacing(0)
    if title_text:
        hdr=QFrame();hdr.setFixedHeight(40)
        hdr.setStyleSheet("QFrame{background:rgba(201,162,39,10);border:none;border-bottom:1px solid rgba(201,162,39,30);border-top-left-radius:4px;border-top-right-radius:4px;}")
        hl=QHBoxLayout(hdr);hl.setContentsMargins(18,0,18,0)
        t=QLabel(f"◆  {title_text}");t.setFont(QFont(FH,9,QFont.Bold))
        t.setStyleSheet(f"color:{GOLD};letter-spacing:3px;border:none;background:transparent;")
        hl.addWidget(t);hl.addStretch()
        if status_text:
            badge=QLabel(status_text);badge.setFont(QFont(FC,7,QFont.Bold))
            # Keep the status badge compact so it doesn't collide with long section titles
            badge.setStyleSheet(
                f"QLabel{{color:{GREEN};background:rgba(0,255,136,30);border:1px solid rgba(0,255,136,80);"
                f"padding:2px 8px;border-radius:2px;letter-spacing:1px;min-height:18px;}}"
            )
            hl.addWidget(badge)
        lay.addWidget(hdr)
    return f,lay

class BatLogo(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.setFixedSize(70,70);self._angle=0.0
    def set_angle(self,a):self._angle=a;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        cx,cy=35,35;pulse=0.7+0.3*math.sin(self._angle)
        # Outer glow
        og=QRadialGradient(cx,cy,35);og.setColorAt(0,QColor(201,162,39,int(15*pulse)));og.setColorAt(1,QColor(0,0,0,0))
        p.setPen(Qt.NoPen);p.setBrush(og);p.drawEllipse(QRectF(0,0,70,70))
        # Outer cyan ring
        p.setPen(QPen(QColor(0,212,255,int(90*pulse)),1.5));p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(cx-33,cy-33,66,66))
        # Inner dashed gold ring
        pen1=QPen(QColor(201,162,39,int(80*pulse)),1);pen1.setStyle(Qt.DashLine)
        p.setPen(pen1);p.drawEllipse(QRectF(cx-27,cy-27,54,54))
        # Orbiting dots
        a1=self._angle*0.7;dx1=cx+27*math.cos(a1);dy1=cy+27*math.sin(a1)
        p.setPen(Qt.NoPen);p.setBrush(QColor(201,162,39,int(220*pulse)));p.drawEllipse(QRectF(dx1-3,dy1-3,6,6))
        a2=-self._angle*0.5;dx2=cx+33*math.cos(a2);dy2=cy+33*math.sin(a2)
        p.setBrush(QColor(0,212,255,int(220*pulse)));p.drawEllipse(QRectF(dx2-2.5,dy2-2.5,5,5))
        # Bat silhouette
        bat=QPainterPath();sc=0.45;ox=cx-22;oy=cy-11
        bat.moveTo(ox+50*sc,oy+5*sc)
        bat.cubicTo(ox+45*sc,oy+5*sc,ox+40*sc,oy+10*sc,ox+38*sc,oy+15*sc)
        bat.cubicTo(ox+35*sc,oy+10*sc,ox+25*sc,oy+5*sc,ox+15*sc,oy+10*sc)
        bat.cubicTo(ox+20*sc,oy+15*sc,ox+18*sc,oy+25*sc,ox+15*sc,oy+30*sc)
        bat.cubicTo(ox+18*sc,oy+35*sc,ox+30*sc,oy+45*sc,ox+40*sc,oy+48*sc)
        bat.cubicTo(ox+43*sc,oy+50*sc,ox+47*sc,oy+50*sc,ox+50*sc,oy+50*sc)
        bat.cubicTo(ox+53*sc,oy+50*sc,ox+57*sc,oy+50*sc,ox+60*sc,oy+48*sc)
        bat.cubicTo(ox+70*sc,oy+45*sc,ox+82*sc,oy+35*sc,ox+85*sc,oy+30*sc)
        bat.cubicTo(ox+82*sc,oy+25*sc,ox+80*sc,oy+15*sc,ox+85*sc,oy+10*sc)
        bat.cubicTo(ox+75*sc,oy+5*sc,ox+65*sc,oy+10*sc,ox+62*sc,oy+15*sc)
        bat.cubicTo(ox+60*sc,oy+10*sc,ox+55*sc,oy+5*sc,ox+50*sc,oy+5*sc)
        # Inner glow behind bat
        glow=QRadialGradient(cx,cy,24);glow.setColorAt(0,QColor(201,162,39,int(50*pulse)));glow.setColorAt(1,QColor(0,0,0,0))
        p.setBrush(glow);p.setPen(Qt.NoPen);p.drawEllipse(QRectF(cx-24,cy-24,48,48))
        p.fillPath(bat,QColor(201,162,39,int(230*pulse)))
        p.end()

class HeaderBar(TechFrame):
    notify_clicked=pyqtSignal();stats_clicked=pyqtSignal();settings_clicked=pyqtSignal();power_clicked=pyqtSignal();lang_clicked=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__("header", parent);self.setFixedHeight(80)
        self.setStyleSheet(f"QFrame{{background:{PANEL_BG};border:1px solid rgba(201,162,39,77);}}")
        self._angle=0.0;lay=QHBoxLayout(self);lay.setContentsMargins(20,0,20,0);lay.setSpacing(10)
        self._bat=BatLogo();lay.addWidget(self._bat,alignment=Qt.AlignVCenter);lay.addSpacing(10)
        tc=QVBoxLayout();tc.setSpacing(2);tc.setContentsMargins(0,0,0,0)
        mt=QLabel("ALFREDX");mt.setFont(QFont(FH,20,QFont.Bold));mt.setStyleSheet(f"color:{GOLD};letter-spacing:8px;background:transparent;border:none;")
        tc.addWidget(mt)
        st=QLabel(">>  WAYNECORE ASSISTANT SYSTEM v2.1");st.setFont(QFont(FC,8));st.setStyleSheet(f"color:{BLUE};letter-spacing:4px;background:transparent;border:none;")
        tc.addWidget(st);lay.addLayout(tc);lay.addStretch()
        # Compact SYSTEM ONLINE pill so it doesn't overlap adjacent header text
        sf=QFrame();sf.setStyleSheet("QFrame{background:rgba(0,255,136,18);border:1.5px solid rgba(0,255,136,80);border-radius:4px;}")
        sf.setFixedHeight(44)
        sf.setMaximumWidth(240)
        sfl=QHBoxLayout(sf);sfl.setContentsMargins(12,4,12,4);sfl.setSpacing(6)
        self._dot=QLabel("●");self._dot.setFont(QFont(FM,7));self._dot.setStyleSheet(f"color:{GREEN};border:none;background:transparent;")
        sfl.addWidget(self._dot)
        self._status_text=QLabel("SYSTEM ONLINE");self._status_text.setFont(QFont(FC,8,QFont.Bold));self._status_text.setStyleSheet(f"color:{GREEN};letter-spacing:2px;border:none;background:transparent;")
        sfl.addWidget(self._status_text);lay.addWidget(sf);lay.addSpacing(20)
        dtc=QVBoxLayout();dtc.setSpacing(2)
        self.time_label=QLabel("00:00:00");self.time_label.setFont(QFont(FC,18,QFont.Bold));self.time_label.setStyleSheet(f"color:{GOLD};background:transparent;border:none;");self.time_label.setAlignment(Qt.AlignRight)
        dtc.addWidget(self.time_label)
        self.date_label=QLabel("");self.date_label.setFont(QFont(FC,8));self.date_label.setStyleSheet("color:rgba(201,162,39,160);background:transparent;border:none;letter-spacing:1px;");self.date_label.setAlignment(Qt.AlignRight)
        dtc.addWidget(self.date_label);lay.addLayout(dtc);lay.addSpacing(12)
        # Language toggle button
        self._lang_btn=QPushButton("\U0001f1ec\U0001f1e7 EN");self._lang_btn.setFixedSize(60,38);self._lang_btn.setCursor(Qt.PointingHandCursor);self._lang_btn.setFont(QFont(FM,9,QFont.Bold))
        self._lang_btn.setStyleSheet(f"QPushButton{{background:rgba(201,162,39,20);border:1.5px solid rgba(201,162,39,80);color:{GOLD};border-radius:4px;}}QPushButton:hover{{background:rgba(201,162,39,60);}}")
        self._lang_btn.clicked.connect(self.lang_clicked.emit);lay.addWidget(self._lang_btn)
        # Header action buttons
        for icon,sig in [("\U0001f514",self.notify_clicked),("\U0001f4ca",self.stats_clicked),("\u2699",self.settings_clicked),("\u23fb",self.power_clicked)]:
            b=QPushButton(icon);b.setFixedSize(40,38);b.setCursor(Qt.PointingHandCursor);b.setFont(QFont(FM,13))
            b.setStyleSheet(f"QPushButton{{background:rgba(201,162,39,15);border:1.5px solid rgba(201,162,39,60);color:{GOLD};border-radius:4px;}}QPushButton:hover{{background:rgba(201,162,39,60);border-color:{GOLD};}}")
            b.clicked.connect(sig.emit);lay.addWidget(b)
    def update_lang_btn(self,flag,label):self._lang_btn.setText(f"{flag} {label}")
    def update_time(self):
        now=datetime.now();self.time_label.setText(now.strftime("%H:%M:%S"));self.date_label.setText(now.strftime("%A, %b %d, %Y").upper())
    def set_angle(self,a):self._bat.set_angle(a)
    def set_status(self,text,color=GREEN):
        self._status_text.setText(text);self._status_text.setStyleSheet(f"color:{color};letter-spacing:2px;border:none;background:transparent;")
        self._dot.setStyleSheet(f"color:{color};border:none;background:transparent;")
    def paintEvent(self,event):
        super().paintEvent(event);p=QPainter(self);w=self.width()
        g=QLinearGradient(0,0,w,0);g.setColorAt(0,QColor(0,0,0,0));g.setColorAt(0.2,QColor(201,162,39,180));g.setColorAt(0.5,QColor(0,212,255,220));g.setColorAt(0.8,QColor(201,162,39,180));g.setColorAt(1,QColor(0,0,0,0))
        p.fillRect(QRectF(0,0,w,2),g)
        g2=QLinearGradient(0,0,w,0);g2.setColorAt(0,QColor(0,0,0,0));g2.setColorAt(0.3,QColor(201,162,39,60));g2.setColorAt(0.7,QColor(201,162,39,60));g2.setColorAt(1,QColor(0,0,0,0))
        p.fillRect(QRectF(0,self.height()-1,w,1),g2);p.end()

class AICoreWidget(QWidget):
    def __init__(self,parent=None):super().__init__(parent);self.setFixedHeight(340);self._angle=0.0
    def set_angle(self,a):self._angle=a;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);w,h=self.width(),self.height();cx,cy=w/2,h/2-40;pulse=0.7+0.3*math.sin(self._angle)
        pen3=QPen(QColor(201,162,39,int(50*pulse)),1);pen3.setStyle(Qt.DashLine);p.setPen(pen3);p.setBrush(Qt.NoBrush);p.drawEllipse(QRectF(cx-100,cy-100,200,200))
        p.setPen(QPen(QColor(0,212,255,int(77*pulse)),1));p.drawEllipse(QRectF(cx-90,cy-90,180,180))
        p.setPen(QPen(QColor(201,162,39,int(100*pulse)),1));p.drawEllipse(QRectF(cx-80,cy-80,160,160))
        for r,col,spd in [(80,QColor(201,162,39),0.8),(90,QColor(0,212,255),-0.6)]:
            a=self._angle*spd;dx=cx+r*math.cos(a);dy=cy+r*math.sin(a);p.setPen(Qt.NoPen)
            gl=QRadialGradient(dx,dy,10);gl.setColorAt(0,QColor(col.red(),col.green(),col.blue(),int(150*pulse)));gl.setColorAt(1,QColor(0,0,0,0))
            p.setBrush(gl);p.drawEllipse(QRectF(dx-10,dy-10,20,20));p.setBrush(col);p.drawEllipse(QRectF(dx-4,dy-4,8,8))
        for i in range(4):
            sx2=cx-40+i*27;phase=self._angle*2+i*1.2;sy2=cy-80+55*((math.sin(phase)+1)/2)
            g=QLinearGradient(sx2,sy2,sx2,sy2+40);g.setColorAt(0,QColor(201,162,39,int(130*pulse)));g.setColorAt(1,QColor(0,0,0,0))
            p.setPen(Qt.NoPen);p.setBrush(g);p.drawRect(QRectF(sx2,sy2,2,40))
        hr=60;hp=QPolygonF()
        for i in range(6):
            a2=i*math.pi/3-math.pi/6;hp.append(QPointF(cx+hr*math.cos(a2),cy+hr*math.sin(a2)))
        hpath=QPainterPath();hpath.addPolygon(hp);hpath.closeSubpath()
        hf=QLinearGradient(cx-hr,cy-hr,cx+hr,cy+hr);hf.setColorAt(0,QColor(201,162,39,int(77*pulse)));hf.setColorAt(1,QColor(0,212,255,int(26*pulse)))
        p.fillPath(hpath,hf);p.setPen(QPen(QColor(201,162,39,int(130*pulse)),1.5));p.setBrush(Qt.NoBrush);p.drawPath(hpath)
        p.setPen(QColor(201,162,39,int(240*pulse)));p.setFont(QFont(FH,22,QFont.Bold));p.drawText(QRectF(cx-30,cy-14,60,28),Qt.AlignCenter,"AI")
        # Text placed well below the outermost orbit ring (radius 100)
        text_y=cy+115
        p.setPen(QColor(255,255,255,int(220*pulse)));p.setFont(QFont(FH,16,QFont.Bold));p.drawText(QRectF(0,text_y,w,24),Qt.AlignCenter,"ALFRED")
        p.setPen(QColor(0,212,255,int(170*pulse)));p.setFont(QFont(FC,8));p.drawText(QRectF(0,text_y+24,w,14),Qt.AlignCenter,"NEURAL ENGINE v3.2.1");p.end()

class ResourceBar(QWidget):
    def __init__(self,icon_text,label,bar_color,parent=None):
        super().__init__(parent);self.setFixedHeight(54);self._icon=icon_text;self._label=label;self._color=bar_color;self._value=0
    def set_value(self,v):self._value=v;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);w=self.width()
        # Icon box with subtle glow
        p.setPen(QPen(QColor(201,162,39,60),1));p.setBrush(QColor(201,162,39,18))
        p.drawRoundedRect(QRectF(10,8,36,36),4,4)
        p.setPen(QColor(255,255,255));p.setFont(QFont(FM,13));p.drawText(QRectF(10,8,36,36),Qt.AlignCenter,self._icon)
        lx=56;p.setPen(QColor(255,255,255,180));p.setFont(QFont(FC,8,QFont.Bold));p.drawText(QRectF(lx,8,200,16),Qt.AlignLeft|Qt.AlignVCenter,self._label)
        p.setPen(QColor(GOLD));p.setFont(QFont(FC,9,QFont.Bold));p.drawText(QRectF(lx,8,w-lx-14,16),Qt.AlignRight|Qt.AlignVCenter,f"{self._value}%")
        by=30;bw=w-lx-14;bh=5
        # Track
        p.setPen(Qt.NoPen);p.setBrush(QColor(255,255,255,20));p.drawRoundedRect(QRectF(lx,by,bw,bh),2,2)
        # Fill
        fw=bw*min(self._value,100)/100;c=QColor(self._color)
        g=QLinearGradient(lx,0,lx+fw,0);g.setColorAt(0,c);g.setColorAt(1,c.lighter(140))
        p.setBrush(g);p.drawRoundedRect(QRectF(lx,by,fw,bh),2,2)
        # Glow at tip
        if fw>10:
            sh=QRadialGradient(lx+fw,by+bh/2,12);sh.setColorAt(0,QColor(255,255,255,50));sh.setColorAt(1,QColor(0,0,0,0));p.setBrush(sh);p.drawEllipse(QRectF(lx+fw-12,by-6,24,bh+12))
        p.end()

class ChatMessage(QFrame):
    def __init__(self,sender,text,timestamp=None,is_alfred=True,model_tag=None,parent=None):
        super().__init__(parent);self.setStyleSheet("QFrame{background:transparent;border:none;}")
        layout=QHBoxLayout(self);layout.setContentsMargins(10,6,10,6);layout.setSpacing(12)
        ts=timestamp or datetime.now().strftime("%H:%M:%S");color=GOLD if is_alfred else BLUE;letter="A" if is_alfred else "W";qc=QColor(color)
        if not is_alfred:layout.addStretch()
        avatar=HexAvatar(letter,color);content=QVBoxLayout();content.setSpacing(4)
        hdr=QHBoxLayout();hdr.setSpacing(10)
        # Sender + timestamp (ALFRED left, MASTER right)
        base_sender = "ALFRED" if is_alfred else "MASTER WAYNE"
        if is_alfred and model_tag:
            tag = str(model_tag).upper()
            dot_color = GREEN if "OLLAMA" in tag else BLUE
            base_sender = f'ALFRED <span style="color:{dot_color}">●</span> <span style="color:{dot_color}">{tag}</span>'
        sl=QLabel(base_sender);sl.setTextFormat(Qt.RichText);sl.setFont(QFont(FH,8,QFont.Bold));sl.setStyleSheet(f"color:{color};letter-spacing:2px;background:transparent;border:none;")
        tl=QLabel(ts);tl.setFont(QFont(FC,7));tl.setStyleSheet("color:rgba(255,255,255,80);background:transparent;border:none;")
        if not is_alfred:
            hdr.addStretch()
        hdr.addWidget(sl)
        hdr.addWidget(tl)
        if is_alfred:
            hdr.addStretch()
        content.addLayout(hdr)
        # Use QTextBrowser so long responses never get cut off and height auto-expands
        bubble=QTextBrowser();bubble.setOpenExternalLinks(True)
        bubble.setFrameShape(QFrame.NoFrame)
        bubble.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bubble.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bubble.setReadOnly(True)
        bubble.setFont(QFont(FM,11))
        # Wrap aggressively so users never need horizontal scrolling to read long replies.
        bubble.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        bubble.setText(text)
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        bubble.setMaximumHeight(16777215)
        bs="border-left" if is_alfred else "border-right"
        bubble.setStyleSheet(
            f"QTextBrowser{{color:rgba(255,255,255,230);background:rgba({qc.red()},{qc.green()},{qc.blue()},20);"
            f"border:1px solid rgba({qc.red()},{qc.green()},{qc.blue()},60);{bs}:3px solid {color};"
            f"padding:12px 16px;border-radius:4px;}}"
            f"QTextBrowser:focus{{outline:none;}}"
        )
        self._bubble=bubble
        content.addWidget(bubble)
        if is_alfred:layout.addWidget(avatar,alignment=Qt.AlignTop);layout.addLayout(content);layout.addStretch()
        else:layout.addLayout(content);layout.addWidget(avatar,alignment=Qt.AlignTop)


    def set_bubble_width(self,px:int):
        try:
            px=max(260,int(px))
            self._bubble.setFixedWidth(px)
            # Ensure wrapping uses the current width, then let height expand naturally
            self._bubble.document().setTextWidth(px-32)
            doc_h=int(self._bubble.document().size().height())
            self._bubble.setMinimumHeight(max(44, doc_h+26))
        except Exception:
            pass

class HexAvatar(QWidget):
    def __init__(self,letter,color,parent=None):
        super().__init__(parent);self.setFixedSize(44,44);self._letter=letter;self._color=QColor(color)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);cx,cy,r=22,22,20
        hp=QPolygonF()
        for i in range(6):a=i*math.pi/3-math.pi/6;hp.append(QPointF(cx+r*math.cos(a),cy+r*math.sin(a)))
        path=QPainterPath();path.addPolygon(hp);path.closeSubpath();c=self._color
        fill=QLinearGradient(0,0,44,44);fill.setColorAt(0,QColor(c.red(),c.green(),c.blue(),77));fill.setColorAt(1,QColor(c.red(),c.green(),c.blue(),26))
        p.fillPath(path,fill);p.setPen(QPen(c,1.5));p.setBrush(Qt.NoBrush);p.drawPath(path)
        p.setPen(c);p.setFont(QFont(FH,14,QFont.Bold));p.drawText(QRectF(0,0,44,44),Qt.AlignCenter,self._letter);p.end()

class TypingIndicator(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent);self.setStyleSheet("QFrame{background:transparent;border:none;}")
        layout=QHBoxLayout(self);layout.setContentsMargins(10,6,10,6);layout.setSpacing(12)
        layout.addWidget(HexAvatar("A",GOLD),alignment=Qt.AlignTop)
        self._dots=QLabel("\u25cf  \u25cf  \u25cf");self._dots.setFont(QFont(FM,14,QFont.Bold))
        self._dots.setStyleSheet(f"QLabel{{color:{GOLD};background:rgba(201,162,39,20);border:1px solid rgba(201,162,39,60);border-left:3px solid {GOLD};padding:14px 22px;border-radius:4px;}}")
        layout.addWidget(self._dots);layout.addStretch();self._step=0
        self._timer=QTimer();self._timer.timeout.connect(self._anim);self._timer.start(400)
    def _anim(self):
        s=["\u25cf  \u25cb  \u25cb","\u25cb  \u25cf  \u25cb","\u25cb  \u25cb  \u25cf","\u25cf  \u25cf  \u25cb","\u25cb  \u25cf  \u25cf","\u25cf  \u25cf  \u25cf"];self._step=(self._step+1)%len(s);self._dots.setText(s[self._step])
    def cleanup(self):self._timer.stop()

class VoiceVisualizer(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.setFixedHeight(90);self._angle=0.0;self._active=True;self._status_text="\u25cf VOICE RECOGNITION ACTIVE"
    def set_angle(self,a):self._angle=a;self.update()
    def set_active(self,v):self._active=v;self.update()
    def set_status(self,t):self._status_text=t;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);w,h=self.width(),self.height();cx=w/2
        p.fillRect(self.rect(),QColor(0,0,0,100))
        # Subtle top/bottom lines
        g=QLinearGradient(0,0,w,0);g.setColorAt(0,QColor(0,0,0,0));g.setColorAt(0.3,QColor(201,162,39,40));g.setColorAt(0.7,QColor(201,162,39,40));g.setColorAt(1,QColor(0,0,0,0))
        p.fillRect(QRectF(0,0,w,1),g);p.fillRect(QRectF(0,h-1,w,1),g)
        if not self._active:
            p.setPen(QColor(201,162,39,80));p.setFont(QFont(FC,8,QFont.Bold));p.drawText(QRectF(0,h-20,w,18),Qt.AlignCenter,self._status_text);p.end();return
        pulse=0.6+0.4*math.sin(self._angle);n,bw,gap=30,4,2;total=n*(bw+gap);sx=cx-total/2;p.setPen(Qt.NoPen)
        for i in range(n):
            bx=sx+i*(bw+gap);dist=abs(i-n//2)/(n//2);max_h=48*(1-dist*0.5);delay=abs(i-n//2)*0.05
            bh=6+max_h*abs(math.sin(self._angle*2.5+delay*20+i*0.25));bar_cy=38
            g=QLinearGradient(bx,bar_cy-bh/2,bx,bar_cy+bh/2);g.setColorAt(0,QColor(GOLD_BRIGHT));g.setColorAt(0.5,QColor(GOLD));g.setColorAt(1,QColor(GOLD_DIM))
            p.setBrush(g);p.drawRoundedRect(QRectF(bx,bar_cy-bh/2,bw,bh),2,2)
        p.setPen(QColor(201,162,39,int(180*pulse)));p.setFont(QFont(FC,8,QFont.Bold));p.drawText(QRectF(0,h-20,w,18),Qt.AlignCenter,self._status_text);p.end()

class CommandButton(QPushButton):
    def __init__(self,icon,label,parent=None):
        super().__init__(parent);self.setFixedHeight(70);self.setCursor(Qt.PointingHandCursor);self._icon=icon;self._label=label
        self.setStyleSheet(f"QPushButton{{background:rgba(201,162,39,8);border:1px solid rgba(201,162,39,40);border-radius:4px;}}QPushButton:hover{{background:rgba(201,162,39,30);border-color:rgba(201,162,39,120);}}")
    def paintEvent(self,event):
        super().paintEvent(event);p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);w,h=self.width(),self.height()
        p.setPen(QColor(255,255,255));p.setFont(QFont(FM,20));p.drawText(QRectF(0,6,w,32),Qt.AlignCenter,self._icon)
        p.setPen(QColor(255,255,255,200));p.setFont(QFont(FC,7,QFont.Bold));p.drawText(QRectF(0,42,w,16),Qt.AlignCenter,self._label);p.end()

class PerformanceArc(QWidget):
    def __init__(self,label,color,parent=None):
        super().__init__(parent);self.setFixedSize(85,100);self._label=label;self._color=QColor(color);self._value=0
    def set_value(self,v):self._value=v;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);w,h=self.width(),self.height();cx,cy,r=w/2,38,30
        # Track ring
        p.setPen(QPen(QColor(255,255,255,20),5));p.setBrush(Qt.NoBrush);p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
        # Value arc
        span=int(-360*self._value/100*16);p.setPen(QPen(self._color,5,cap=Qt.RoundCap));p.drawArc(QRectF(cx-r,cy-r,r*2,r*2),90*16,span)
        # Percentage text
        p.setPen(self._color);p.setFont(QFont(FC,12,QFont.Bold));p.drawText(QRectF(cx-r,cy-10,r*2,20),Qt.AlignCenter,f"{self._value}%")
        # Label
        p.setPen(QColor(255,255,255,160));p.setFont(QFont(FC,7,QFont.Bold));p.drawText(QRectF(0,h-16,w,14),Qt.AlignCenter,self._label);p.end()

class LogItem(QFrame):
    def __init__(self,icon,text,time_str,status="success",parent=None):
        super().__init__(parent);self.setFixedHeight(44)
        self.setStyleSheet("QFrame{background:transparent;border:none;border-bottom:1px solid rgba(255,255,255,8);}")
        layout=QHBoxLayout(self);layout.setContentsMargins(10,4,10,4);layout.setSpacing(10)
        c=GREEN if status=="success" else(GOLD if status=="pending" else RED);qc=QColor(c)
        il=QLabel(icon);il.setFixedSize(28,28);il.setAlignment(Qt.AlignCenter);il.setFont(QFont(FM,11))
        il.setStyleSheet(f"QLabel{{background:rgba({qc.red()},{qc.green()},{qc.blue()},20);border:1px solid rgba({qc.red()},{qc.green()},{qc.blue()},60);border-radius:4px;color:{c};}}")
        layout.addWidget(il);info=QVBoxLayout();info.setSpacing(2)
        al=QLabel(text);al.setFont(QFont(FM,9));al.setStyleSheet("color:rgba(255,255,255,210);border:none;background:transparent;");info.addWidget(al)
        tl=QLabel(time_str);tl.setFont(QFont(FC,7));tl.setStyleSheet("color:rgba(255,255,255,80);border:none;background:transparent;");info.addWidget(tl)
        layout.addLayout(info);layout.addStretch()

class FooterBar(TechFrame):
    model_toggled=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__("footer", parent);self.setFixedHeight(36);self.setStyleSheet(f"QFrame{{background:{PANEL_BG};border:1px solid rgba(201,162,39,40);border-radius:2px;}}")
        lay=QHBoxLayout(self);lay.setContentsMargins(25,0,25,0);lay.setSpacing(0)
        self.uptime_label=self._s("UPTIME:","0H 0M 0S");lay.addWidget(self.uptime_label);lay.addWidget(self._d())
        self.cmd_label=self._s("COMMANDS:","0");lay.addWidget(self.cmd_label);lay.addWidget(self._d())
        self.rate_label=self._s("SUCCESS RATE:","100%");lay.addWidget(self.rate_label);lay.addStretch()
        # Model toggle button
        self._model_btn=QPushButton("\u21c4");self._model_btn.setFixedSize(28,22);self._model_btn.setCursor(Qt.PointingHandCursor);self._model_btn.setFont(QFont(FM,10))
        self._model_btn.setToolTip("Switch AI Model")
        self._model_btn.setStyleSheet(f"QPushButton{{background:rgba(201,162,39,40);border:1px solid rgba(201,162,39,100);color:{GOLD};border-radius:2px;}}QPushButton:hover{{background:rgba(201,162,39,100);}}")
        self._model_btn.clicked.connect(self.model_toggled.emit);lay.addWidget(self._model_btn)
        lay.addSpacing(4)
        self.model_label=self._s("MODEL:","LLAMA-3.3");lay.addWidget(self.model_label)
        lay.addSpacing(10);lay.addWidget(self._d());lay.addSpacing(10)
        vl=QLabel("ALFREDX WAYNECORE v2.1 | WAYNE INDUSTRIES");vl.setFont(QFont(FC,7));vl.setStyleSheet("color:rgba(255,255,255,77);letter-spacing:2px;background:transparent;border:none;");lay.addWidget(vl)
    def _s(self,label,value):
        w=QLabel(f'<span style="color:rgba(255,255,255,128)">{label}</span> <span style="color:{GOLD}">{value}</span>');w.setFont(QFont(FC,8));w.setStyleSheet("background:transparent;border:none;padding:0 8px;");return w
    def _d(self):d=QFrame();d.setFixedSize(1,16);d.setStyleSheet("background:rgba(201,162,39,77);border:none;");return d

class ChatInput(QTextEdit):
    submitted=pyqtSignal(str)
    def __init__(self,parent=None):
        super().__init__(parent);self.setPlaceholderText("Enter command or speak to Alfred...");self.setFont(QFont(FM,12));self.setFixedHeight(70);self.setAcceptRichText(False)
        self.setStyleSheet(f"QTextEdit{{background:rgba(8,12,28,0.9);border:2px solid rgba(201,162,39,50);color:white;padding:12px 18px;border-radius:4px;}}QTextEdit:focus{{border-color:rgba(201,162,39,180);}}")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    def keyPressEvent(self,event):
        if event.key() in(Qt.Key_Return,Qt.Key_Enter):
            if event.modifiers()&Qt.ShiftModifier:super().keyPressEvent(event)
            else:
                text=self.toPlainText().strip()
                if text:self.submitted.emit(text);self.clear()
        else:super().keyPressEvent(event)

class NotificationDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle("Notifications");self.setFixedSize(460,360)
        self.setStyleSheet("QDialog{background:rgb(5,10,25);border:1px solid rgba(201,162,39,80);}")
        layout=QVBoxLayout(self);layout.setContentsMargins(28,28,28,28);layout.setSpacing(14)
        title=QLabel("\u26a1 NOTIFICATIONS");title.setFont(QFont(FH,12,QFont.Bold));title.setStyleSheet(f"color:{GOLD};letter-spacing:4px;");layout.addWidget(title)
        for emoji,tag,msg,color in[("\U0001f534","ALERT:","Unusual network activity detected on Port 443 \u2014 resolved.",RED),("\U0001f7e1","PENDING:","Wayne Enterprises quarterly report due in 3 days.",GOLD),("\U0001f7e2","INFO:","System backup completed successfully.",GREEN),("\U0001f7e2","INFO:","All security protocols updated to latest version.",GREEN)]:
            lbl=QLabel(f"{emoji} <span style='color:{color};font-weight:bold'>{tag}</span> {msg}");lbl.setWordWrap(True);lbl.setFont(QFont(FM,10));lbl.setStyleSheet("color:rgba(255,255,255,200);padding:6px 0;");layout.addWidget(lbl)
        layout.addStretch()
        btn=QPushButton("DISMISS");btn.setFont(QFont(FH,9,QFont.Bold));btn.setStyleSheet(f"QPushButton{{background:rgba(201,162,39,51);border:1px solid {GOLD};color:{GOLD};padding:8px 30px;letter-spacing:2px;}}QPushButton:hover{{background:rgba(201,162,39,102);}}")
        btn.setCursor(Qt.PointingHandCursor);btn.clicked.connect(self.accept);layout.addWidget(btn,alignment=Qt.AlignCenter)

class SettingsDialog(QDialog):
    def __init__(self, settings_state, parent=None):
        super().__init__(parent)
        self._state = settings_state
        self.setWindowTitle("AlfredX Settings")
        self.setFixedSize(460, 480)
        self.setStyleSheet("QDialog{background:rgb(5,10,25);border:1px solid rgba(201,162,39,100);}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(3)

        # Title
        title = QLabel("⚙️  SYSTEM SETTINGS")
        title.setFont(QFont(FH, 11, QFont.Bold))
        title.setStyleSheet(f"color:{GOLD};letter-spacing:3px;")
        layout.addWidget(title)
        layout.addSpacing(10)

        # ── Toggle settings ──────────────────────────────────
        self._toggles = {}
        for key in self._state:
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 6, 0, 6)
            lbl = QLabel(key)
            lbl.setFont(QFont(FC, 9))
            lbl.setStyleSheet("color:rgba(255,255,255,180);")
            btn = QPushButton("ON" if self._state[key] else "OFF")
            btn.setFixedSize(50, 24)
            btn.setCursor(Qt.PointingHandCursor)
            self._us(btn, self._state[key])
            btn.clicked.connect(lambda _, k=key, b=btn: self._tog(k, b))
            rl.addWidget(lbl)
            rl.addStretch()
            rl.addWidget(btn)
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background:rgba(255,255,255,13);")
            layout.addWidget(row)
            layout.addWidget(sep)
            self._toggles[key] = btn

        layout.addSpacing(14)

        # ── Divider ──────────────────────────────────────────
        div_label = QLabel("🔑  API KEYS & CREDENTIALS")
        div_label.setFont(QFont(FH, 9, QFont.Bold))
        div_label.setStyleSheet(f"color:{GOLD};letter-spacing:2px;")
        layout.addWidget(div_label)

        div_line = QFrame()
        div_line.setFixedHeight(1)
        div_line.setStyleSheet(f"background:rgba(201,162,39,60);")
        layout.addWidget(div_line)
        layout.addSpacing(8)

        # ── Update API Keys button ───────────────────────────
        api_btn = QPushButton("  🔑  Update API Keys  ")
        api_btn.setFont(QFont(FH, 9, QFont.Bold))
        api_btn.setFixedHeight(38)
        api_btn.setCursor(Qt.PointingHandCursor)
        api_btn.setStyleSheet(
            f"QPushButton{{background:rgba(201,162,39,30);border:1.5px solid rgba(201,162,39,120);"
            f"color:{GOLD};border-radius:4px;letter-spacing:1px;}}"
            f"QPushButton:hover{{background:rgba(201,162,39,80);}}"
        )
        api_btn.clicked.connect(self._open_api_settings)
        layout.addWidget(api_btn)

        layout.addStretch()

        # ── Close button ─────────────────────────────────────
        close_btn = QPushButton("CLOSE")
        close_btn.setFont(QFont(FH, 9, QFont.Bold))
        close_btn.setStyleSheet(
            f"QPushButton{{background:rgba(201,162,39,51);border:1px solid {GOLD};"
            f"color:{GOLD};padding:8px 30px;letter-spacing:2px;}}"
            f"QPushButton:hover{{background:rgba(201,162,39,102);}}"
        )
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

    def _open_api_settings(self):
        from setup_wizard import open_settings
        self.accept()          # close this dialog first
        open_settings()        # then open the API keys wizard

    def _tog(self, key, btn):
        self._state[key] = not self._state[key]
        btn.setText("ON" if self._state[key] else "OFF")
        self._us(btn, self._state[key])

    def _us(self, btn, on):
        if on:
            btn.setStyleSheet(
                f"QPushButton{{background:rgba(0,255,136,77);border:1px solid rgba(0,255,136,120);"
                f"color:{GREEN};border-radius:12px;font-size:9px;}}"
                f"QPushButton:hover{{background:rgba(0,255,136,120);}}"
            )
        else:
            btn.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,25);border:1px solid rgba(255,255,255,50);"
                "color:rgba(255,255,255,100);border-radius:12px;font-size:9px;}"
                "QPushButton:hover{background:rgba(255,255,255,50);}"
            )
# ═══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════
class MainWindow(QWidget):
    command_submitted=pyqtSignal(str)
    def __init__(self,parent=None):
        super().__init__(parent);self._anim_angle=0.0;self._start_time=time.time();self._cmd_count=0;self._success_count=0;self._is_processing=False;self._mic_active=False;self._typing_widget=None;self._current_model="groq"
        self._settings=self._load_settings()
        self._processing_start = 0 
        self._particles=[];random.seed(42)
        for _ in range(9):self._particles.append({'x':random.uniform(0,1),'phase':random.uniform(0,2*math.pi),'speed':random.uniform(0.3,1.0),'size':random.uniform(1.5,3)})
        self._signals=_SignalBridge();self._lang=LanguageSwitcher("en")
        self._signals.ai_response.connect(self._on_ai_response);self._signals.voice_heard.connect(self._on_voice_heard);self._signals.voice_error.connect(self._on_voice_error);self._signals.tts_done.connect(self._on_tts_done);self._signals.wake_detected.connect(self._on_wake_detected);self._signals.reminder_fired.connect(self._on_reminder)
        self._init_engines();self._build();self._setup_shortcuts()
        self._timer=QTimer();self._timer.timeout.connect(self._tick);self._timer.start(33)
        # Chat History Restore
        self.session_id=chat_db.get_last_session_id()
        if self.session_id:
            for msg in chat_db.get_messages(self.session_id):
                name="ALFRED" if msg["role"]=="assistant" else "MASTER WAYNE"
                self.add_message(name,msg["content"],is_alfred=(msg["role"]=="assistant"))
        else:
            self.session_id=chat_db.create_session()
        # Hotkey
        self._hotkey=GlobalHotkey("ctrl+shift+a")
        self._hotkey.summoned.connect(self._summon)
        self._hotkey.start()
        

    # ── Settings Persistence ──
    def _load_settings(self):
        defaults={"VOICE RECOGNITION":True,"PARTICLE EFFECTS":True,"SCANLINE OVERLAY":True,"AUTO-SCROLL CHAT":True}
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE,"r",encoding="utf-8") as f:
                    saved=json.load(f)
                    defaults.update(saved)
                    print("[MW] Settings loaded from file")
        except Exception as e:
            print(f"[MW] Settings load error: {e}")
        return defaults

    def _save_settings(self):
        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE),exist_ok=True)
            with open(SETTINGS_FILE,"w",encoding="utf-8") as f:
                json.dump(self._settings,f,indent=2)
            print("[MW] Settings saved")
        except Exception as e:
            print(f"[MW] Settings save error: {e}")

    # ── Keyboard Shortcuts ──
    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+L"),self,self._clear_chat)
        QShortcut(QKeySequence("Ctrl+N"),self,self._new_chat)
        QShortcut(QKeySequence("Escape"),self,self.showMinimized)
        QShortcut(QKeySequence("Ctrl+M"),self,self._toggle_mic)
        QShortcut(QKeySequence("Ctrl+Q"),self,self._quit_app)

    def _init_engines(self):
        self._cmd_handler=self._ai=self._memory=self._stt=self._tts=self._wake=None
        try:
            from core.commands import CommandHandler;self._cmd_handler=CommandHandler();self._cmd_handler.set_reminder_callback(lambda t:self._signals.reminder_fired.emit(t));print("[MW] \u2713 CommandHandler")
        except Exception as e:print(f"[MW] \u2717 CommandHandler: {e}")
        try:
            from core.ai_engine import AIEngine;self._ai=AIEngine();print("[MW] \u2713 AIEngine")
        except Exception as e:print(f"[MW] \u2717 AIEngine: {e}")
        try:
            from core.memory import Memory;self._memory=Memory()
            if self._ai:self._ai.memory=self._memory
            print("[MW] \u2713 Memory")
        except Exception as e:print(f"[MW] \u2717 Memory: {e}")
        try:
            from core.speech_engine import SpeechEngine;self._stt=SpeechEngine();print("[MW] \u2713 SpeechEngine")
        except Exception as e:print(f"[MW] \u2717 SpeechEngine: {e}")
        try:
            from core.tts_engine import TTSEngine;self._tts=TTSEngine();print("[MW] \u2713 TTSEngine")
        except Exception as e:print(f"[MW] \u2717 TTSEngine: {e}")
        try:
            from core.wake_word import WakeWordDetector;self._wake=WakeWordDetector();print("[MW] \u2713 WakeWordDetector")
        except Exception as e:print(f"[MW] \u2717 WakeWordDetector: {e}")

    def cleanup(self):
        try:
            if self._stt:self._stt.stop()
            if self._tts:self._tts.stop()
            if self._wake:self._wake.stop()
        except:pass

    def _tick(self):
        self._anim_angle+=0.02;self._header.update_time();self._header.set_angle(self._anim_angle);self._ai_core.set_angle(self._anim_angle);self._visualizer.set_angle(self._anim_angle);self._update_resources();self._update_uptime();self.update()

    def _update_resources(self):
        if not PSUTIL_OK:return
        try:
            cpu=int(psutil.cpu_percent(interval=0));mem=int(psutil.virtual_memory().percent)
            self._cpu_bar.set_value(cpu);self._mem_bar.set_value(mem);self._net_bar.set_value(min(99,cpu+30))
            self._cpu_arc.set_value(cpu);self._ram_arc.set_value(mem);self._gpu_arc.set_value(max(5,cpu//2))
        except:pass

    def _update_uptime(self):
        e=int(time.time()-self._start_time);h,m,s=e//3600,(e%3600)//60,e%60
        self._footer.uptime_label.setText(f'<span style="color:rgba(255,255,255,128)">UPTIME:</span> <span style="color:{GOLD}">{h}H {m}M {s}S</span>')


    def _time_greeting(self):
        h = datetime.now().hour
        if 5 <= h < 12:
            return "Good morning", "morning"
        elif 12 <= h < 17:
            return "Good afternoon", "afternoon"
        elif 17 <= h < 21:
            return "Good evening", "evening"
        else:
            return "Good night", "night"

    def _current_model_tag(self):
        # Used by ChatMessage to draw the colored model dot
        return "OLLAMA" if self._current_model == "ollama" else "LLAMA"

    def _precheck_user_text(self, text: str):
        t = (text or "").strip()
        t = t.replace("supose", "suppose").replace("Supose", "Suppose")
        low = t.lower()
        if low in ("tell me about", "can you please tell me about") or low.endswith("tell me about"):
            self._deliver_response("About what exactly, Master Wayne? Tell me the topic/name.")
            return None
        return t

    def welcome_on_login(self):
        # Greet every time login succeeds (call from main.py after switching to MainWindow)
        if not getattr(self, "session_id", None):
            self.session_id = chat_db.create_session()

        greet, part = self._time_greeting()
        msg = (
            f"{greet}, Master Wayne. All systems are operational and Wayne Tower security protocols are active. "
            f"How may I assist you this {part}?"
        )
        self.add_message("ALFRED", msg, is_alfred=True, model_tag=self._current_model_tag())
        chat_db.add_message(self.session_id, "assistant", msg)
        if self._tts:
            self._tts.speak(msg, callback=lambda: self._signals.tts_done.emit())

    def _build(self):
        self.setStyleSheet("background:#000000;");root=QVBoxLayout(self);root.setContentsMargins(0,0,0,0);root.setSpacing(0)
        # Overall app scroll:
        # - Vertical scroll for smaller heights
        # - Horizontal scroll for smaller widths (so you can reach the right panels)
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{width:6px;background:rgba(0,0,0,0.3);}"
            "QScrollBar::handle:vertical{background:rgba(201,162,39,180);border-radius:3px;min-height:30px;}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}"
            "QScrollBar:horizontal{height:6px;background:rgba(0,0,0,0.3);}"
            "QScrollBar::handle:horizontal{background:rgba(201,162,39,180);border-radius:3px;min-width:30px;}"
            "QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal{width:0;}")
        inner=QWidget();inner.setStyleSheet("background:transparent;")
        inner.setMinimumHeight(800)
        # Keep a cinematic baseline width; on smaller screens, the outer QScrollArea will allow
        # left/right scrolling to reach the right-side panels.
        inner.setMinimumWidth(1320)
        inner_lay=QVBoxLayout(inner);inner_lay.setContentsMargins(20,20,20,20);inner_lay.setSpacing(15)

        self._header=HeaderBar()
        self._header.notify_clicked.connect(self._show_notifications)
        self._header.stats_clicked.connect(lambda:self._process_input("Run full system diagnostic"))
        self._header.settings_clicked.connect(self._show_settings)
        self._header.power_clicked.connect(self._power_off)
        self._header.lang_clicked.connect(self._toggle_language)
        inner_lay.addWidget(self._header)

        main_row=QHBoxLayout();main_row.setSpacing(15)
        # LEFT 280px
        left=QVBoxLayout();left.setSpacing(15);ai_p,ai_l=make_panel("AI CORE STATUS");self._ai_core=AICoreWidget();ai_l.addWidget(self._ai_core);left.addWidget(ai_p)
        res_p,res_l=make_panel("SYSTEM RESOURCES");rc=QVBoxLayout();rc.setContentsMargins(8,14,8,14);rc.setSpacing(4)
        self._cpu_bar=ResourceBar("\u26a1","CPU USAGE",GREEN);self._mem_bar=ResourceBar("\U0001f9e0","MEMORY",BLUE);self._net_bar=ResourceBar("\U0001f4e1","NETWORK",GOLD)
        rc.addWidget(self._cpu_bar);rc.addWidget(self._mem_bar);rc.addWidget(self._net_bar)
        rf=QFrame();rf.setStyleSheet("background:transparent;border:none;");rf.setLayout(rc);res_l.addWidget(rf);left.addWidget(res_p);left.addStretch()
        # Slightly slimmer side columns so the COMMAND INTERFACE gets more width (better chat readability).
        lw=QWidget();lw.setFixedWidth(260);lw.setLayout(left);lw.setStyleSheet("background:transparent;");main_row.addWidget(lw)

        # CENTER flex
        center=QVBoxLayout();center.setSpacing(0);cp,cl=make_panel("COMMAND INTERFACE")
        self._chat_scroll=QScrollArea();self._chat_scroll.setWidgetResizable(True)
        self._chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._chat_scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}QScrollBar:vertical{width:4px;background:rgba(0,0,0,0.3);}QScrollBar::handle:vertical{background:#c9a227;border-radius:2px;}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        self._msg_container=QWidget();self._msg_container.setStyleSheet("background:transparent;")
        self._msg_layout=QVBoxLayout(self._msg_container);self._msg_layout.setAlignment(Qt.AlignTop);self._msg_layout.setSpacing(4);self._msg_layout.setContentsMargins(4,8,4,8)
        self._chat_scroll.setWidget(self._msg_container);cl.addWidget(self._chat_scroll,1)
        self._visualizer=VoiceVisualizer();cl.addWidget(self._visualizer)
        inp_f=QFrame();inp_f.setFixedHeight(80);inp_f.setStyleSheet("background:transparent;border:none;")
        il=QHBoxLayout(inp_f);il.setContentsMargins(15,8,15,8);il.setSpacing(10)
        self._input=ChatInput();self._input.submitted.connect(self._on_submit);il.addWidget(self._input)
        btn_col=QVBoxLayout();btn_col.setSpacing(4);btn_row1=QHBoxLayout();btn_row1.setSpacing(4)
        ab=QPushButton("✚");ab.setFixedSize(38,34);ab.setCursor(Qt.PointingHandCursor);ab.setFont(QFont(FM,13));ab.setToolTip("Attach / Add (Ctrl+O)");ab.setStyleSheet(f"QPushButton{{background:{GOLD};border:none;border-radius:4px;}}QPushButton:hover{{background:{GOLD_BRIGHT};}}");ab.clicked.connect(self._attach_file);btn_row1.addWidget(ab)
        self._mic_btn=QPushButton("🎙️");self._mic_btn.setFixedSize(38,34);self._mic_btn.setCursor(Qt.PointingHandCursor);self._mic_btn.setFont(QFont(FM,13));self._mic_btn.setStyleSheet(f"QPushButton{{background:{RED};border:none;border-radius:4px;}}QPushButton:hover{{background:#ff5555;}}");self._mic_btn.clicked.connect(self._toggle_mic);btn_row1.addWidget(self._mic_btn)
        btn_col.addLayout(btn_row1)
        # Send + Clear buttons row
        btn_row2=QHBoxLayout();btn_row2.setSpacing(4)
        sb=QPushButton("➤");sb.setFixedSize(38,34);sb.setCursor(Qt.PointingHandCursor);sb.setFont(QFont(FM,14));sb.setStyleSheet(f"QPushButton{{background:{BLUE};border:none;border-radius:4px;color:white;}}QPushButton:hover{{background:#00eeff;}}")
        sb.clicked.connect(lambda:self._input.submitted.emit(self._input.toPlainText().strip()) if self._input.toPlainText().strip() else None);btn_row2.addWidget(sb)
        # Clear Chat button
        cb=QPushButton("🗑");cb.setFixedSize(38,34);cb.setCursor(Qt.PointingHandCursor);cb.setFont(QFont(FM,13));cb.setToolTip("Clear Chat (Ctrl+L)")
        cb.setStyleSheet(f"QPushButton{{background:rgba(255,51,51,30);border:1px solid rgba(255,51,51,60);border-radius:4px;color:{RED};}}QPushButton:hover{{background:rgba(255,51,51,80);}}")
        cb.clicked.connect(self._clear_chat);btn_row2.addWidget(cb)
        btn_col.addLayout(btn_row2)
        il.addLayout(btn_col);cl.addWidget(inp_f);center.addWidget(cp)
        cw=QWidget();cw.setLayout(center);cw.setStyleSheet("background:transparent;");main_row.addWidget(cw,1)

        # RIGHT 300px
        right=QVBoxLayout();right.setSpacing(15)
        # Quick commands (no READY badge)
        qp,ql=make_panel("\u26a1 QUICK COMMANDS",status_text=None);qg=QGridLayout();qg.setSpacing(10);qg.setContentsMargins(12,12,12,12)
        for i,(ic,lb) in enumerate([("\U0001f310","BROWSER"),("\U0001f4bb","VS CODE"),("\U0001f3b5","MUSIC"),("\U0001f4c1","FILES"),("\U0001f4f7","VISION"),("\U0001f50d","SEARCH")]):
            b=CommandButton(ic,lb);b.clicked.connect(lambda _,l=lb:self._quick_command(l));qg.addWidget(b,i//2,i%2)
        qf=QFrame();qf.setStyleSheet("background:transparent;border:none;");qf.setLayout(qg);ql.addWidget(qf);right.addWidget(qp)
        pp,pl=make_panel("\U0001f4ca PERFORMANCE");ar=QHBoxLayout();ar.setAlignment(Qt.AlignCenter);ar.setSpacing(10);ar.setContentsMargins(10,12,10,12)
        self._cpu_arc=PerformanceArc("CPU",GREEN);self._ram_arc=PerformanceArc("RAM",BLUE);self._gpu_arc=PerformanceArc("GPU",GOLD)
        ar.addWidget(self._cpu_arc);ar.addWidget(self._ram_arc);ar.addWidget(self._gpu_arc)
        af=QFrame();af.setStyleSheet("background:transparent;border:none;");af.setLayout(ar);pl.addWidget(af);right.addWidget(pp)
        lp,ll=make_panel("\U0001f4dc ACTIVITY LOG");self._log_scroll=QScrollArea();self._log_scroll.setWidgetResizable(True);self._log_scroll.setMaximumHeight(200)
        self._log_scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}QScrollBar:vertical{width:4px;background:rgba(0,0,0,0.3);}QScrollBar::handle:vertical{background:#c9a227;border-radius:2px;}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        self._log_container=QWidget();self._log_container.setStyleSheet("background:transparent;");self._log_layout=QVBoxLayout(self._log_container);self._log_layout.setAlignment(Qt.AlignTop);self._log_layout.setSpacing(0);self._log_layout.setContentsMargins(0,0,0,0)
        self._log_scroll.setWidget(self._log_container);ll.addWidget(self._log_scroll);right.addWidget(lp);right.addStretch()
        rw=QWidget();rw.setFixedWidth(290);rw.setLayout(right);rw.setStyleSheet("background:transparent;");main_row.addWidget(rw)

        inner_lay.addLayout(main_row,1)
        self._footer=FooterBar();self._footer.model_toggled.connect(self._toggle_model);inner_lay.addWidget(self._footer);scroll.setWidget(inner);root.addWidget(scroll)
        now_t=datetime.now().strftime("%H:%M:%S")
        for txt in["System initialized","Neural engine online","Voice module ready","Alfred AI initialized"]:self._add_log("\u2713",txt,now_t,"success")

    def add_message(self,sender,text,timestamp=None,is_alfred=True,model_tag=None):
        msg=ChatMessage(sender,text,timestamp,is_alfred,model_tag=model_tag)
        self._msg_layout.addWidget(msg)
        self._apply_chat_widths()
        if self._settings.get("AUTO-SCROLL CHAT",True):
            QTimer.singleShot(50,lambda:self._chat_scroll.verticalScrollBar().setValue(self._chat_scroll.verticalScrollBar().maximum()))

    def _apply_chat_widths(self):
        # Match HTML-like max width (about 70% of center panel) and prevent cut-off.
        try:
            viewport_w=self._chat_scroll.viewport().width()
            target=int(viewport_w*0.70)
            # walk widgets
            for i in range(self._msg_layout.count()):
                w=self._msg_layout.itemAt(i).widget()
                if hasattr(w,"set_bubble_width"):
                    w.set_bubble_width(target)
        except Exception:
            pass

    def resizeEvent(self,event):
        super().resizeEvent(event)
        QTimer.singleShot(0,self._apply_chat_widths)
    def add_log(self,text,status="success"):self._add_log("\u2713" if status=="success" else("\u23f3" if status=="pending" else "\u2717"),text,datetime.now().strftime("%H:%M:%S"),status)
    def get_input(self):return self._input
    def get_mic_btn(self):return self._mic_btn
    def set_visualizer_active(self,a):self._visualizer.set_active(a)

    def _on_submit(self, text):
        if not text: return
        self._input.clear()
        if self._is_processing:
            # Reset if stuck more than 30 seconds
            if time.time() - self._processing_start > 30:
                self._is_processing = False
                self._hide_typing()
            else:
                self.add_log("Alfred is still thinking, Master...", "pending")
                return
        self._process_input(text)
    def _process_input(self, text):
        checked = self._precheck_user_text(text)
        if checked is None:
            return                          # precheck handled it; _deliver_response
                                            # already cleaned up _is_processing
        text = checked
        if not text:
            return

        if self._tts and self._tts.is_speaking:self._tts.stop()
        self._is_processing=True;self._cmd_count+=1
        self._footer.cmd_label.setText(f'<span style="color:rgba(255,255,255,128)">COMMANDS:</span> <span style="color:{GOLD}">{self._cmd_count}</span>')
        self.add_message("MASTER WAYNE",text,is_alfred=False);chat_db.add_message(self.session_id,"user",text);self.add_log(f"Command: {text[:40]}","pending");self.command_submitted.emit(text)
        if "codex" in text.lower():
            import subprocess;subprocess.Popen(["cmd","/c","start","",os.path.join("data","codex","Alfred_Codex.pdf")],shell=True)
            self._deliver_response("Opening the Alfred Codex, Master Wayne.")
            return
        if self._cmd_handler:
            try:
                handled,response=self._cmd_handler.process(text)
                if handled:self._deliver_response(response);return
            except Exception as e:print(f"[MW] Cmd error: {e}")
        if self._ai:
            self._show_typing()
            lang_hint=self._lang.get("AI_LANG_HINT")
            def _w():
                try:r=self._ai.chat(f"[{lang_hint}] {text}");self._signals.ai_response.emit(r)
                except Exception as e:self._signals.ai_response.emit(f"Apologies Master, error: {str(e)[:100]}")
            threading.Thread(target=_w,daemon=True).start()
        else:self._deliver_response(self._lang.get("OFFLINE_MSG"))

    def _sanitize_reply(self, text: str) -> str:
    # Remove internal memory markers from UI + TTS
        if not text:
            return ""
        # [REMEMBER: ...]
        text = re.sub(r"\[\s*REMEMBER\s*:[^\]]*\]", "", text, flags=re.IGNORECASE)
        # REMEMBER:xxx on its own line
        text = re.sub(r"^\s*REMEMBER\s*:\s*.*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
        # REMEMBER=xxx
        text = re.sub(r"^\s*REMEMBER\s*=\s*.*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
        return text.strip()

    def _on_ai_response(self,text):self._hide_typing();self._deliver_response(text)
    def _sanitize_assistant_text(self, text: str) -> str:
        if not text:
            return ""
        t = str(text)
        # Remove [REMEMBER:...] blocks
        t = re.sub(r"\[\s*REMEMBER\s*:[^\]]*\]", "", t, flags=re.IGNORECASE)
        # Remove REMEMBER: on its own line
        t = re.sub(r"\bREMEMBER\s*:[^\n]*", "", t, flags=re.IGNORECASE)
        # Remove REMEMBER(...) blocks
        t = re.sub(r"\bREMEMBER\s*\([^\)]*\)", "", t, flags=re.IGNORECASE)
        # Remove any leftover lone [ or ] brackets
        t = re.sub(r"^\s*[\[\]]\s*$", "", t, flags=re.MULTILINE)
        # Clean up extra blank lines
        t = re.sub(r"\n{3,}", "\n\n", t).strip()
        # If nothing left after cleaning, return a fallback
        if not t:
            return "I shall attend to that, Master Wayne."
        return t

    def _deliver_response(self,text):
        clean=self._sanitize_assistant_text(text)
        self.add_message("ALFRED", clean, is_alfred=True, model_tag=self._current_model_tag());chat_db.add_message(self.session_id,"assistant",clean);self._success_count+=1
        rate=f"{(self._success_count/max(1,self._cmd_count)*100):.0f}%"
        self._footer.rate_label.setText(f'<span style="color:rgba(255,255,255,128)">SUCCESS RATE:</span> <span style="color:{GOLD}">{rate}</span>')
        self.add_log("Response delivered","success");self._is_processing=False
        if self._tts:self._tts.speak(clean,callback=lambda:self._signals.tts_done.emit())
    def _on_tts_done(self):
        if self._wake and self._settings.get("VOICE RECOGNITION",True) and not self._wake.is_running and not self._mic_active:
            self._wake.start(lambda:self._signals.wake_detected.emit())
    def _on_reminder(self,text):
        self.add_message("ALFRED", f"\u23f0 Reminder: {text}", is_alfred=True, model_tag=self._current_model_tag())
        self.add_log(f"Reminder: {text}", "pending")

    def _show_typing(self):
        if self._typing_widget:return
        self._typing_widget=TypingIndicator();self._msg_layout.addWidget(self._typing_widget)
        QTimer.singleShot(50,lambda:self._chat_scroll.verticalScrollBar().setValue(self._chat_scroll.verticalScrollBar().maximum()))
    def _hide_typing(self):
        if self._typing_widget:self._typing_widget.cleanup();self._msg_layout.removeWidget(self._typing_widget);self._typing_widget.deleteLater();self._typing_widget=None

    def _quick_command(self,label):
        try:
            if label=="BROWSER": webbrowser.open("https://www.google.com"); self.add_log("Browser opened","success"); return
            if label=="SEARCH": webbrowser.open("https://www.google.com"); self.add_log("Search opened","success"); return
            if label=="VS CODE":
                try: subprocess.Popen(["code"], shell=True)
                except Exception: pass
                self.add_log("VS Code launched","success"); return
            if label=="FILES":
                try: os.startfile(os.path.expanduser("~"))
                except Exception: pass
                self.add_log("File explorer opened","success"); return
        except Exception as e:
            self.add_log(f"Quick command error: {e}","error")
        # Fallback to your command pipeline (AI / command handler)
        m={"MUSIC":"play music","VISION":"take screenshot"}
        self._process_input(m.get(label,label.lower()))

    def _toggle_mic(self):
        self._mic_active=not self._mic_active
        if self._mic_active:
            self._mic_btn.setStyleSheet(f"QPushButton{{background:{GREEN};border:none;border-radius:4px;}}QPushButton:hover{{background:#33ff99;}}")
            self._visualizer.set_status(self._lang.get("LISTENING"));self.add_log("Microphone activated","success")
            if self._wake:self._wake.stop()
            if self._stt:self._stt.start_continuous(callback=lambda t:self._signals.voice_heard.emit(t),error_callback=lambda e:self._signals.voice_error.emit(e))
        else:
            self._mic_btn.setStyleSheet(f"QPushButton{{background:{RED};border:none;border-radius:4px;}}QPushButton:hover{{background:#ff5555;}}")
            self._visualizer.set_status(self._lang.get("VOICE_ACTIVE"));self.add_log("Microphone deactivated","pending")
            if self._stt:self._stt.stop_continuous()
    def _on_voice_heard(self,text):self._input.setPlainText(text);QTimer.singleShot(500,lambda:self._process_input(text))
    def _on_voice_error(self,error):self.add_log(f"Voice: {error}","error")
    def _on_wake_detected(self):
        if not self._mic_active:self._toggle_mic();self.add_log("Wake word detected!","success")

    def _toggle_language(self):
        lang=self._lang.toggle()
        self._header.update_lang_btn(self._lang.flag,self._lang.label)
        self._header._status_text.setText(self._lang.get("SYSTEM_ONLINE"))
        self._input.setPlaceholderText(self._lang.get("TYPE_COMMAND"))
        self._visualizer.set_status(self._lang.get("VOICE_ACTIVE"))
        if self._stt:self._stt.set_language(self._lang.get("STT_LANG"))
        if self._tts:self._tts.set_language(self._lang.get("TTS_LANG"))
        self.add_log(f"Language: {lang.upper()}","success")

    def _toggle_model(self):
        if self._current_model=="groq":
            self._current_model="ollama"
            model_name="OLLAMA"
            try:
                from core.ai_engine import AIEngine;self._ai=AIEngine(provider="ollama");print("[MW] Switched to Ollama")
            except Exception as e:
                print(f"[MW] Ollama switch error: {e}");model_name="OLLAMA (ERR)"
        else:
            self._current_model="groq"
            model_name="LLAMA-3.3"
            try:
                from core.ai_engine import AIEngine;self._ai=AIEngine(provider="groq");print("[MW] Switched to Groq")
            except Exception as e:
                print(f"[MW] Groq switch error: {e}");model_name="LLAMA-3.3 (ERR)"
        if self._memory and self._ai:self._ai.memory=self._memory
        self._footer.model_label.setText(f'<span style="color:rgba(255,255,255,128)">MODEL:</span> <span style="color:{GOLD}">{model_name}</span>')
        self.add_log(f"Model: {model_name}","success")

    def _clear_chat(self):
        while self._msg_layout.count():
            item=self._msg_layout.takeAt(0)
            if item.widget():item.widget().deleteLater()
        self.add_log("Chat cleared","success")

    def _new_chat(self):
        self._clear_chat()
        self.session_id=chat_db.create_session()
        self.add_message("ALFRED",self._lang.get("WELCOME"),is_alfred=True)
        self.add_log("New chat session","success")

    def _attach_file(self):
        path,_=QFileDialog.getOpenFileName(self,"Attach File")
        if path:
            name=os.path.basename(path);self.add_log(f"File: {name}","success");self.add_message("MASTER WAYNE",f"\U0001f4ce Attached: {name}",is_alfred=False)
            if self._ai:
                self._show_typing()
                def _w():
                    try:r=self._ai.chat(f"User attached a file named '{name}'. Acknowledge it in character.");self._signals.ai_response.emit(r)
                    except:self._signals.ai_response.emit(f'File "{name}" received, Master. Stored in the secure vault.')
                threading.Thread(target=_w,daemon=True).start()
            else:self._deliver_response(self._lang.get("FILE_RECEIVED"))

    def _show_notifications(self):self.add_log("Notifications opened","success");NotificationDialog(self).exec_()
    def _show_settings(self):
        self.add_log("Settings opened", "success")
        dlg = SettingsDialog(self._settings, self)
        dlg.exec_()
        self._visualizer.set_active(self._settings["VOICE RECOGNITION"])
        self._save_settings()

    def _power_off(self):
        reply = QMessageBox.question(self, "AlfredX", self._lang.get("POWER_QUESTION"), QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.add_log("Shutdown initiated", "error")
            self._header.set_status(self._lang.get("SHUTTING_DOWN"), RED)
            self.add_message("ALFRED", self._lang.get("SHUTDOWN_MSG"), is_alfred=True)
            self.cleanup()
            self._save_settings()
            QTimer.singleShot(3000, lambda: self._header.set_status(self._lang.get("SYSTEM_OFFLINE"), RED))

    def _add_log(self, icon, text, time_str, status):
        self._log_layout.insertWidget(0, LogItem(icon, text, time_str, status))
    def paintEvent(self,event):
        p=QPainter(self);w,h=self.width(),self.height();p.fillRect(self.rect(),QColor(0,0,0))
        g1=QRadialGradient(w*0.2,0,w*0.5);g1.setColorAt(0,QColor(201,162,39,26));g1.setColorAt(1,QColor(0,0,0,0));p.fillRect(self.rect(),g1)
        g2=QRadialGradient(w*0.8,h,w*0.5);g2.setColorAt(0,QColor(0,212,255,20));g2.setColorAt(1,QColor(0,0,0,0));p.fillRect(self.rect(),g2)
        if self._settings.get("PARTICLE EFFECTS",True):
            for pt in self._particles:
                t=self._anim_angle*pt['speed']+pt['phase'];py=h-(((t*30)%(h+100))-50);px=pt['x']*w;alpha=int(153*(0.5+0.5*math.sin(t)))
                p.setPen(Qt.NoPen);p.setBrush(QColor(201,162,39,alpha));p.drawEllipse(QRectF(px-pt['size']/2,py-pt['size']/2,pt['size'],pt['size']))
        gold_pen=QPen(QColor(201,162,39),2);cs=120
        p.setPen(gold_pen);p.setBrush(Qt.NoBrush);p.drawLine(0,0,cs,0);p.drawLine(0,0,0,cs);p.setPen(Qt.NoPen);p.setBrush(QColor(201,162,39));p.drawRect(QRectF(10,10,8,8))
        p.setPen(gold_pen);p.setBrush(Qt.NoBrush);p.drawLine(w-cs,0,w,0);p.drawLine(w,0,w,cs);p.setPen(Qt.NoPen);p.setBrush(QColor(201,162,39));p.drawRect(QRectF(w-18,10,8,8))
        p.setPen(gold_pen);p.setBrush(Qt.NoBrush);p.drawLine(0,h-cs,0,h);p.drawLine(0,h,cs,h);p.setPen(Qt.NoPen);p.setBrush(QColor(201,162,39));p.drawRect(QRectF(10,h-18,8,8))
        p.setPen(gold_pen);p.setBrush(Qt.NoBrush);p.drawLine(w,h-cs,w,h);p.drawLine(w-cs,h,w,h);p.setPen(Qt.NoPen);p.setBrush(QColor(201,162,39));p.drawRect(QRectF(w-18,h-18,8,8))
        if self._settings.get("SCANLINE OVERLAY",True):
            p.setPen(Qt.NoPen)
            for y in range(0,h,2):p.fillRect(QRectF(0,y,w,1),QColor(0,0,0,18))
        p.end()

    def _summon(self):
        import ctypes
        self.setWindowFlags(self.windowFlags()|Qt.WindowStaysOnTopHint)
        self.show()
        self.setWindowFlags(self.windowFlags()&~Qt.WindowStaysOnTopHint)
        self.show()
        self.activateWindow()
        self._input.setFocus()

    def _quit_app(self):
        self._save_settings()
        QApplication.instance().quit()

    def closeEvent(self, event):
        self._save_settings()
        self.cleanup()
        event.accept()