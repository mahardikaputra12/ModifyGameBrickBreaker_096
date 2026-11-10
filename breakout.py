# -*- coding: utf-8 -*-
"""
BRICK BREAKER ULTIMATE EDITION
==============================
Modifikasi besar dari game Brick Breaker bawaan (tkinter).

Konsep PM yang dipakai:
  - Inheritance   : Ball, Paddle, Brick, PowerUp, Particle -> turunan GameObject
  - Polymorphism  : delete()/move() di-override oleh kelas turunan
  - Encapsulation : tiap objek mengurus posisi, gambar, dan perilakunya sendiri
  - Composition   : Game "memiliki" paddle, bola, brick, power-up, partikel

Setiap fitur diberi tanda  [FITUR #n]  di komentar dan dijelaskan juga di README.md
"""

import json
import math
import os
import random
import threading
import time
import tkinter as tk

try:                       # [FITUR #18] Efek suara (hanya jalan di Windows)
    import winsound
except ImportError:        # Di Linux/Mac game tetap jalan tanpa suara
    winsound = None

# ----------------------------------------------------------------------------
# KONSTANTA GLOBAL (mudah diubah untuk balancing game)
# ----------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600          # Ukuran jendela game (bawaan: 610 x 400)
FRAME_MS = 16                     # ~60 FPS (bawaan: 50 ms = 20 FPS, patah-patah)
TOP_WALL = 44                     # Batas atas area main (di bawah bar HUD)
PADDLE_Y = HEIGHT - 50            # Posisi vertikal paddle
PADDLE_SPEED = 10                 # Kecepatan paddle via keyboard (px/frame)
MAX_BALL_SPEED = 11               # Batas kecepatan bola
MAX_BALLS = 12                    # Batas jumlah bola saat Multi-Ball
EFFECT_FRAMES = 600               # Durasi power-up (600 frame = ~10 detik)
DROP_CHANCE = 0.18                # Peluang brick menjatuhkan power-up
TRAIL_LEN = 6                     # Panjang jejak bola

BRICK_W, BRICK_H, BRICK_GAP = 70, 22, 4
BRICK_COLS = 10
BRICK_LEFT = (WIDTH - (BRICK_COLS * (BRICK_W + BRICK_GAP) - BRICK_GAP)) / 2
BRICK_TOP = 80

BG_TOP, BG_BOTTOM = '#080a28', '#2a1050'     # Warna gradasi latar
TRAIL_BG = '#1a1040'                          # Warna akhir jejak (menyatu dg latar)
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'highscore.json')

# [FITUR #6] Tipe brick: karakter pada pola level -> properti brick
#   hits  : jumlah pukulan untuk hancur (-1 = tidak bisa dihancurkan)
#   points: skor dasar
BRICK_TYPES = {
    '1': {'hits': 1, 'points': 10},                       # Merah (1x pukul)
    '2': {'hits': 2, 'points': 20},                       # Biru  (2x pukul)
    '3': {'hits': 3, 'points': 30},                       # Ungu  (3x pukul)
    '#': {'hits': -1, 'points': 0},                       # Baja  (kebal)
    'E': {'hits': 1, 'points': 40, 'explosive': True},    # Brick peledak
}
BRICK_COLORS = {1: '#e74c3c', 2: '#3498db', 3: '#8e44ad'}
STEEL_COLOR, EXPLOSIVE_COLOR = '#7f8c8d', '#e67e22'

# [FITUR #7] Daftar power-up: kode -> (label, warna, nama)
POWERUPS = {
    'W': ('W', '#2ecc71', 'Paddle Lebar'),
    'M': ('M', '#f1c40f', 'Multi-Ball'),
    'S': ('S', '#3498db', 'Bola Lambat'),
    'F': ('F', '#e67e22', 'Fireball'),
    'L': ('+', '#e74c3c', 'Nyawa +1'),
    'N': ('N', '#8e44ad', 'Paddle Sempit (buruk!)'),
}
POWERUP_WEIGHTS = {'W': 25, 'M': 20, 'S': 18, 'F': 12, 'L': 6, 'N': 19}

