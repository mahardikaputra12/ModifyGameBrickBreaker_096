# 🧱 Brick Breaker — Edisi Modifikasi

Modifikasi game **Brick Breaker** bawaan (Python + Tkinter) dengan prinsip **PM** dan 14 fitur baru.

> **Nama / NIM:** `[Mahardika Putra Qohar / 20250140096]`

## ▶️ Cara Menjalankan

```bash
python brick_breaker.py
```

Butuh Python 3.6+ dengan Tkinter (Linux: `sudo apt install python3-tk`). Tidak perlu library tambahan.

## 🎮 Kontrol

| Tombol                    | Fungsi                              |
| ------------------------- | ----------------------------------- |
| `←` `→` / `A` `D` / Mouse | Gerakkan paddle                     |
| `SPASI` / Klik kiri       | Mulai, luncurkan bola, lanjut level |
| `P`                       | Pause / lanjut                      |
| `R`                       | Restart                             |

## 🔍 Perbandingan dengan Versi Bawaan

| Aspek                                      | Bawaan               | Modifikasi                          |
| ------------------------------------------ | -------------------- | ----------------------------------- |
| Layar                                      | 610 × 400            | 800 × 600                           |
| Frame                                      | 20 FPS               | ~60 FPS (delta-time)                |
| Level                                      | 1                    | 4 level, kecepatan naik tiap level  |
| Tipe brick                                 | 2                    | 5 (1x, 2x, 3x, baja kebal, peledak) |
| Pantulan paddle                            | Sama di semua bagian | Bergantung bagian paddle yang kena  |
| Power-up, combo, rekor, pause, efek visual | Tidak ada            | Ada                                 |

## 🔄 Apa yang Berubah dari Kode Awal

Bagian ini membandingkan kode awal dengan `breakout.py` per kelas. Keterangan: ✅ dipertahankan, ✏️ diubah, ❌ dihapus, ➕ ditambahkan.

### 1. Perbaikan error di kode awal

| Masalah di kode awal                                                                                  | Perbaikan                                             |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Tanda kutip ganda dua kali (`''white''`, `''#e74c3c''`, dst.) menyebabkan _SyntaxError_               | ✏️ Diganti kutip biasa (`'white'`) di seluruh kode    |
| Nyawa awal 3, tetapi game over baru saat `lives < 0` sehingga pemain sebenarnya punya **4** nyawa     | ✏️ Game over saat `lives <= 0` → tepat 3 nyawa        |
| Setelah menang/kalah, game tidak bisa dimulai ulang                                                   | ➕ Tekan `SPASI` untuk main lagi, atau `R` kapan saja |
| Pantulan memakai `find_overlapping` (kotak pembatas), sehingga bola bisa memantul aneh di sudut brick | ✏️ Diganti tabrakan lingkaran-vs-persegi              |

### 2. Perubahan per kelas

#### `GameObject` (kelas induk)

| Bagian                           | Status | Keterangan                                                                                                                   |
| -------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `__init__`, `move()`, `delete()` | ✅     | Tetap sama                                                                                                                   |
| `get_position()`                 | ❌     | Dihapus karena posisi sekarang disimpan sendiri sebagai atribut (`x`, `y`, `rect`), tidak perlu dibaca dari canvas tiap saat |

#### `Ball`

| Bagian                        | Kode awal                                             | Sekarang                                                                                                  |
| ----------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Ukuran & kecepatan            | `radius = 10`, `speed = 10` tetap                     | ✏️ `R = 8`; kecepatan awal `6.0 + 0.7 × level` dan naik tiap kena paddle (maks 11)                        |
| Arah                          | ✏️ `direction = [1, -1]` (hanya diagonal 45°)         | Vektor arah `dx, dy` yang bisa bersudut bebas, diatur lewat `set_angle()`                                 |
| Posisi                        | Dibaca dari `canvas.coords()`                         | ✏️ Disimpan sebagai `x, y` (float) lalu digambar lewat `render()`                                         |
| `update()` (pantulan dinding) | Ada di kelas `Ball`                                   | ✏️ Pindah ke `Game.update_ball()` karena harus tahu paddle, brick, dan `dt`                               |
| `collide()` (tabrakan)        | Membalik arah sesuai jumlah objek yang tumpang tindih | ❌ Diganti `Game.update_ball()` (tabrakan lingkaran-vs-persegi, sudut pantul bergantung posisi di paddle) |
| `set_angle()`, `render()`     | –                                                     | ➕ Baru                                                                                                   |
| `stuck`                       | –                                                     | ➕ Bola menempel di paddle sebelum diluncurkan                                                            |
| `fire`                        | –                                                     | ➕ Mode Fireball (warna bola berubah oranye)                                                              |

