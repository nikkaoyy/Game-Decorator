# player.py
"""
Jugador concreto (ConcreteComponent) del patrón Decorador.

Carga los sprites del dinosaurio desde src/ y maneja las animaciones:
  - Idle  → sin movimiento
  - Walk  → movimiento sin boost de velocidad
  - Run   → movimiento con boost de velocidad (FireDecorator)
  - Jump  → forzado por ThunderDecorator (invencibilidad)
  - Dead  → usado en la pantalla de Game Over

El Player es el núcleo de la cadena de decoradores.
Los decoradores envuelven a esta clase para añadir auras y efectos.
"""

import os
import pygame
from setting import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, WHITE,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    DINO_SCALE, DINO_ANIM_SPEED, DINO_SPRITES_DIR, DINO_ANIMS,
)
from base_entity import EntityComponent


class Player(EntityComponent):
    """Dinosaurio animado — Componente concreto del patrón Decorador."""

    def __init__(self, x: int, y: int):
        self.speed = PLAYER_SPEED
        self.size  = PLAYER_SIZE

        # ── Cargar sprites ───────────────────────────────────
        self.animations: dict[str, list[pygame.Surface]] = {}
        self._load_sprites()

        # ── Estado de animación ──────────────────────────────
        self.current_anim   = "Idle"
        self.frame_index    = 0
        self.anim_counter   = 0
        self.facing_right   = True      # dirección del sprite
        self._forced_anim   = None      # si un decorador fuerza una animación

        # ── Imagen y rect ────────────────────────────────────
        self.image = self.animations["Idle"][0]
        self.rect  = self.image.get_rect(center=(x, y))

    # ─────────────────────────────────────────────────────────
    #  Carga de sprites
    # ─────────────────────────────────────────────────────────
    def _load_sprites(self):
        """Carga y escala todos los frames de animación desde src/."""
        base_dir = os.path.join(os.path.dirname(__file__), DINO_SPRITES_DIR)

        for anim_name, frame_count in DINO_ANIMS.items():
            frames = []
            for i in range(1, frame_count + 1):
                filename = f"{anim_name} ({i}).png"
                path     = os.path.join(base_dir, filename)
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    surf = pygame.transform.smoothscale(surf, DINO_SCALE)
                    frames.append(surf)
                except (FileNotFoundError, pygame.error):
                    # Sprite de respaldo si falta el archivo
                    fallback = pygame.Surface(DINO_SCALE, pygame.SRCALPHA)
                    pygame.draw.rect(fallback, PLAYER_COLOR,
                                     (0, 0, *DINO_SCALE), border_radius=8)
                    pygame.draw.circle(fallback, WHITE,
                                       (DINO_SCALE[0] // 2, DINO_SCALE[1] // 3), 4)
                    frames.append(fallback)

            self.animations[anim_name] = frames

        # Asegurar que al menos exista "Idle" con 1 frame de respaldo
        if not self.animations.get("Idle"):
            fb = pygame.Surface(DINO_SCALE, pygame.SRCALPHA)
            pygame.draw.rect(fb, PLAYER_COLOR, (0, 0, *DINO_SCALE), border_radius=8)
            self.animations["Idle"] = [fb]

    # ─────────────────────────────────────────────────────────
    #  Control de animación
    # ─────────────────────────────────────────────────────────
    def set_animation(self, name: str):
        """Cambia la animación si existe y no está forzada."""
        if self._forced_anim:
            return  # un decorador la tiene bloqueada
        if name in self.animations and name != self.current_anim:
            self.current_anim = name
            self.frame_index  = 0
            self.anim_counter = 0

    def force_animation(self, name: str):
        """Un decorador fuerza una animación específica."""
        if name in self.animations:
            self._forced_anim = name
            if self.current_anim != name:
                self.current_anim = name
                self.frame_index  = 0
                self.anim_counter = 0

    def release_animation(self):
        """Libera la animación forzada."""
        self._forced_anim = None

    def get_state(self) -> str:
        return self.current_anim.lower()

    # ─────────────────────────────────────────────────────────
    #  Métodos de la interfaz EntityComponent
    # ─────────────────────────────────────────────────────────
    def get_speed(self) -> int:
        return self.speed

    def is_invincible(self) -> bool:
        return False

    def get_attack_bonus(self) -> int:
        return 0

    def get_rect(self) -> pygame.Rect:
        return self.rect

    # ─────────────────────────────────────────────────────────
    #  Update — movimiento + selección de animación
    # ─────────────────────────────────────────────────────────
    def update(self):
        keys = pygame.key.get_pressed()
        spd  = self.speed
        moving = False

        # Movimiento en 4 direcciones
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= spd
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += spd
            self.facing_right = True
            moving = True
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= spd
            moving = True
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += spd
            moving = True

        # Seleccionar animación según estado (si no está forzada)
        if not self._forced_anim:
            if moving:
                # Run si tiene boost de velocidad, Walk si es velocidad normal
                if self.speed > PLAYER_SPEED:
                    self.set_animation("Run")
                else:
                    self.set_animation("Walk")
            else:
                self.set_animation("Idle")

        # Avanzar frame de animación
        self.anim_counter += 1
        if self.anim_counter >= DINO_ANIM_SPEED:
            self.anim_counter = 0
            frames = self.animations.get(self.current_anim, self.animations["Idle"])
            self.frame_index = (self.frame_index + 1) % len(frames)

        # Actualizar imagen
        frames = self.animations.get(self.current_anim, self.animations["Idle"])
        self.image = frames[self.frame_index % len(frames)]

    # ─────────────────────────────────────────────────────────
    #  Draw
    # ─────────────────────────────────────────────────────────
    def draw(self, screen):
        img = self.image
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, self.rect)

    # ─────────────────────────────────────────────────────────
    #  Animación de muerte (para Game Over)
    # ─────────────────────────────────────────────────────────
    def play_death_frame(self, frame: int) -> pygame.Surface:
        """Retorna el frame de la animación Dead para Game Over."""
        dead_frames = self.animations.get("Dead", self.animations["Idle"])
        idx = min(frame, len(dead_frames) - 1)
        img = dead_frames[idx]
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        return img
    
    # ─────────────────────────────────────────────────────────
    #  Reset - volver al estado inicial del personaje
    # ─────────────────────────────────────────────────────────
    def reset_position(self,x,y:int):
        self.center = (x,y)
        self.rect.center = self.center

    def reset_speed(self):
        self.speed = PLAYER_SPEED
    
    def reset_animation(self):
        self.current_anim = "Idle"
        self.frame_index = 0
        self.anim_counter = 0
        self._forced_anim = None

    def reset(self,x,y):
        self.reset_position(x,y)
        self.reset_speed()
        self.reset_animation()