# [FITUR #5] Lima level dengan pola berbeda. '.' = kosong. Tiap baris 10 karakter.
LEVELS = [
    ['1111111111',
     '1111111111',
     '2222222222',
     '1111111111'],

    ['2121212121',
     '1212121212',
     '2121212121',
     '1212121212'],

    ['#.1.11.1.#',
     '.2.2222.2.',
     'E33333333E',
     '.1.1111.1.'],

    ['1E1E1E1E1E',
     '2#2#2#2#2#',
     '3333333333',
     '#.#.#.#.#.',
     '1111111111'],

    ['3E222222E3',
     '#31111113#',
     '.22222222.',
     'E1E1E1E1E1',
     '3333333333'],
]

# [FITUR #18] Frekuensi (Hz) dan durasi (ms) tiap efek suara
SOUNDS = {'wall': (300, 25), 'paddle': (440, 35), 'brick': (660, 35),
          'steel': (200, 50), 'power': (880, 90), 'explode': (120, 150),
          'lose': (150, 300), 'win': (1000, 250)}


# ----------------------------------------------------------------------------
# FUNGSI BANTU
# ----------------------------------------------------------------------------
def clamp(value, low, high):
    """Membatasi nilai agar tetap di antara low dan high."""
    return max(low, min(high, value))


def hex_to_rgb(color):
    color = color.lstrip('#')
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, t):
    """Campuran dua warna hex. t=0 -> c1, t=1 -> c2 (dipakai utk gradasi/jejak)."""
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    mixed = [int(clamp(a[i] + (b[i] - a[i]) * t, 0, 255)) for i in range(3)]
    return '#%02x%02x%02x' % tuple(mixed)


# ----------------------------------------------------------------------------
# [FITUR #18] EFEK SUARA
# ----------------------------------------------------------------------------
class Sound:
    """Pemutar efek suara sederhana. Dijalankan di thread agar game tidak macet."""

    def __init__(self):
        self.enabled = True          # Bisa di-toggle dengan tombol M

    def play(self, name):
        if not self.enabled or winsound is None:
            return
        freq, dur = SOUNDS[name]
        threading.Thread(target=self._beep, args=(freq, dur),
                         daemon=True).start()

    @staticmethod
    def _beep(freq, dur):
        try:
            winsound.Beep(freq, dur)
        except RuntimeError:
            pass


# ----------------------------------------------------------------------------
# KELAS DASAR
# ----------------------------------------------------------------------------
class GameObject(object):
    """Kelas induk semua objek di canvas (dipertahankan dari kode asli)."""

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