#### `Paddle`

| Bagian            | Kode awal                                           | Sekarang                                                                          |
| ----------------- | --------------------------------------------------- | --------------------------------------------------------------------------------- |
| Ukuran            | 80 × 10 tetap                                       | ✏️ Lebar `100` (`BASE`), bisa membesar 1.6× karena power-up W                     |
| `move(offset)`    | Menggeser paddle (dan bola jika `self.ball` terisi) | ❌ Diganti `move_to(x)` yang membatasi paddle agar tidak keluar layar             |
| `set_ball()`      | Menautkan bola ke paddle                            | ❌ Dihapus. Bola menempel lewat flag `stuck`, posisinya diatur di `Game.update()` |
| `rect` (properti) | –                                                   | ➕ Mengembalikan kotak paddle untuk tabrakan                                      |

#### `Brick`

| Bagian                                 | Kode awal                                 | Sekarang                                                                                                                  |
| -------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Tipe                                   | `hits` 1–3 (3 = hitam)                    | ✏️ Karakter `'1' '2' '3' '#' 'E'` → 3 tingkat + baja kebal + peledak. Warna 3-pukulan jadi ungu                           |
| `COLORS`                               | Kamus di dalam kelas                      | ✏️ Pindah jadi konstanta global; baja dan peledak punya warna khusus                                                      |
| `hit()`                                | Mengurangi `hits`, menghapus brick jika 0 | ✏️ `hit(damage)` hanya mengembalikan `True` jika hancur. Penghapusan, skor, partikel, dan ledakan diurus `Game.destroy()` |
| `shine`, `paint()`, `color()`, `steel` | –                                         | ➕ Kilap 3D di bagian atas brick dan pengatur warna                                                                       |
| `delete()`                             | Bawaan induk                              | ✏️ Di-override (polymorphism) agar kilap ikut terhapus                                                                    |

#### `Game`

| Bagian                               | Kode awal                                                | Sekarang                                                              |
| ------------------------------------ | -------------------------------------------------------- | --------------------------------------------------------------------- |
| Ukuran layar                         | 610 × 400                                                | ✏️ 800 × 600                                                          |
| Susunan brick                        | Tiga baris tetap (`add_brick` dalam loop)                | ✏️ Dibangun dari pola teks `LEVELS` lewat `load_level()` (4 level)    |
| `self.items` (kamus)                 | Menyimpan objek untuk `find_overlapping`                 | ❌ Diganti list `bricks`, `balls`, `powers`, `parts`                  |
| `setup_game()`, `add_ball()`         | Menyiapkan bola dan teks awal                            | ✏️ Digantikan `reset_round()`                                         |
| `add_brick()`                        | Membuat satu brick                                       | ✏️ Dilebur ke `load_level()`                                          |
| `draw_text()`, `update_lives_text()` | Teks nyawa dan pesan                                     | ✏️ Diganti `update_hud()` (HUD lengkap) dan `overlay()` (panel pesan) |
| `start_game()`                       | Memulai game setelah `SPASI`                             | ✏️ Diganti `action()` yang berubah sesuai state                       |
| `game_loop()`                        | `after(50)` = 20 FPS                                     | ✏️ `after(16)` ≈ 60 FPS dengan _delta-time_                           |
| `check_collisions()`                 | `find_overlapping`                                       | ❌ Dihapus, diganti tabrakan di `update_ball()`                       |
| Kontrol                              | `<Left>`/`<Right>` pada canvas (bergantung _key-repeat_) | ✏️ Berbasis status tombol (`self.keys`) + mouse + `A`/`D`             |
| Teks menang/kalah                    | Teks biasa `'You win!'`                                  | ✏️ Panel `overlay()` dengan skor, rekor, dan petunjuk main lagi       |

### 3. Kelas dan fungsi yang ditambahkan

| Nama                                                   | Fungsi                                                                           |
| ------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `PowerUp` (kelas)                                      | Kapsul yang jatuh dari brick; `move()` dan `delete()` di-override (polymorphism) |
| `Particle` (kelas)                                     | Serpihan saat brick hancur                                                       |
| `mix()`, `clamp()`                                     | Fungsi bantu: campur warna (gradasi) dan batasi nilai                            |
| `LEVELS`, `HITS`, `POWER`, `COLORS`                    | Konstanta data level, brick, dan power-up                                        |
| `Game.update()`, `update_ball()`, `update_powers()`    | Memperbarui paddle, bola, dan kapsul tiap frame                                  |
| `Game.destroy()`                                       | Brick hancur: skor, combo, partikel, drop power-up, ledakan berantai             |
| `Game.apply()`                                         | Efek tiap power-up (W, M, F, L)                                                  |
| `Game.level_clear()`, `finish()`                       | Level selesai dengan bonus nyawa, serta akhir game (menang/kalah)                |
| `Game.pause()`, `new_game()`, `load_high()`, `close()` | Pause, mulai ulang, baca dan simpan rekor                                        |

