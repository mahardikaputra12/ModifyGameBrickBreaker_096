# -*- coding: utf-8 -*-
"""
BRICK BREAKER - EDISI MODIFIKASI (versi ringkas)
Konsep PBO: Inheritance (semua objek turunan GameObject), Polymorphism
(delete() di-override), Encapsulation (tiap kelas urus dirinya), Composition.
Tiap fitur ditandai [FITUR n] dan dijelaskan di README.md
"""
import json, math, os, random, time
import tkinter as tk

W, H, TOP = 800, 600, 44                      # Ukuran layar & batas atas area main
SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'highscore.json')
BW, BH, GAP = 70, 22, 4                       # Ukuran brick & jarak antar brick
LEFT = (W - (10 * (BW + GAP) - GAP)) / 2      # Posisi x brick pertama (rata tengah)
COLORS = {1: '#e74c3c', 2: '#3498db', 3: '#8e44ad'}   # Warna sesuai sisa pukulan
# [FITUR 4] Tipe brick: 1/2/3 = jumlah pukulan, # = baja (kebal), E = peledak
HITS = {'1': 1, '2': 2, '3': 3, '#': -1, 'E': 1}
# [FITUR 5] Power-up: W=paddle lebar, M=multi-ball, F=fireball, L=nyawa +1
POWER = {'W': '#2ecc71', 'M': '#f1c40f', 'F': '#e67e22', 'L': '#e74c3c'}
NAMES = {'wide': 'Paddle Lebar', 'fire': 'Fireball'}
# [FITUR 3] Empat level dengan pola berbeda ('.' = kosong, tiap baris 10 karakter)
LEVELS = [['1111111111', '1111111111', '2222222222', '1111111111'],
          ['2121212121', '1212121212', '2121212121', '1212121212'],
          ['#.1.11.1.#', '.2.2222.2.', 'E33333333E', '.1.1111.1.'],
          ['3E222222E3', '#31111113#', '.22222222.', 'E1E1E1E1E1']]


