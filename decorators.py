# decorators.py
"""
Decoradores de aura — Patrón Decorator aplicado al dinosaurio.

Cada decorador envuelve al Player (o a otro decorador) y añade:
  - Un efecto visual (aura, partículas, etc.)
  - Una modificación de comportamiento (velocidad, escudo, invencibilidad, regen)

Se apilan en cadena:
  Thunder( Ice( Fire( Player ) ) )
  → Cada draw() delega hacia adentro y después dibuja su propia capa encima.

Los decoradores ahora interactúan con el sistema de animación del dinosaurio:
  - FireDecorator  → fuerza animación "Run" (el dino corre con fuego)
  - ThunderDecorator → fuerza animación "Jump" (el dino flota eléctrico)
  - IceDecorator / NatureDecorator → no fuerzan animación, solo efectos visuales
"""

import pygame
import math
import random
from base_entity import EntityComponent
from setting import (
    POWERUP_DURATION, PLAYER_SIZE, PLAYER_SPEED,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, GREY, BLACK,
    AURA_FIRE, AURA_ICE, AURA_THUNDER, AURA_HEAL,
)


# ════════════════════════════════════════════════════════════════
#  DECORADOR BASE — delega todo al componente envuelto
# ════════════════════════════════════════════════════════════════
class AuraDecorator(EntityComponent):
    """
    Decorator abstracto.
    Todos los decoradores concretos heredan de aquí.
    Delega cada método al componente envuelto (_entity).
    """
    NAME  = "Base"
    COLOR = WHITE

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        self._entity  = entity
        self.duration = duration
        self.timer    = 0

    # ── Propiedades de tiempo ────────────────────────────────
    @property
    def expired(self) -> bool:
        return self.timer >= self.duration

    @property
    def remaining(self) -> int:
        return max(0, self.duration - self.timer)

    @property
    def progress(self) -> float:
        """Progreso de 0.0 (recién adquirido) a 1.0 (expirado)."""
        return self.timer / self.duration if self.duration > 0 else 1.0

    # ── Delegación al componente envuelto ────────────────────
    def get_speed(self) -> int:
        return self._entity.get_speed()

    def get_rect(self) -> pygame.Rect:
        return self._entity.get_rect()

    def is_invincible(self) -> bool:
        return self._entity.is_invincible()

    def get_attack_bonus(self) -> int:
        return self._entity.get_attack_bonus()

    def get_state(self) -> str:
        return self._entity.get_state()

    def set_animation(self, name: str):
        self._entity.set_animation(name)

    def force_animation(self, name: str):
        self._entity.force_animation(name)

    # ── Update base ──────────────────────────────────────────
    def update(self):
        self._entity.update()
        if not self.expired:
            self.timer += 1

    # ── Draw base ────────────────────────────────────────────
    def draw(self, screen):
        self._entity.draw(screen)  # dibuja capas interiores primero

    # ── Utilidades visuales ──────────────────────────────────
    def _draw_timer_bar(self, screen, color, offset_y=0):
        """Barra de duración debajo del dinosaurio."""
        rect  = self.get_rect()
        bar_w = PLAYER_SIZE
        ratio = self.remaining / self.duration
        y_pos = rect.bottom + 6 + offset_y

        # Fondo
        bg = pygame.Rect(rect.centerx - bar_w // 2, y_pos, bar_w, 5)
        pygame.draw.rect(screen, (30, 30, 40), bg, border_radius=3)

        # Barra de progreso
        fg = pygame.Rect(rect.centerx - bar_w // 2, y_pos,
                         int(bar_w * ratio), 5)
        pygame.draw.rect(screen, color, fg, border_radius=3)

        # Borde sutil
        pygame.draw.rect(screen, (*color, 120), bg, 1, border_radius=3)

    def _get_base(self):
        """Navega hasta el Player base a través de la cadena."""
        obj = self._entity
        while hasattr(obj, '_entity'):
            obj = obj._entity
        return obj

    def _get_bar_offset(self) -> int:
        """Calcula offset vertical para la barra según decoradores apilados."""
        # Cada decorador dibuja su barra 10px más abajo
        count = 0
        obj = self._entity
        while hasattr(obj, '_entity'):
            if isinstance(obj, AuraDecorator) and not obj.expired:
                count += 1
            obj = obj._entity
        return count * 10


# ════════════════════════════════════════════════════════════════
#  🔥 FUEGO — Aura naranja, boost de velocidad, partículas de fuego
# ════════════════════════════════════════════════════════════════
class FireDecorator(AuraDecorator):
    """
    Envuelve al dinosaurio en llamas.
    ✦ Efecto: +3 velocidad
    ✦ Visual: partículas de fuego + aura pulsante naranja
    ✦ Animación: fuerza "Run" mientras está activo
    """
    NAME  = "Fuego +Vel"
    COLOR = AURA_FIRE
    BOOST = 3

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self.particles: list[list] = []  # [x, y, age, vx, vy]

    def get_speed(self) -> int:
        base_speed = self._entity.get_speed()
        return base_speed + (self.BOOST if not self.expired else 0)

    def get_attack_bonus(self) -> int:
        bonus = 2 if not self.expired else 0
        return self._entity.get_attack_bonus() + bonus

    def update(self):
        if not self.expired:
            # Inyectar velocidad al núcleo para que la animación lo detecte
            base = self._get_base()
            base.speed += self.BOOST
            self._entity.update()
            base.speed -= self.BOOST
            self.timer += 1

            # Forzar animación de correr
            base.force_animation("Run")

            # Generar partículas de fuego (desde la cola del dino)
            r = self.get_rect()
            for _ in range(2):
                px = r.centerx + random.randint(-12, 12)
                py = r.bottom + random.randint(-8, 4)
                vx = random.uniform(-0.8, 0.8)
                vy = random.uniform(-2.5, -0.5)
                self.particles.append([px, py, 0, vx, vy])
        else:
            self._entity.update()
            # Liberar animación forzada al expirar
            base = self._get_base()
            base.release_animation()

        # Envejecer y mover partículas
        new_particles = []
        for p in self.particles:
            p[0] += p[3]           # x += vx
            p[1] += p[4]           # y += vy
            p[4] -= 0.05           # gravedad inversa sutil
            p[2] += 1              # age++
            if p[2] < 20:
                new_particles.append(p)
        self.particles = new_particles

    def draw(self, screen):
        # Partículas de fuego DETRÁS del dinosaurio
        for x, y, age, *_ in self.particles:
            alpha  = max(0, 220 - age * 11)
            radius = max(1, 8 - age // 3)
            # Color que va de naranja a rojo con la edad
            r = min(255, AURA_FIRE[0] + age * 2)
            g = max(0, AURA_FIRE[1] - age * 5)
            b = max(0, AURA_FIRE[2] - age)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (r, g, b, alpha), (radius, radius), radius)
            screen.blit(surf, (int(x) - radius, int(y) - radius))

        # Dinosaurio
        self._entity.draw(screen)

        if not self.expired:
            rect   = self.get_rect()
            # Aura pulsante naranja alrededor del dino
            pulse  = abs(math.sin(self.timer * 0.12)) * 8
            radius = PLAYER_SIZE // 2 + 10 + int(pulse)
            surf   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*AURA_FIRE, 50), (radius, radius), radius)
            pygame.draw.circle(surf, (*AURA_FIRE, 130), (radius, radius), radius, 2)
            screen.blit(surf, (rect.centerx - radius, rect.centery - radius))

            # Barra de duración
            self._draw_timer_bar(screen, AURA_FIRE, self._get_bar_offset())