### 4. Baris `main`

| Kode awal                      | Sekarang                                                    |
| ------------------------------ | ----------------------------------------------------------- |
| `root.title('Hello, Jarvis!')` | ✏️ `'Brick Breaker - Edisi Modifikasi'`                     |
| –                              | ➕ `root.resizable(False, False)` agar ukuran jendela tetap |

## ✨ Daftar Fitur

Setiap fitur ditandai `[FITUR n]` di komentar `brick_breaker.py`.

| #   | Fitur                                  | Penjelasan                                                                                                                                            |
| --- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Game loop 60 FPS + kesulitan progresif | Gerakan dikali `dt` agar kecepatan konsisten di PC lambat/cepat. Kecepatan bola naik tiap level dan tiap kena paddle.                                 |
| 2   | Fisika bola                            | Posisi float + vektor arah. Tabrakan lingkaran-vs-persegi. Sudut pantul paddle bergantung titik tumbukan (tengah = lurus, pinggir = miring maks 65°). |
| 3   | 4 level                                | Pola brick berupa teks di `LEVELS`, mudah menambah level. Bonus skor sisa nyawa tiap level selesai.                                                   |
| 4   | 5 tipe brick                           | `1` `2` `3` = jumlah pukulan (warna berubah tiap kena), `#` baja kebal, `E` peledak.                                                                  |
| 5   | Power-up                               | Peluang drop 18%, ditangkap dengan paddle (tabel di bawah).                                                                                           |
| 6   | Fireball & Multi-Ball                  | Fireball menembus brick tanpa memantul (kecuali baja). Multi-Ball memecah tiap bola jadi 3.                                                           |
| 7   | Combo                                  | Hancurkan brick beruntun tanpa kena paddle → pengali skor ×2 tiap 5 combo (maks ×5).                                                                  |
| 8   | Latar gradasi                          | Gradasi biru tua → ungu dari 60 strip.                                                                                                                |
| 9   | Partikel                               | Serpihan berwarna saat brick hancur, kena gravitasi lalu hilang.                                                                                      |
| 10  | HUD                                    | Skor, rekor, level, nyawa, combo, dan efek aktif beserta sisa waktu.                                                                                  |
| 11  | Kontrol mulus                          | Keyboard (berbasis status tombol, bukan key-repeat) + mouse.                                                                                          |
| 12  | State machine + menu + pause           | `menu → ready → playing → levelclear → gameover/win`, plus `paused`.                                                                                  |
| 13  | Rekor tersimpan                        | High score disimpan di `highscore.json`.                                                                                                              |
| 14  | Brick peledak berantai                 | Brick `E` menghancurkan brick radius 100 px; brick `E` lain ikut meledak.                                                                             |

### Power-up

| Kapsul   | Efek                          |
| -------- | ----------------------------- |
| 🟩 **W** | Paddle lebar 1.6× (~10 detik) |
| 🟨 **M** | Multi-Ball                    |
| 🟧 **F** | Fireball (~10 detik)          |
| 🟥 **L** | Nyawa +1 (maks 5)             |

## 🧬 Struktur Kelas (Konsep PM)

```
GameObject            (induk: canvas, item, move, delete)
 ├── Ball             (bola: arah, kecepatan, mode api)
 ├── Paddle           (lebar dinamis)
 ├── Brick            (tipe, sisa pukulan, warna)
 ├── PowerUp          (kapsul jatuh)
 └── Particle         (serpihan)
Game(tk.Frame)        (input, loop, tabrakan, skor, level)
```

- **Inheritance** — semua objek game mewarisi `GameObject`.
- **Polymorphism** — `delete()` di-override (`Brick` hapus kilap, `PowerUp` hapus huruf); `move()` di `PowerUp` menggerakkan kapsul + huruf.
- **Encapsulation** — tiap kelas mengurus datanya sendiri (`Brick.hit()`, `Ball.set_angle()`).
- **Composition** — `Game` memiliki list `bricks`, `balls`, `powers`, `parts`.

## 🛠️ Menambah Level

Tambahkan pola ke `LEVELS` (tiap baris tepat 10 karakter):

```python
['1111111111', '#.E.22.E.#', '3333333333']   # # = baja, E = peledak, . = kosong
```

TAMPILAN GAME
![alt text](image.png)
![alt text](image-1.png)
