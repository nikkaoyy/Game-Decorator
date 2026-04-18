# settings.py
"""
Configuración centralizada del juego Dinosaurio con Patrón Decorador.
Todas las constantes del juego se definen aquí para fácil ajuste.
"""

# ── Pantalla ──────────────────────────────────────────────────
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
TITLE         = "Dino Aura — Patrón Decorador con Power-ups"
FPS           = 60

# ── Colores base ──────────────────────────────────────────────
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GREY   = (128, 128, 128)

# Colores del entorno
BG_TOP      = (15, 12, 30)      # Gradiente superior (cielo nocturno)
BG_BOTTOM   = (35, 55, 45)      # Gradiente inferior (selva)
STAR_COLOR  = (60, 60, 100)

# Jugador y enemigos (colores de respaldo si no cargan los sprites)
PLAYER_COLOR = (80, 200, 100)   # Verde dinosaurio
ENEMY_COLOR  = (200, 60, 60)    # Rojo peligro

# ── Aura de decoradores ──────────────────────────────────────
AURA_FIRE    = (255, 100, 20)   # 🔥 Naranja — ataque de fuego / velocidad
AURA_ICE     = (100, 220, 255)  # ❄️  Cyan   — escudo de hielo
AURA_THUNDER = (255, 240, 40)   # ⚡  Amarillo — invencibilidad de rayo
AURA_HEAL    = (60, 220, 80)    # 🌿  Verde  — regeneración natural

# ── Dinosaurio (sprites) ─────────────────────────────────────
DINO_SCALE       = (64, 64)     # Tamaño al escalar los sprites
DINO_ANIM_SPEED  = 6            # Frames de juego entre cada cuadro de animación
DINO_SPRITES_DIR = "src"        # Carpeta con los sprites

# Animaciones disponibles y cuántos frames tiene cada una
DINO_ANIMS = {
    "Idle": 10,
    "Run":   8,
    "Walk": 10,
    "Jump": 12,
    "Dead":  8,
}

# ── Físicas ──────────────────────────────────────────────────
PLAYER_SIZE   = 64              # Coincide con DINO_SCALE para colisiones
PLAYER_SPEED  = 4
ENEMY_SIZE    = 36              # Proporcional al dinosaurio
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 4

# ── Power-ups ────────────────────────────────────────────────
POWERUP_SIZE     = 28           # Un poco más grande para mejor visibilidad
POWERUP_DURATION = 420          # Duración en frames (7 s × 60 FPS)

# ── Juego ────────────────────────────────────────────────────
INITIAL_LIVES       = 3
MAX_LIVES           = 5
ENEMY_SPAWN_MIN     = 30        # Intervalo mínimo de spawn de enemigos (frames)
ENEMY_SPAWN_BASE    = 60        # Intervalo base de spawn
POWERUP_SPAWN_INTERVAL = 360   # Cada ~6 segundos aparece un power-up

# ── Partículas ambientales ────────────────────────────────────
AMBIENT_PARTICLE_COUNT = 40     # Esporas/polvo flotando en el fondo
AMBIENT_PARTICLE_COLOR = (80, 120, 70, 60)  # Verde bosque translúcido