# ════════════════════════════════════════════════════════════════
#  ❄️  HIELO — Aura cyan, escudo que absorbe 1 golpe
# ════════════════════════════════════════════════════════════════
class IceDecorator(AuraDecorator):
    """
    Envuelve al dinosaurio en un escudo de hielo.
    ✦ Efecto: absorbe 1 golpe mortal
    ✦ Visual: cristales de hielo orbitando + aura cyan
    ✦ Animación: no fuerza (el dino puede moverse normalmente)
    """
    NAME  = "Hielo +Escudo"
    COLOR = AURA_ICE

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self.shield_hp   = 1       # absorbe 1 colisión
        self.flash_timer = 0       # flash al absorber golpe

    def absorb_hit(self) -> bool:
        """Absorbe un golpe. Retorna True si fue absorbido."""
        if self.shield_hp > 0 and not self.expired:
            self.shield_hp   -= 1
            self.flash_timer  = 15     # flash visual
            self.timer        = self.duration  # se agota
            return True
        return False

    def update(self):
        super().update()
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def draw(self, screen):
        self._entity.draw(screen)

        # Flash blanco al absorber golpe
        if self.flash_timer > 0:
            rect = self.get_rect()
            alpha = int(200 * (self.flash_timer / 15))
            flash_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, alpha))
            screen.blit(flash_surf, (rect.x - 10, rect.y - 10))

        if not self.expired and self.shield_hp > 0:
            rect   = self.get_rect()
            radius = PLAYER_SIZE // 2 + 18

            # Cristales de hielo orbitando — más grandes y brillantes
            for i in range(6):
                angle = math.radians(i * 60 + self.timer * 1.5)
                sx = rect.centerx + int(math.cos(angle) * radius)
                sy = rect.centery + int(math.sin(angle) * radius)

                # Cristal = diamante pequeño
                crystal_size = 7
                crystal = pygame.Surface((crystal_size * 2, crystal_size * 2), pygame.SRCALPHA)
                points = [
                    (crystal_size, 0),
                    (crystal_size * 2, crystal_size),
                    (crystal_size, crystal_size * 2),
                    (0, crystal_size),
                ]
                pygame.draw.polygon(crystal, (*AURA_ICE, 220), points)
                pygame.draw.polygon(crystal, (200, 240, 255, 160), points, 1)
                rot = pygame.transform.rotate(crystal, math.degrees(angle) * 0.5)
                screen.blit(rot, (sx - rot.get_width() // 2,
                                  sy - rot.get_height() // 2))

            # Aura circular helada
            aura_r = radius + 6
            surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*AURA_ICE, 30), (aura_r, aura_r), aura_r)
            pygame.draw.circle(surf, (*AURA_ICE, 100), (aura_r, aura_r), aura_r, 2)
            screen.blit(surf, (rect.centerx - aura_r, rect.centery - aura_r))

            # Barra de duración
            self._draw_timer_bar(screen, AURA_ICE, self._get_bar_offset())