# ----------------------------------------------------------------------------
# BOLA
# ----------------------------------------------------------------------------
class Ball(GameObject):
    """
    [FITUR #2]  Fisika bola baru: posisi float + vektor arah (dx, dy) + speed.
    [FITUR #12] Jejak (trail) berwarna memudar di belakang bola.
    [FITUR #13] Mode Fireball (bola api menembus brick).
    """

    def __init__(self, canvas, x, y, speed):
        self.radius = 8
        self.x, self.y = x, y            # Posisi pusat (float, lebih halus)
        self.speed = speed
        self.dx, self.dy = 0.0, -1.0     # Arah (vektor satuan)
        self.stuck = True                # Menempel di paddle sebelum diluncurkan
        self.offset = 0                  # Jarak bola dari tengah paddle
        self.fire = False
        self.history = []                # Riwayat posisi untuk jejak
        # Jejak dibuat DULU supaya tampil di belakang bola (urutan z-order)
        self.trail = [canvas.create_oval(0, 0, 0, 0, fill='', outline='')
                      for _ in range(TRAIL_LEN)]
        item = canvas.create_oval(0, 0, 0, 0, fill='white',
                                  outline='#9fd8ff', width=2)
        super(Ball, self).__init__(canvas, item)
        self.render()

    def set_angle(self, degrees):
        """Atur arah bola (0 derajat = lurus ke atas, + = condong ke kanan)."""
        rad = math.radians(degrees)
        self.dx, self.dy = math.sin(rad), -math.cos(rad)

    def rotate(self, degrees):
        """Putar vektor arah (dipakai Multi-Ball untuk menyebar bola)."""
        rad = math.radians(degrees)
        c, s = math.cos(rad), math.sin(rad)
        self.dx, self.dy = self.dx * c - self.dy * s, self.dx * s + self.dy * c

    def set_fire(self, flag):
        """Ganti tampilan bola antara normal dan Fireball."""
        if flag != self.fire:
            self.fire = flag
            self.canvas.itemconfig(self.item,
                                   fill='#ffb347' if flag else 'white',
                                   outline='#ff4500' if flag else '#9fd8ff')

    def render(self):
        """Gambar ulang bola + jejaknya sesuai posisi terbaru."""
        r = self.radius
        self.canvas.coords(self.item, self.x - r, self.y - r,
                           self.x + r, self.y + r)
        self.history.append((self.x, self.y))
        if len(self.history) > TRAIL_LEN + 1:
            self.history.pop(0)
        head = '#ff8c1a' if self.fire else '#bfe9ff'
        last = len(self.history) - 1
        for i, trail_item in enumerate(self.trail):
            idx = last - 1 - i
            if idx < 0:
                self.canvas.coords(trail_item, 0, 0, 0, 0)
                continue
            hx, hy = self.history[idx]
            rr = r * (1 - (i + 1) / (TRAIL_LEN + 2.0))     # Makin kecil
            self.canvas.coords(trail_item, hx - rr, hy - rr, hx + rr, hy + rr)
            self.canvas.itemconfig(
                trail_item, fill=lerp_color(head, TRAIL_BG, (i + 1.0) / (TRAIL_LEN + 1)))

    def delete(self):                    # Polymorphism: hapus bola + jejaknya
        for t in self.trail:
            self.canvas.delete(t)
        super(Ball, self).delete()


# ----------------------------------------------------------------------------
# PADDLE
# ----------------------------------------------------------------------------
class Paddle(GameObject):
    """
    [FITUR #3] Paddle dengan gerak mulus (keyboard + mouse) & lebar dinamis
               (berubah karena power-up Lebar / Sempit).
    """
    BASE_WIDTH = 100

    def __init__(self, canvas, x, y):
        self.width = Paddle.BASE_WIDTH
        self.height = 14
        self.x, self.y = x, y            # Pusat paddle
        item = canvas.create_rectangle(0, 0, 0, 0, fill='#f1c40f',
                                       outline='#fff3b0', width=2)
        self.shine = canvas.create_rectangle(0, 0, 0, 0, fill='#fff3b0',
                                             outline='')   # Kilap di atas paddle
        super(Paddle, self).__init__(canvas, item)
        self.render()

    @property
    def rect(self):
        w, h = self.width / 2, self.height / 2
        return self.x - w, self.y - h, self.x + w, self.y + h

    def render(self):
        x1, y1, x2, y2 = self.rect
        self.canvas.coords(self.item, x1, y1, x2, y2)
        self.canvas.coords(self.shine, x1 + 6, y1 + 2, x2 - 6, y1 + 5)

    def move_to(self, x):
        """Pindahkan pusat paddle ke x (tidak boleh keluar layar)."""
        self.x = clamp(x, self.width / 2, WIDTH - self.width / 2)
        self.render()

    def move_by(self, dx):
        self.move_to(self.x + dx)

    def set_width(self, width):
        self.width = width
        self.move_to(self.x)             # Pastikan tetap di dalam layar

    def delete(self):
        self.canvas.delete(self.shine)
        super(Paddle, self).delete()


