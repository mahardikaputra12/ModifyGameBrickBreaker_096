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

