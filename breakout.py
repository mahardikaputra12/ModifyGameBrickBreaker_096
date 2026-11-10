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

