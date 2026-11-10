🧱 Brick Breaker — Ultimate Edition

Modifikasi besar dari game Brick Breaker bawaan (Python + Tkinter). Game ini ditulis ulang dengan prinsip Pemrograman Berorientasi Objek (PBO) dan dilengkapi 18 fitur baru.

Nama / NIM: [Mahardika Putra Qohar / 20250140096 ] Mata kuliah: Pemrograman MultiPlatfrom

▶️ Cara Menjalankan
bash
python brick_breaker.py

Kebutuhan: Python 3.6+ dengan Tkinter (sudah termasuk di instalasi Python standar Windows/macOS; di Linux: sudo apt install python3-tk). Tidak perlu library tambahan.

🎮 Kontrol
Tombol Fungsi
← → atau A D Gerakkan paddle
Mouse Gerakkan paddle mengikuti kursor
SPASI / Klik kiri Mulai game, luncurkan bola, lanjut level
P Pause / lanjut
R Restart dari level 1
M Suara hidup / mati (Windows)
Esc Kembali ke menu
🔍 Perbandingan dengan Game Bawaan
Aspek Bawaan Modifikasi
Ukuran layar 610 × 400 800 × 600
Kecepatan frame 20 FPS (patah-patah) ~60 FPS, berbasis delta-time
Level 1 (pola tetap) 5 level dengan pola & tingkat kesulitan berbeda
Tipe brick 2 tipe (1x & 2x pukul) 5 tipe (1x, 2x, 3x, baja kebal, peledak)
Pantulan paddle Sama di semua bagian Sudut bergantung bagian paddle yang kena
Power-up Tidak ada 6 jenis
Skor / rekor Tidak ada Skor, combo, rekor tersimpan
Pause, menu, efek visual & suara Tidak ada Ada
✨ Daftar Fitur

Setiap fitur ditandai [FITUR #n] di komentar brick_breaker.py agar mudah dicari.

# Fitur Penjelasan Kelas / Metode

1 Game loop 60 FPS + delta-time Gerakan dikali dt sehingga kecepatan game konsisten di komputer lambat maupun cepat. Game.game_loop
2 Fisika bola yang lebih realistis Posisi memakai float dan vektor arah. Tabrakan lingkaran-vs-persegi memantul sesuai sisi yang terkena, tanpa menembus brick. Sudut pantul paddle bergantung pada titik tumbukan: tengah = lurus, pinggir = miring (maks 65°). Ball, ball_paddle_collision, ball_brick_collision
3 Kontrol mulus (keyboard + mouse) Pakai status tombol yang ditekan, bukan key-repeat, sehingga paddle bergerak halus. Mouse juga bisa dipakai. Paddle, update_paddle, on_mouse_move
4 Kesulitan progresif Kecepatan awal bola naik tiap level dan bola makin cepat tiap kena paddle (ada batas maksimum). base_speed, ball_paddle_collision
5 5 level Pola brick didefinisikan sebagai teks (LEVELS), jadi mudah menambah level baru. Ada bonus skor sisa nyawa tiap level selesai. LEVELS, load_level, check_level_clear
6 5 tipe brick 1 merah (1 pukul), 2 biru (2 pukul), 3 ungu (3 pukul), # baja (kebal), E peledak. Brick bertingkat berubah warna saat terkena. Brick, BRICK_TYPES
7 Power-up jatuh dari brick Peluang drop 18%. Tangkap dengan paddle. Lihat tabel power-up di bawah. PowerUp, apply_powerup
8 HUD lengkap Menampilkan skor, rekor, level, nyawa, combo, dan efek aktif beserta sisa waktunya. create_hud, update_hud
9 Rekor tersimpan High score disimpan ke highscore.json dan dimuat saat game dibuka lagi. load_high_score, save_high_score
10 Latar gradasi + bintang parallax Gradasi ungu→biru dari 60 strip, ditambah bintang yang jatuh dengan kecepatan berbeda sesuai ukuran. draw_background, create_stars
11 Partikel ledakan Brick hancur menyebar serpihan berwarna yang kena gravitasi dan memudar. Particle
12 Jejak bola (trail) Bola meninggalkan jejak yang mengecil dan warnanya menyatu dengan latar. Ball.render
13 Fireball Bola menjadi api: langsung menghancurkan brick tanpa memantul (kecuali baja). Ball.set_fire, ball_brick_collision
14 State machine + menu + pause Alur game jelas: menu → ready → playing → levelclear → gameover/win, plus paused. Ada layar menu, level selesai, kalah, dan menang. Game.state, toggle_pause, finish
15 Sistem combo Hancurkan brick beruntun tanpa menyentuh paddle untuk menaikkan pengali skor (×2 tiap 5 combo, maks ×5). destroy_brick
16 Brick peledak berantai Brick E meledak dan menghancurkan brick di radius 100 px. Brick peledak lain di sekitarnya ikut meledak (rekursif). explode
17 Multi-Ball Setiap bola dipecah menjadi 3 (maks 12 bola). Game baru berakhir bila semua bola jatuh. spawn_multiball
18 Efek suara Bunyi berbeda untuk dinding, paddle, brick, baja, ledakan, power-up, kalah, dan menang. Berjalan di thread terpisah agar game tidak macet. Hanya Windows (winsound), di OS lain game tetap berjalan tanpa suara. Sound
Power-up
Kapsul Efek Durasi
🟩 W Paddle Lebar (1.6×) ~10 detik
🟨 M Multi-Ball Permanen sampai bola jatuh
🟦 S Bola Lambat (65%) ~10 detik
🟧 F Fireball ~10 detik
🟥 + Nyawa +1 (maks 5) Instan
🟪 N Paddle Sempit (0.6×) — power-up buruk, hindari! ~10 detik
Skor
Aksi Poin
Brick 1x / 2x / 3x pukul 10 / 20 / 30 × pengali combo
Brick peledak 40 × pengali combo
Pukulan yang belum menghancurkan brick 5
Menangkap power-up 25
Selesai level 100 × sisa nyawa
🧬 Struktur Kelas (Konsep PBO)
GameObject (induk: canvas, item, get_position, move, delete)
├── Ball (bola: arah, kecepatan, jejak, mode api)
├── Paddle (paddle: lebar dinamis, gerak mulus)
├── Brick (brick: tipe, sisa pukulan, warna)
├── PowerUp (kapsul jatuh)
└── Particle (serpihan ledakan)

Sound (efek suara)
Game(tk.Frame) (pengatur alur: input, loop, tabrakan, skor, level)
Inheritance — Ball, Paddle, Brick, PowerUp, dan Particle mewarisi GameObject.
Polymorphism — delete() di-override: Ball menghapus jejaknya, Brick menghapus kilap/label, PowerUp menghapus huruf. move() di PowerUp menggerakkan kapsul sekaligus hurufnya.
Encapsulation — Tiap kelas mengurus data dan perilakunya sendiri (misalnya Brick.hit(), Paddle.set_width(), Ball.rotate()).
Composition — Game memiliki objek-objek tersebut dalam list bricks, balls, powerups, particles.
🛠️ Menambah Level Sendiri

Tambahkan satu pola ke LEVELS di brick_breaker.py. Tiap baris harus tepat 10 karakter:

python
['1111111111', # 1,2,3 = brick bertingkat
'#.E.22.E.#', # # = baja, E = peledak, . = kosong
'3333333333']
📁 Isi Folder
brick_breaker.py # kode game (dengan komentar tiap fitur)
README.md # dokumentasi ini
highscore.json # dibuat otomatis setelah main