def mix(c1, c2, t):
    """Campur dua warna hex (dipakai untuk gradasi & efek kilap)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class GameObject(object):
    """Kelas induk semua objek di canvas."""
    def __init__(self, canvas, item):
        self.canvas, self.item = canvas, item

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    """[FITUR 2] Bola dengan posisi float + vektor arah (dx, dy) + kecepatan."""
    R = 8

    def __init__(self, canvas, x, y, speed):
        super(Ball, self).__init__(canvas, canvas.create_oval(0, 0, 0, 0, fill='white', outline='#9fd8ff', width=2))
        self.x, self.y, self.speed = x, y, speed
        self.dx, self.dy, self.stuck, self.fire = 0.0, -1.0, True, False
        self.render()

    def set_angle(self, deg):
        """0 derajat = lurus ke atas, positif = condong ke kanan."""
        self.dx, self.dy = math.sin(math.radians(deg)), -math.cos(math.radians(deg))

    def render(self):
        r = self.R
        self.canvas.coords(self.item, self.x - r, self.y - r, self.x + r, self.y + r)
        self.canvas.itemconfig(self.item, fill='#ffb347' if self.fire else 'white')   # [FITUR 6] api


class Paddle(GameObject):
    """[FITUR 5] Paddle dengan lebar dinamis (berubah oleh power-up W)."""
    BASE = 100

    def __init__(self, canvas):
        super(Paddle, self).__init__(canvas, canvas.create_rectangle(0, 0, 0, 0, fill='#f1c40f', outline='#fff3b0', width=2))
        self.x, self.y, self.w = W / 2, H - 50, self.BASE
        self.move_to(self.x)

    @property
    def rect(self):
        return self.x - self.w / 2, self.y - 7, self.x + self.w / 2, self.y + 7

    def move_to(self, x):
        self.x = clamp(x, self.w / 2, W - self.w / 2)      # Tidak boleh keluar layar
        self.canvas.coords(self.item, *self.rect)


class Brick(GameObject):
    """[FITUR 4] Brick bertingkat: berubah warna tiap kena, baja kebal, E meledak."""

    def __init__(self, canvas, x, y, kind):
        self.kind, self.hits = kind, HITS[kind]
        self.cx, self.cy = x, y
        self.rect = (x - BW / 2, y - BH / 2, x + BW / 2, y + BH / 2)
        super(Brick, self).__init__(canvas, canvas.create_rectangle(*self.rect, width=2))
        self.shine = canvas.create_rectangle(self.rect[0] + 3, self.rect[1] + 3,   # Kilap 3D
                                             self.rect[2] - 3, self.rect[1] + 6, outline='')
        self.paint()
        self.base = self.color()

    @property
    def steel(self):
        return self.kind == '#'

    def color(self):
        return '#7f8c8d' if self.steel else '#e67e22' if self.kind == 'E' else COLORS[self.hits]

    def paint(self):
        c = self.color()
        self.canvas.itemconfig(self.item, fill=c, outline=mix(c, '#000000', 0.4))
        self.canvas.itemconfig(self.shine, fill=mix(c, '#ffffff', 0.45))

    def hit(self, damage=1):
        """Kurangi pukulan. True jika brick hancur."""
        if self.steel:
            return False
        self.hits -= damage
        if self.hits > 0:
            self.paint()
        return self.hits <= 0

    def delete(self):                       # Polymorphism: hapus kilap juga
        self.canvas.delete(self.shine)
        super(Brick, self).delete()


class PowerUp(GameObject):
    """[FITUR 5] Kapsul yang jatuh dari brick; tangkap dengan paddle."""

    def __init__(self, canvas, x, y, kind):
        super(PowerUp, self).__init__(canvas, canvas.create_rectangle(x - 20, y - 9, x + 20, y + 9, fill=POWER[kind], outline='white', width=2))
        self.text = canvas.create_text(x, y, text=kind, fill='white', font=('Arial', 10, 'bold'))
        self.x, self.y, self.kind = x, y, kind

    def move(self, x, y):                   # Polymorphism: gerakkan kapsul + hurufnya
        self.x, self.y = self.x + x, self.y + y
        self.canvas.move(self.item, x, y)
        self.canvas.move(self.text, x, y)

    def delete(self):
        self.canvas.delete(self.text)
        super(PowerUp, self).delete()


class Particle(GameObject):
    """[FITUR 9] Serpihan kecil saat brick hancur, kena gravitasi lalu hilang."""

    def __init__(self, canvas, x, y, color):
        s = random.uniform(2, 5)
        super(Particle, self).__init__(canvas, canvas.create_rectangle(x - s, y - s, x + s, y + s, fill=color, outline=''))
        self.vx, self.vy, self.life = random.uniform(-3.5, 3.5), random.uniform(-4.5, 1), random.randint(25, 45)

    def update(self, dt):
        self.vy += 0.22 * dt
        self.move(self.vx * dt, self.vy * dt)
        self.life -= dt
        return self.life > 0


class Game(tk.Frame):
    """[FITUR 12] State machine: menu -> ready -> playing -> levelclear -> gameover/win (+ paused)."""

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.pack()
        self.canvas = tk.Canvas(self, width=W, height=H, bg='#080a28', highlightthickness=0)
        self.canvas.pack()
        self.high = self.load_high()
        self.keys, self.state, self.prev = set(), 'menu', 'ready'
        self.bricks, self.balls, self.powers, self.parts = [], [], [], []
        self.score = self.level = self.combo = 0
        self.lives, self.fx = 3, {}                        # fx = efek power-up aktif
        for i in range(60):                                # [FITUR 8] Latar gradasi
            self.canvas.create_rectangle(0, i * 10, W, i * 10 + 11, outline='',
                                         fill=mix('#080a28', '#2a1050', i / 59.0))
        self.canvas.create_rectangle(0, 0, W, TOP, fill='#0a0a23', outline='#4b4b9f', width=2)
        f = ('Arial', 13, 'bold')                          # [FITUR 10] HUD
        t = self.canvas.create_text
        self.h_score, self.h_level = t(15, 14, anchor='w', fill='white', font=f), t(W / 2, 22, fill='#f1c40f', font=f)
        self.h_high, self.h_lives = t(15, 32, anchor='w', fill='#aaaadd', font=('Arial', 9)), t(W - 15, 22, anchor='e', fill='#ff6b81', font=f)
        self.h_fx, self.h_combo = t(12, H - 12, anchor='w', fill='#7fffd4', font=f), t(W - 12, H - 12, anchor='e', fill='#ffd166', font=f)
        m = self.master                                    # [FITUR 11] Kontrol keyboard & mouse
        m.bind('<KeyPress>', self.on_key)
        m.bind('<KeyRelease>', lambda e: self.keys.discard(e.keysym.lower()))
        self.canvas.bind('<Motion>', lambda e: self.paddle.move_to(e.x) if self.state in ('ready', 'playing') else None)
        self.canvas.bind('<Button-1>', lambda e: self.action())
        m.protocol('WM_DELETE_WINDOW', self.close)
        self.paddle = Paddle(self.canvas)
        self.overlay('BRICK BREAKER', ['SPASI / Klik = Mulai & luncurkan bola', 'Panah / A-D / Mouse = Gerak paddle',
                                       'P = Pause    R = Restart', 'Rekor: %d' % self.high])
        self.last = time.perf_counter()
        self.loop()

    # ---------------------------------------------------------------- input
    def on_key(self, e):
        k = e.keysym.lower()
        self.keys.add(k)
        if k == 'space':
            self.action()
        elif k == 'p':
            self.pause()
        elif k == 'r':
            self.new_game()

    def action(self):
        """SPASI / klik: aksi tergantung state."""
        if self.state in ('menu', 'gameover', 'win'):
            self.new_game()
        elif self.state == 'ready':
            for b in self.balls:
                b.stuck = False
                b.set_angle(random.uniform(-20, 20))
            self.state = 'playing'
            self.canvas.delete('overlay')
        elif self.state == 'levelclear':
            self.level += 1
            self.load_level()
        elif self.state == 'paused':
            self.pause()

    def pause(self):
        """[FITUR 12] Pause / lanjut."""
        if self.state in ('ready', 'playing'):
            self.prev, self.state = self.state, 'paused'
            self.overlay('PAUSE', ['Tekan P atau SPASI untuk lanjut'], '#3498db')
        elif self.state == 'paused':
            self.state = self.prev
            self.canvas.delete('overlay')

    # ----------------------------------------------------- rekor & tampilan
    def load_high(self):
        """[FITUR 13] Baca rekor dari highscore.json."""
        try:
            return int(json.load(open(SAVE))['high_score'])
        except (OSError, ValueError, KeyError):
            return 0

    def close(self):
        try:
            json.dump({'high_score': self.high}, open(SAVE, 'w'))   # [FITUR 13] Simpan rekor
        except OSError:
            pass
        self.master.destroy()

    def overlay(self, title, lines, color='#f1c40f'):
        """Panel pesan di tengah layar (menu, pause, game over...)."""
        c, cx, cy, h = self.canvas, W / 2, H / 2 + 30, 90 + 26 * len(lines)
        c.delete('overlay')
        c.create_rectangle(cx - 300, cy - h / 2, cx + 300, cy + h / 2, fill='#10143a', outline=color, width=3, tags='overlay')
        c.create_text(cx, cy - h / 2 + 40, text=title, fill=color, font=('Arial', 32, 'bold'), tags='overlay')
        for i, s in enumerate(lines):
            c.create_text(cx, cy - h / 2 + 85 + 26 * i, text=s, fill='white', font=('Arial', 13), tags='overlay')

    # --------------------------------------------------------- alur game
    def clear(self, *groups):
        for g in groups:
            for o in g:
                o.delete()
            del g[:]

    def new_game(self):
        self.clear(self.bricks, self.balls, self.powers, self.parts)
        self.score, self.lives, self.level = 0, 3, 0
        self.load_level()

    def load_level(self):
        """[FITUR 3] Bangun brick dari pola teks LEVELS."""
        self.clear(self.bricks, self.balls, self.powers)
        for r, row in enumerate(LEVELS[self.level]):
            for c, ch in enumerate(row):
                if ch != '.':
                    self.bricks.append(Brick(self.canvas, LEFT + c * (BW + GAP) + BW / 2, 80 + r * (BH + GAP) + BH / 2, ch))
        self.reset_round()

    def reset_round(self):
        """Bola baru menempel di paddle; efek & combo direset."""
        self.clear(self.balls, self.powers)
        self.fx.clear()
        self.combo, self.paddle.w = 0, Paddle.BASE
        self.paddle.move_to(W / 2)
        # [FITUR 1] Kecepatan awal bola naik tiap level (kesulitan progresif)
        self.balls.append(Ball(self.canvas, self.paddle.x, self.paddle.y - 20, 6.0 + 0.7 * self.level))
        self.state = 'ready'
        self.overlay('LEVEL %d' % (self.level + 1), ['Tekan SPASI untuk meluncurkan bola'], '#3498db')

    def finish(self, result):
        self.clear(self.balls, self.powers)
        self.state = result
        try:
            json.dump({'high_score': self.high}, open(SAVE, 'w'))
        except OSError:
            pass
        lines = ['Skor akhir: %d' % self.score, 'Rekor: %d' % self.high, 'Tekan SPASI untuk main lagi']
        self.overlay('KAMU MENANG!' if result == 'win' else 'GAME OVER', lines, '#2ecc71' if result == 'win' else '#e74c3c')

    # ------------------------------------------------------------ loop utama
    def loop(self):
        """[FITUR 1] Game loop ~60 FPS berbasis delta-time (kecepatan konsisten di PC lambat/cepat)."""
        now = time.perf_counter()
        dt = clamp((now - self.last) * 60.0, 0.1, 2.5)
        self.last = now
        if self.state != 'paused':
            for p in list(self.parts):
                if not p.update(dt):
                    p.delete()
                    self.parts.remove(p)
        if self.state in ('ready', 'playing'):
            self.update(dt)
        self.update_hud()
        self.after(16, self.loop)

    def update(self, dt):
        # Gerak paddle mulus dari status tombol
        d = ('right' in self.keys or 'd' in self.keys) - ('left' in self.keys or 'a' in self.keys)
        if d:
            self.paddle.move_to(self.paddle.x + d * 10 * dt)
        for k in list(self.fx):                            # Hitung mundur efek power-up
            self.fx[k] -= dt
            if self.fx[k] <= 0:
                del self.fx[k]
                if k == 'wide':
                    self.paddle.w = Paddle.BASE
                    self.paddle.move_to(self.paddle.x)
        for b in list(self.balls):
            b.fire = 'fire' in self.fx
            if b.stuck:                                    # Bola ikut paddle sebelum diluncurkan
                b.x, b.y = self.paddle.x, self.paddle.rect[1] - b.R
            elif not self.update_ball(b, dt):
                self.balls.remove(b)
                b.delete()
                continue
            b.render()
        self.update_powers(dt)
        if all(b.steel for b in self.bricks):              # Level selesai (baja boleh sisa)
            self.level_clear()
        elif self.state == 'playing' and not self.balls:   # Semua bola jatuh
            self.lives, self.combo = self.lives - 1, 0
            self.finish('gameover') if self.lives <= 0 else self.reset_round()

    def level_clear(self):
        self.add_score(self.lives * 100)                   # Bonus sisa nyawa
        if self.level + 1 >= len(LEVELS):
            self.finish('win')
        else:
            self.clear(self.balls, self.powers)
            self.state = 'levelclear'
            self.overlay('LEVEL SELESAI!', ['Bonus nyawa: +%d' % (self.lives * 100), 'Tekan SPASI untuk lanjut'], '#2ecc71')

    # --------------------------------------------------------------- fisika
    def update_ball(self, b, dt):
        """Gerakkan bola, pantulkan di dinding/paddle/brick. False jika jatuh."""
        b.x += b.dx * b.speed * dt
        b.y += b.dy * b.speed * dt
        r = b.R
        if b.x - r <= 0 or b.x + r >= W:                   # Dinding kiri/kanan
            b.dx = abs(b.dx) if b.x - r <= 0 else -abs(b.dx)
            b.x = clamp(b.x, r, W - r)
        if b.y - r <= TOP:                                 # Dinding atas
            b.y, b.dy = TOP + r, abs(b.dy)
        x1, y1, x2, y2 = self.paddle.rect
        if b.dy > 0 and x1 - r / 2 <= b.x <= x2 + r / 2 and y1 <= b.y + r and b.y <= y2:
            # [FITUR 2] Sudut pantul bergantung bagian paddle: tengah = lurus, pinggir = miring (maks 65 derajat)
            b.y = y1 - r
            b.set_angle(clamp((b.x - self.paddle.x) / (self.paddle.w / 2.0), -1, 1) * 65)
            b.speed = min(b.speed + 0.05, 11)              # Makin lama makin cepat
            self.combo = 0                                 # Combo putus saat kena paddle
        for k in self.bricks:                              # Tabrakan lingkaran vs persegi
            nx, ny = clamp(b.x, k.rect[0], k.rect[2]), clamp(b.y, k.rect[1], k.rect[3])
            dx, dy = b.x - nx, b.y - ny
            if dx * dx + dy * dy > r * r:
                continue
            if k.hit(k.hits if b.fire else 1):
                self.destroy(k)
            elif not k.steel:
                self.combo += 1
                self.add_score(5)
            if b.fire and not k.steel:                     # [FITUR 6] Fireball menembus brick
                break
            if dx == 0 and dy == 0:
                b.dy = -b.dy
            elif abs(dx) > abs(dy):                        # Pantul horizontal (kena sisi samping)
                s = 1 if dx > 0 else -1
                b.dx, b.x = abs(b.dx) * s, nx + s * (r + 0.1)
            else:                                          # Pantul vertikal (kena atas/bawah)
                s = 1 if dy > 0 else -1
                b.dy, b.y = abs(b.dy) * s, ny + s * (r + 0.1)
            break                                          # Satu brick per frame
        return b.y - r <= H

    def add_score(self, n):
        self.score += n
        self.high = max(self.high, self.score)

    def destroy(self, k):
        """
        [FITUR 7] Combo: hancurkan brick beruntun tanpa kena paddle -> pengali skor (x2 tiap 5 combo, maks x5).
        [FITUR 9] Partikel, [FITUR 5] peluang drop power-up, [FITUR 14] brick E meledak berantai.
        """
        if k not in self.bricks:
            return
        self.bricks.remove(k)
        self.combo += 1
        self.add_score({'1': 10, '2': 20, '3': 30, 'E': 40}[k.kind] * (1 + min(self.combo, 20) // 5))
        for _ in range(16 if k.kind == 'E' else 8):
            self.parts.append(Particle(self.canvas, k.cx, k.cy, k.base))
        k.delete()
        if random.random() < 0.18:
            self.powers.append(PowerUp(self.canvas, k.cx, k.cy, random.choice('WWMMFL')))
        if k.kind == 'E':                                  # Ledakan: brick radius 100px ikut hancur
            for o in list(self.bricks):
                if not o.steel and math.hypot(o.cx - k.cx, o.cy - k.cy) <= 100:
                    self.destroy(o)

    # ------------------------------------------------------------- power-up
    def update_powers(self, dt):
        x1, y1, x2, y2 = self.paddle.rect
        for p in list(self.powers):
            p.move(0, 3 * dt)
            if p.x + 20 >= x1 and p.x - 20 <= x2 and p.y + 9 >= y1 and p.y - 9 <= y2:
                self.apply(p.kind)
                self.powers.remove(p)
                p.delete()
            elif p.y > H + 20:
                self.powers.remove(p)
                p.delete()

    def apply(self, kind):
        self.add_score(25)
        if kind == 'L':                                    # Nyawa +1 (maks 5)
            self.lives = min(self.lives + 1, 5)
        elif kind == 'W':                                  # Paddle lebar 10 detik
            self.fx['wide'], self.paddle.w = 600, Paddle.BASE * 1.6
            self.paddle.move_to(self.paddle.x)
        elif kind == 'F':                                  # Fireball 10 detik
            self.fx['fire'] = 600
        elif kind == 'M':                                  # [FITUR 6] Multi-Ball: tiap bola jadi 3
            for b in [b for b in self.balls if not b.stuck][:4]:
                for a in (-25, 25):
                    n = Ball(self.canvas, b.x, b.y, b.speed)
                    n.stuck = False
                    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
                    n.dx, n.dy = b.dx * c - b.dy * s, b.dx * s + b.dy * c
                    self.balls.append(n)

    def update_hud(self):
        """[FITUR 10] Perbarui HUD tiap frame."""
        c = self.canvas.itemconfig
        c(self.h_score, text='SKOR: %d' % self.score)
        c(self.h_high, text='REKOR: %d' % self.high)
        c(self.h_level, text='LEVEL %d / %d' % (self.level + 1, len(LEVELS)))
        c(self.h_lives, text='NYAWA: ' + '\u2665 ' * self.lives)
        c(self.h_fx, text='   '.join('%s %ds' % (NAMES[k], v / 60 + 1) for k, v in self.fx.items()))
        c(self.h_combo, text='COMBO %d  x%d' % (self.combo, 1 + min(self.combo, 20) // 5) if self.combo > 1 else '')
        self.canvas.tag_raise('overlay')


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker - Edisi Modifikasi')
    root.resizable(False, False)
    Game(root).mainloop()