# ════════════════════════════════════════════════════════════════
#  ⚡ RAYO — Aura amarilla, invencibilidad total temporal
# ════════════════════════════════════════════════════════════════
class ThunderDecorator(AuraDecorator):
    """
    Envuelve al dinosaurio en electricidad pura.
    ✦ Efecto: invencibilidad total (destruye enemigos al contacto)
    ✦ Visual: rayos eléctricos irradiando + parpadeo
    ✦ Animación: fuerza "Jump" (el dino parece flotar)
    """
    NAME  = "Rayo +Inven"
    COLOR = AURA_THUNDER

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self._bolts: list[tuple] = []  # rayos eléctricos pre-calculados

    def is_invincible(self) -> bool:
        return not self.expired or self._entity.is_invincible()

    def update(self):
        if not self.expired:
            # Forzar animación de salto (flotando)
            base = self._get_base()
            base.force_animation("Jump")

        self._entity.update()
        if not self.expired:
            self.timer += 1

            # Generar rayos eléctricos aleatorios cada pocos frames
            if self.timer % 3 == 0:
                self._bolts = []
                rect = self.get_rect()
                for _ in range(4):
                    angle  = random.uniform(0, math.pi * 2)
                    length = PLAYER_SIZE // 2 + random.randint(15, 35)
                    x1, y1 = rect.centerx, rect.centery
                    # Rayo con segmentos zigzag
                    points = [(x1, y1)]
                    segments = random.randint(3, 5)
                    for s in range(1, segments + 1):
                        t = s / segments
                        bx = x1 + int(math.cos(angle) * length * t) + random.randint(-6, 6)
                        by = y1 + int(math.sin(angle) * length * t) + random.randint(-6, 6)
                        points.append((bx, by))
                    self._bolts.append(points)
        else:
            # Liberar animación forzada
            base = self._get_base()
            base.release_animation()

    def draw(self, screen):
        # Parpadeo eléctrico: oculta al dino en frames alternos
        show = self.expired or (self.timer // 4) % 3 != 0
        if show:
            self._entity.draw(screen)

        if not self.expired:
            rect = self.get_rect()

            # Aura eléctrica central
            pulse = abs(math.sin(self.timer * 0.15)) * 6
            aura_r = PLAYER_SIZE // 2 + 12 + int(pulse)
            surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*AURA_THUNDER, 40), (aura_r, aura_r), aura_r)
            screen.blit(surf, (rect.centerx - aura_r, rect.centery - aura_r))

            # Rayos zigzag
            for bolt in self._bolts:
                if len(bolt) >= 2:
                    alpha = 180 + int(math.sin(self.timer * 0.3) * 75)
                    bolt_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    # Rayo principal
                    pygame.draw.lines(bolt_surf, (*AURA_THUNDER, alpha), False, bolt, 2)
                    # Brillo central
                    pygame.draw.lines(bolt_surf, (255, 255, 200, alpha // 2), False, bolt, 4)
                    screen.blit(bolt_surf, (0, 0))

            # Chispas pequeñas alrededor
            for i in range(3):
                angle = math.radians(self.timer * 8 + i * 120)
                sr = PLAYER_SIZE // 2 + 20
                sx = rect.centerx + int(math.cos(angle) * sr)
                sy = rect.centery + int(math.sin(angle) * sr)
                spark = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(spark, (*AURA_THUNDER, 200), (3, 3), 3)
                screen.blit(spark, (sx - 3, sy - 3))

            # Barra de duración
            self._draw_timer_bar(screen, AURA_THUNDER, self._get_bar_offset())


# ════════════════════════════════════════════════════════════════
#  🌿 NATURALEZA — Aura verde, regenera vida
# ════════════════════════════════════════════════════════════════
class NatureDecorator(AuraDecorator):
    """
    Envuelve al dinosaurio en energía natural.
    ✦ Efecto: regenera 1 vida cada REGEN_INTERVAL frames
    ✦ Visual: hojas orbitando + pulso de curación verde
    ✦ Animación: no fuerza (permite moverse libremente)
    """
    NAME  = "Natura +Regen"
    COLOR = AURA_HEAL
    REGEN_INTERVAL = 90    # cada 90 frames (1.5 seg) regenera 1 vida

    def __init__(self, entity: EntityComponent, duration: int = POWERUP_DURATION):
        super().__init__(entity, duration)
        self.regen_tick  = 0
        self.healed      = 0       # puntos regenerados (game.py los consume)
        self.heal_flash  = 0       # flash verde cuando cura

    def update(self):
        super().update()
        if not self.expired:
            self.regen_tick += 1
            if self.regen_tick >= self.REGEN_INTERVAL:
                self.healed     += 1
                self.regen_tick  = 0
                self.heal_flash  = 20  # activar flash

        if self.heal_flash > 0:
            self.heal_flash -= 1

    def draw(self, screen):
        self._entity.draw(screen)

        # Flash verde al regenerar
        if self.heal_flash > 0:
            rect = self.get_rect()
            alpha = int(100 * (self.heal_flash / 20))
            flash = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
            flash.fill((*AURA_HEAL, alpha))
            screen.blit(flash, (rect.x - 8, rect.y - 8))

        if not self.expired:
            rect = self.get_rect()

            # Hojas orbitando — más grandes y detalladas
            for i in range(5):
                angle  = math.radians(i * 72 + self.timer * 2)
                orbit_r = PLAYER_SIZE // 2 + 20
                lx = rect.centerx + int(math.cos(angle) * orbit_r)
                ly = rect.centery + int(math.sin(angle) * orbit_r)

                # Hoja = elipse rotada con gradiente
                leaf_w, leaf_h = 16, 8
                leaf = pygame.Surface((leaf_w, leaf_h), pygame.SRCALPHA)
                # Hoja principal
                pygame.draw.ellipse(leaf, (*AURA_HEAL, 220), (0, 0, leaf_w, leaf_h))
                # Nervadura central
                pygame.draw.line(leaf, (40, 180, 60, 180),
                                 (2, leaf_h // 2), (leaf_w - 2, leaf_h // 2), 1)
                rotated = pygame.transform.rotate(leaf, math.degrees(angle))
                screen.blit(rotated, (lx - rotated.get_width() // 2,
                                      ly - rotated.get_height() // 2))

            # Pulso de energía natural
            pulse  = abs(math.sin(self.timer * 0.08)) * 6
            aura_r = PLAYER_SIZE // 2 + 8 + int(pulse)
            surf   = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*AURA_HEAL, 35), (aura_r, aura_r), aura_r)
            pygame.draw.circle(surf, (*AURA_HEAL, 80), (aura_r, aura_r), aura_r, 2)
            screen.blit(surf, (rect.centerx - aura_r, rect.centery - aura_r))

            # Pequeñas esporas de vida flotando
            for i in range(3):
                spore_angle = math.radians(self.timer * 1.5 + i * 120)
                sr = PLAYER_SIZE // 2 + 10 + int(math.sin(self.timer * 0.1 + i) * 8)
                sx = rect.centerx + int(math.cos(spore_angle) * sr)
                sy = rect.centery + int(math.sin(spore_angle) * sr)
                spore = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(spore, (*AURA_HEAL, 160), (2, 2), 2)
                screen.blit(spore, (sx - 2, sy - 2))

            # Barra de duración
            self._draw_timer_bar(screen, AURA_HEAL, self._get_bar_offset())