# ----------------------------------------------------------------------------
# BRICK
# ----------------------------------------------------------------------------
class Brick(GameObject):
    """
    [FITUR #6] Beberapa tipe brick: 1/2/3 pukulan, baja (kebal), peledak.
    Brick bertingkat berubah warna saat terkena pukulan.
    """

    def __init__(self, canvas, x, y, kind):
        cfg = BRICK_TYPES[kind]
        self.kind = kind
        self.hits = cfg['hits']
        self.points = cfg['points']
        self.explosive = cfg.get('explosive', False)
        self.unbreakable = self.hits < 0
        self.cx, self.cy = x, y
        self.rect = (x - BRICK_W / 2, y - BRICK_H / 2,
                     x + BRICK_W / 2, y + BRICK_H / 2)
        x1, y1, x2, y2 = self.rect
        color = self.current_color()
        self.base_color = color          # Warna awal (untuk warna serpihan)
        item = canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                       outline=lerp_color(color, '#000000', 0.4),
                                       width=2)
        # Garis kilap tipis di bagian atas -> efek 3D
        self.shine = canvas.create_rectangle(x1 + 3, y1 + 3, x2 - 3, y1 + 6,
                                             fill=lerp_color(color, '#ffffff', 0.45),
                                             outline='')
        self.label = None
        if self.explosive:               # Tanda seru pada brick peledak
            self.label = canvas.create_text(x, y, text='!', fill='white',
                                            font=('Arial', 12, 'bold'))
        super(Brick, self).__init__(canvas, item)

    def current_color(self):
        if self.unbreakable:
            return STEEL_COLOR
        if self.explosive:
            return EXPLOSIVE_COLOR
        return BRICK_COLORS[self.hits]

    def hit(self, damage=1):
        """Kurangi nyawa brick. Return True bila brick hancur."""
        if self.unbreakable:
            return False
        self.hits -= damage
        if self.hits <= 0:
            return True
        color = self.current_color()      # Ganti warna sesuai sisa pukulan
        self.canvas.itemconfig(self.item, fill=color,
                               outline=lerp_color(color, '#000000', 0.4))
        self.canvas.itemconfig(self.shine, fill=lerp_color(color, '#ffffff', 0.45))
        return False

    def delete(self):                    # Polymorphism: hapus semua bagian brick
        self.canvas.delete(self.shine)
        if self.label:
            self.canvas.delete(self.label)
        super(Brick, self).delete()


# ----------------------------------------------------------------------------
# POWER-UP
# ----------------------------------------------------------------------------
class PowerUp(GameObject):
    """[FITUR #7] Kapsul yang jatuh dari brick; tangkap dengan paddle."""
    W, H = 40, 18

    def __init__(self, canvas, x, y, kind):
        label, color, _ = POWERUPS[kind]
        self.kind = kind
        self.x, self.y = x, y
        item = canvas.create_rectangle(x - self.W / 2, y - self.H / 2,
                                       x + self.W / 2, y + self.H / 2,
                                       fill=color, outline='white', width=2)
        self.text = canvas.create_text(x, y, text=label, fill='white',
                                       font=('Arial', 10, 'bold'))
        super(PowerUp, self).__init__(canvas, item)

    @property
    def rect(self):
        return (self.x - self.W / 2, self.y - self.H / 2,
                self.x + self.W / 2, self.y + self.H / 2)

    def update(self, dt):
        self.move(0, 3 * dt)

    def move(self, x, y):                # Polymorphism: gerakkan kapsul + hurufnya
        self.x += x
        self.y += y
        self.canvas.move(self.item, x, y)
        self.canvas.move(self.text, x, y)

    def delete(self):
        self.canvas.delete(self.text)
        super(PowerUp, self).delete()


# ----------------------------------------------------------------------------
# PARTIKEL
# ----------------------------------------------------------------------------
class Particle(GameObject):
    """[FITUR #11] Serpihan kecil saat brick hancur (efek ledakan)."""

    def __init__(self, canvas, x, y, color):
        size = random.uniform(2, 5)
        item = canvas.create_rectangle(x - size, y - size, x + size, y + size,
                                       fill=color, outline='')
        super(Particle, self).__init__(canvas, item)
        self.vx = random.uniform(-3.5, 3.5)
        self.vy = random.uniform(-4.5, 1.0)
        self.life = random.randint(25, 45)

    def update(self, dt):
        """Gerak + gravitasi. Return False bila umur partikel habis."""
        self.vy += 0.22 * dt
        self.move(self.vx * dt, self.vy * dt)
        self.life -= dt
        return self.life > 0


# ----------------------------------------------------------------------------
# GAME UTAMA
# ----------------------------------------------------------------------------
class Game(tk.Frame):
    """
    Mengatur seluruh alur game dengan state machine [FITUR #14]:
      menu -> ready -> playing -> (levelclear -> ready ...) -> gameover / win
      paused dapat disisipkan kapan saja saat ready/playing.
    """

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.master = master
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT,
                                bg=BG_TOP, highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.sound = Sound()
        self.high_score = self.load_high_score()     # [FITUR #9]
        self.keys = set()                            # Tombol yang sedang ditekan
        self.state = 'menu'
        self.prev_state = 'ready'

        self.score = 0
        self.lives = 3
        self.level_index = 0
        self.combo = 0
        self.effects = {}                # nama efek -> sisa frame
        self.bricks, self.balls, self.powerups, self.particles = [], [], [], []
        self.paddle = None

        self.draw_background()           # [FITUR #10]
        self.create_stars()              # [FITUR #10]
        self.create_hud()                # [FITUR #8]
        self.bind_inputs()               # [FITUR #3 & #14]
        self.show_menu()

        self.last_time = time.perf_counter()
        self.game_loop()

    # ------------------------------------------------------------------ setup
    def draw_background(self):
        """[FITUR #10] Latar gradasi (ungu tua -> biru gelap) dari 60 strip."""
        strips = 60
        h = HEIGHT / float(strips)
        for i in range(strips):
            color = lerp_color(BG_TOP, BG_BOTTOM, i / float(strips - 1))
            self.canvas.create_rectangle(0, i * h, WIDTH, (i + 1) * h + 1,
                                         fill=color, outline='')

    def create_stars(self):
        """[FITUR #10] Bintang parallax: yang kecil lambat, yang besar lebih cepat."""
        self.stars = []
        for _ in range(45):
            size = random.choice([1, 1, 2, 2, 3])
            x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
            shade = lerp_color('#555577', '#ffffff', size / 3.0)
            item = self.canvas.create_oval(x, y, x + size, y + size,
                                           fill=shade, outline='')
            self.stars.append({'item': item, 'x': x, 'y': y, 'size': size,
                               'speed': 0.15 * size})

    def create_hud(self):
        """[FITUR #8] HUD: skor, rekor, level, nyawa, combo, dan efek aktif."""
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, TOP_WALL, fill='#0a0a23',
                           outline='#4b4b9f', width=2)
        f = ('Arial', 13, 'bold')
        self.hud_score = c.create_text(15, 14, anchor='w', fill='white', font=f)
        self.hud_high = c.create_text(15, 32, anchor='w', fill='#aaaadd',
                                      font=('Arial', 9))
        self.hud_level = c.create_text(WIDTH / 2, TOP_WALL / 2, fill='#f1c40f', font=f)
        self.hud_lives = c.create_text(WIDTH - 15, TOP_WALL / 2, anchor='e',
                                       fill='#ff6b81', font=f)
        self.hud_effects = c.create_text(12, HEIGHT - 12, anchor='w',
                                         fill='#7fffd4', font=('Arial', 10, 'bold'))
        self.hud_combo = c.create_text(WIDTH - 12, HEIGHT - 12, anchor='e',
                                       fill='#ffd166', font=('Arial', 12, 'bold'))

    def bind_inputs(self):
        """[FITUR #3] Keyboard (panah / A-D) dan mouse; [FITUR #14] kontrol game."""
        root = self.master
        root.bind('<KeyPress>', self.on_key_press)
        root.bind('<KeyRelease>', lambda e: self.keys.discard(e.keysym.lower()))
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', lambda e: self.on_action())
        root.protocol('WM_DELETE_WINDOW', self.on_close)

    # ------------------------------------------------------------------ input
    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == 'space':
            self.on_action()
        elif key == 'p':
            self.toggle_pause()
        elif key == 'r':
            self.start_new_game()
        elif key == 'm':                 # [FITUR #18] Mute / unmute
            self.sound.enabled = not self.sound.enabled
        elif key == 'escape':
            self.go_to_menu()

    def on_mouse_move(self, event):
        if self.state in ('ready', 'playing') and self.paddle:
            self.paddle.move_to(event.x)

    def on_action(self):
        """Tombol SPASI / klik kiri: aksinya tergantung state saat ini."""
        if self.state in ('menu', 'gameover', 'win'):
            self.start_new_game()
        elif self.state == 'ready':
            self.launch_ball()
        elif self.state == 'levelclear':
            self.level_index += 1
            self.load_level()
        elif self.state == 'paused':
            self.toggle_pause()

    def on_close(self):
        self.save_high_score()
        self.master.destroy()

    # ------------------------------------------------------- high score [#9]
    def load_high_score(self):
        """[FITUR #9] Baca rekor dari file JSON (jika ada)."""
        try:
            with open(SAVE_FILE, 'r') as f:
                return int(json.load(f).get('high_score', 0))
        except (OSError, ValueError, AttributeError):
            return 0

    def save_high_score(self):
        """[FITUR #9] Simpan rekor ke file agar tidak hilang saat game ditutup."""
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except OSError:
            pass

    # --------------------------------------------------------- overlay teks
    def clear_overlay(self):
        self.canvas.delete('overlay')

    def show_overlay(self, title, lines, color='#f1c40f'):
        """Panel pesan di tengah layar (menu, pause, game over, dll)."""
        self.clear_overlay()
        cx, cy = WIDTH / 2, HEIGHT / 2 + 30
        height = 90 + 26 * len(lines)
        self.canvas.create_rectangle(cx - 300, cy - height / 2, cx + 300,
                                     cy + height / 2, fill='#10143a',
                                     outline=color, width=3, tags='overlay')
        self.canvas.create_text(cx, cy - height / 2 + 40, text=title, fill=color,
                                font=('Arial', 32, 'bold'), tags='overlay')
        for i, line in enumerate(lines):
            self.canvas.create_text(cx, cy - height / 2 + 85 + 26 * i, text=line,
                                    fill='white', font=('Arial', 13),
                                    tags='overlay')

    def show_hint(self, text):
        """Teks petunjuk kecil di bawah brick (tanpa panel)."""
        self.clear_overlay()
        self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 110, text=text,
                                fill='white', font=('Arial', 16, 'bold'),
                                tags='overlay')

    def show_menu(self):
        self.state = 'menu'
        self.show_overlay('BRICK BREAKER', [
            'SPASI / Klik = Mulai & Luncurkan bola',
            'Panah / A-D / Mouse = Gerakkan paddle',
            'P = Pause    R = Restart    M = Suara    Esc = Menu',
            'Tangkap kapsul: W M S F + N',
            'Rekor tertinggi: %d' % self.high_score])

    def go_to_menu(self):
        self.clear_objects()
        self.show_menu()

    # --------------------------------------------------------- alur permainan
    def clear_objects(self):
        for group in (self.bricks, self.balls, self.powerups, self.particles):
            for obj in group:
                obj.delete()
            del group[:]

    def start_new_game(self):
        """Reset semua data lalu mulai dari level 1."""
        self.clear_objects()
        self.score, self.lives, self.level_index, self.combo = 0, 3, 0, 0
        if self.paddle is None:
            self.paddle = Paddle(self.canvas, WIDTH / 2, PADDLE_Y)
        self.load_level()

    def load_level(self):
        """[FITUR #5] Bangun brick dari pola LEVELS[level_index]."""
        for b in self.bricks:
            b.delete()
        del self.bricks[:]
        for r, row in enumerate(LEVELS[self.level_index]):
            for c, ch in enumerate(row):
                if ch == '.':
                    continue
                x = BRICK_LEFT + c * (BRICK_W + BRICK_GAP) + BRICK_W / 2
                y = BRICK_TOP + r * (BRICK_H + BRICK_GAP) + BRICK_H / 2
                self.bricks.append(Brick(self.canvas, x, y, ch))
        self.reset_round()

    def base_speed(self):
        """[FITUR #4] Kecepatan dasar bola naik tiap level (kesulitan progresif)."""
        return min(6.0 + 0.6 * self.level_index, 9.5)

    def reset_round(self):
        """Siapkan ronde baru: bola menempel di paddle, efek direset."""
        for group in (self.balls, self.powerups):
            for obj in group:
                obj.delete()
            del group[:]
        self.effects.clear()
        self.combo = 0
        self.paddle.set_width(Paddle.BASE_WIDTH)
        self.paddle.move_to(WIDTH / 2)
        self.balls.append(Ball(self.canvas, self.paddle.x,
                               PADDLE_Y - 20, self.base_speed()))
        self.state = 'ready'
        self.show_hint('LEVEL %d  -  Tekan SPASI untuk meluncurkan bola'
                       % (self.level_index + 1))

    def launch_ball(self):
        """Lepaskan bola dari paddle dengan sudut acak kecil."""
        for ball in self.balls:
            if ball.stuck:
                ball.stuck = False
                ball.set_angle(random.uniform(-20, 20))
        self.state = 'playing'
        self.clear_overlay()
        self.sound.play('paddle')

    def toggle_pause(self):
        """[FITUR #14] Pause / lanjut."""
        if self.state in ('ready', 'playing'):
            self.prev_state = self.state
            self.state = 'paused'
            self.show_overlay('PAUSE', ['Tekan P atau SPASI untuk lanjut'], '#3498db')
        elif self.state == 'paused':
            self.state = self.prev_state
            self.clear_overlay()
            if self.state == 'ready':
                self.show_hint('Tekan SPASI untuk meluncurkan bola')

    def lose_life(self):
        """Semua bola jatuh: kurangi nyawa, reset combo."""
        self.lives -= 1
        self.combo = 0
        self.sound.play('lose')
        if self.lives <= 0:
            self.finish('gameover')
        else:
            self.reset_round()

    def finish(self, result):
        """[FITUR #9] Akhir game (kalah / menang) + simpan rekor."""
        self.state = result
        for group in (self.balls, self.powerups):
            for obj in group:
                obj.delete()
            del group[:]
        new_record = self.score >= self.high_score and self.score > 0
        self.save_high_score()
        lines = ['Skor akhir: %d' % self.score,
                 'REKOR BARU!' if new_record else 'Rekor: %d' % self.high_score,
                 'Tekan SPASI untuk main lagi']
        if result == 'win':
            self.sound.play('win')
            self.show_overlay('KAMU MENANG!', lines, '#2ecc71')
        else:
            self.show_overlay('GAME OVER', lines, '#e74c3c')

    def check_level_clear(self):
        """Level selesai bila semua brick yang bisa hancur sudah habis."""
        if self.state != 'playing' and self.state != 'ready':
            return
        if not all(b.unbreakable for b in self.bricks):
            return
        bonus = self.lives * 100         # Bonus sisa nyawa
        self.add_score(bonus)
        for group in (self.balls, self.powerups):
            for obj in group:
                obj.delete()
            del group[:]
        if self.level_index + 1 >= len(LEVELS):
            self.finish('win')
        else:
            self.state = 'levelclear'
            self.sound.play('win')
            self.show_overlay('LEVEL %d SELESAI!' % (self.level_index + 1),
                              ['Bonus nyawa: +%d' % bonus,
                               'Tekan SPASI ke level berikutnya'], '#2ecc71')

    # ------------------------------------------------------------ loop utama
    def game_loop(self):
        """
        [FITUR #1] Game loop ~60 FPS berbasis delta-time: gerakan dikali dt
        sehingga kecepatan tetap konsisten walau komputer lambat/cepat.
        """
        now = time.perf_counter()
        dt = clamp((now - self.last_time) * 60.0, 0.1, 2.5)   # 1.0 = tepat 60 FPS
        self.last_time = now

        self.update_stars(dt)
        if self.state != 'paused':
            self.update_particles(dt)
        if self.state in ('ready', 'playing'):
            self.update_game(dt)
        self.update_hud()
        self.after(FRAME_MS, self.game_loop)

    def update_game(self, dt):
        self.update_paddle(dt)
        self.update_effects(dt)
        for ball in list(self.balls):
            if ball.stuck:               # Bola menempel & ikut paddle
                ball.x = self.paddle.x + ball.offset
                ball.y = self.paddle.rect[1] - ball.radius
                ball.render()
            elif not self.update_ball(ball, dt):
                self.balls.remove(ball)  # Bola jatuh ke bawah
                ball.delete()
        self.update_powerups(dt)
        self.check_level_clear()
        if self.state == 'playing' and not self.balls:
            self.lose_life()

    def update_paddle(self, dt):
        """[FITUR #3] Gerak paddle mulus berbasis status tombol (bukan key-repeat)."""
        left = 'left' in self.keys or 'a' in self.keys
        right = 'right' in self.keys or 'd' in self.keys
        direction = (1 if right else 0) - (1 if left else 0)
        if direction:
            self.paddle.move_by(direction * PADDLE_SPEED * dt)

    # ------------------------------------------------------------- bola/fisika
    def update_ball(self, ball, dt):
        """Gerakkan satu bola. Return False jika bola jatuh keluar layar."""
        speed = ball.speed * (0.65 if 'slow' in self.effects else 1.0)
        ball.x += ball.dx * speed * dt
        ball.y += ball.dy * speed * dt
        r = ball.radius

        # Pantulan dinding kiri/kanan/atas (posisi dikoreksi agar tak tembus)
        if ball.x - r <= 0:
            ball.x, ball.dx = r, abs(ball.dx)
            self.sound.play('wall')
        elif ball.x + r >= WIDTH:
            ball.x, ball.dx = WIDTH - r, -abs(ball.dx)
            self.sound.play('wall')
        if ball.y - r <= TOP_WALL:
            ball.y, ball.dy = TOP_WALL + r, abs(ball.dy)
            self.sound.play('wall')

        self.ball_paddle_collision(ball)
        self.ball_brick_collision(ball)
        ball.render()
        return ball.y - r <= HEIGHT

    def ball_paddle_collision(self, ball):
        """
        [FITUR #2] Sudut pantul bergantung pada BAGIAN paddle yang terkena:
        tengah = lurus ke atas, pinggir = miring tajam (maks 65 derajat).
        Pemain bisa mengarahkan bola -> game jauh lebih strategis.
        """
        if ball.dy <= 0:
            return
        x1, y1, x2, y2 = self.paddle.rect
        r = ball.radius
        if (x1 - r * 0.6 <= ball.x <= x2 + r * 0.6
                and ball.y + r >= y1 and ball.y <= y2):
            ball.y = y1 - r
            rel = clamp((ball.x - self.paddle.x) / (self.paddle.width / 2.0), -1, 1)
            ball.set_angle(rel * 65)
            ball.speed = min(ball.speed + 0.05, MAX_BALL_SPEED)   # Makin lama makin cepat
            self.combo = 0                                          # [FITUR #15] reset combo
            self.sound.play('paddle')

    