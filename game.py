# game.py
"""
Clase principal del juego — Dino Aura.

Orquesta todos los sistemas:
  - Patrón Decorador: apila poderes sobre el dinosaurio
  - Spawn de enemigos y power-ups
  - Colisiones y lógica de vida
  - HUD con información de poderes activos
  - Fondo ambiental prehistórico con partículas
"""

import pygame
import random
import math
from setting import *
from player     import Player
from enemy      import Enemy
from powerup    import PowerUp
from decorators import (
    AuraDecorator,
    FireDecorator,
    IceDecorator,
    ThunderDecorator,
    NatureDecorator,
)

# Mapeo tipo de power-up → clase decoradora
DECORATOR_MAP = {
    "fire":    FireDecorator,
    "ice":     IceDecorator,
    "thunder": ThunderDecorator,
    "nature":  NatureDecorator,
}


class Game:
    """Bucle principal del juego Dino Aura."""

    def __init__(self):
        pygame.init()
        self.screen   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock_pg = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 48)
        self.font_med = pygame.font.SysFont(None, 32)
        self.font_sm  = pygame.font.SysFont(None, 24)
        self.running  = True
        self.score    = 0
        self.lives    = INITIAL_LIVES
        self.frame    = 0

        # ── Jugador (dinosaurio animado) ─────────────────────
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

        # ── Grupos de sprites ────────────────────────────────
        self.enemies  = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Spawn inicial: un power-up de cada tipo
        for kind in DECORATOR_MAP:
            self.powerups.add(PowerUp(kind))

        self.spawn_powerup_timer = 0
        self.spawn_enemy_timer   = 0

        # ── Fondo ────────────────────────────────────────────
        self._bg_surface  = self._create_background()
        self._stars       = self._create_stars()
        self._particles   = self._create_ambient_particles()

    # ═══════════════════════════════════════════════════════════
    #  Fondo ambiental prehistórico
    # ═══════════════════════════════════════════════════════════
    def _create_background(self) -> pygame.Surface:
        """Crea un gradiente de fondo de cielo nocturno a selva."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
            g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
            b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        return surf

    def _create_stars(self) -> list:
        """Estrellas en la parte superior del cielo."""
        stars = []
        for _ in range(60):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            size = random.randint(1, 3)
            brightness = random.randint(40, 100)
            speed = random.uniform(0.3, 0.8)
            stars.append([x, y, size, brightness, speed])
        return stars

    def _create_ambient_particles(self) -> list:
        """Esporas / polvo prehistórico flotando."""
        particles = []
        for _ in range(AMBIENT_PARTICLE_COUNT):
            x   = random.randint(0, SCREEN_WIDTH)
            y   = random.randint(0, SCREEN_HEIGHT)
            vx  = random.uniform(-0.3, 0.3)
            vy  = random.uniform(-0.5, -0.1)
            size = random.randint(1, 3)
            alpha = random.randint(30, 80)
            particles.append([x, y, vx, vy, size, alpha])
        return particles

    def _update_particles(self):
        """Actualiza esporas ambientales."""
        for p in self._particles:
            p[0] += p[2] + math.sin(self.frame * 0.01 + p[1] * 0.01) * 0.3
            p[1] += p[3]
            if p[1] < -10:
                p[0] = random.randint(0, SCREEN_WIDTH)
                p[1] = SCREEN_HEIGHT + 10
            if p[0] < -10:
                p[0] = SCREEN_WIDTH + 10
            elif p[0] > SCREEN_WIDTH + 10:
                p[0] = -10

    def _draw_background(self):
        """Renderiza fondo + estrellas + partículas."""
        self.screen.blit(self._bg_surface, (0, 0))

        # Estrellas titilantes
        for star in self._stars:
            x, y, size, base_bright, speed = star
            # Titileo
            bright = base_bright + int(math.sin(self.frame * speed * 0.1) * 30)
            bright = max(20, min(120, bright))
            color  = (bright, bright, bright + 20)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), size)

        # Partículas ambientales
        for p in self._particles:
            x, y, _, _, size, alpha = p
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (80, 140, 70, alpha), (size, size), size)
            self.screen.blit(surf, (int(x) - size, int(y) - size))

    # ═══════════════════════════════════════════════════════════
    #  Navegación de la cadena de decoradores
    # ═══════════════════════════════════════════════════════════
    def _get_base(self) -> Player:
        """Navega hasta el Player base."""
        obj = self.player
        while hasattr(obj, '_entity'):
            obj = obj._entity
        return obj

    def _collect_decorators(self) -> list[AuraDecorator]:
        """Retorna todos los decoradores activos (de afuera hacia adentro)."""
        result, obj = [], self.player
        while hasattr(obj, '_entity'):
            result.append(obj)
            obj = obj._entity
        return result

    def _find_ice(self) -> IceDecorator | None:
        """Busca el primer IceDecorator activo en la cadena."""
        for dec in self._collect_decorators():
            if isinstance(dec, IceDecorator) and not dec.expired:
                return dec
        return None

    # ═══════════════════════════════════════════════════════════
    #  Aplicar y limpiar decoradores
    # ═══════════════════════════════════════════════════════════
    def apply_power(self, kind: str):
        """Envuelve al jugador con un nuevo decorador (patrón Decorator)."""
        cls = DECORATOR_MAP[kind]
        self.player = cls(self.player)

    def prune_expired(self):
        """
        Reconstruye la cadena eliminando decoradores expirados.
        El Player base nunca se elimina.
        """
        # Recolectar nodos de la cadena
        chain, obj = [], self.player
        while hasattr(obj, '_entity'):
            chain.append(obj)
            obj = obj._entity
        base = obj  # Player concreto

        # Liberar animaciones forzadas de decoradores expirados
        for d in chain:
            if d.expired and isinstance(d, (FireDecorator, ThunderDecorator)):
                base.release_animation()

        # Filtrar activos
        active = [d for d in chain if not d.expired]

        # Reconstruir cadena: base → d[-1] → ... → d[0]
        current = base
        for dec in reversed(active):
            dec._entity = current
            current = dec
        self.player = current

    # ═══════════════════════════════════════════════════════════
    #  Colisiones
    # ═══════════════════════════════════════════════════════════
    def check_enemy_collision(self):
        player_rect = self.player.get_rect()
        for enemy in list(self.enemies):
            if not player_rect.colliderect(enemy.rect):
                continue

            # ¿Invencible por Rayo?
            if self.player.is_invincible():
                enemy.kill()
                self.score += 300  # bonus por destruir con rayo
                return

            # ¿Escudo de Hielo?
            ice = self._find_ice()
            if ice and ice.absorb_hit():
                enemy.kill()
                self.score += 100  # bonus menor por escudo
                return

            # Sin protección → pierde vida
            self.lives -= 1
            enemy.kill()
            if self.lives <= 0:
                self.running = False

    def check_powerup_collision(self):
        player_rect = self.player.get_rect()
        for pu in list(self.powerups):
            if player_rect.colliderect(pu.rect):
                self.apply_power(pu.kind)
                pu.kill()

    # ═══════════════════════════════════════════════════════════
    #  Spawn
    # ═══════════════════════════════════════════════════════════
    def maybe_spawn_enemy(self):
        self.spawn_enemy_timer += 1
        # La dificultad aumenta con el score
        interval = max(ENEMY_SPAWN_MIN, ENEMY_SPAWN_BASE - self.score // 200)
        bonus = self.score // 3000  # velocidad extra por dificultad
        if self.spawn_enemy_timer >= interval:
            self.enemies.add(Enemy(speed_bonus=bonus))
            self.spawn_enemy_timer = 0

    def maybe_spawn_powerup(self):
        self.spawn_powerup_timer += 1
        if self.spawn_powerup_timer >= POWERUP_SPAWN_INTERVAL:
            self.powerups.add(PowerUp())
            self.spawn_powerup_timer = 0

    # ═══════════════════════════════════════════════════════════
    #  HUD — Interfaz de usuario
    # ═══════════════════════════════════════════════════════════
    def draw_hud(self):
        # ── Puntaje (centro arriba) ──────────────────────────
        score_text = f"Puntaje: {self.score // 60:04d}"
        score_surf = self.font_med.render(score_text, True, WHITE)
        # Sombra
        shadow = self.font_med.render(score_text, True, (0, 0, 0))
        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - shadow.get_width() // 2 + 2, 10))
        self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 8))

        # ── Vidas (esquina superior izquierda — corazones) ───
        for i in range(self.lives):
            x = 14 + i * 26
            y = 14
            # Corazón simple con dos círculos y un triángulo
            heart_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(heart_surf, (220, 50, 50), (7, 7), 5)
            pygame.draw.circle(heart_surf, (220, 50, 50), (13, 7), 5)
            pygame.draw.polygon(heart_surf, (220, 50, 50), [(2, 9), (10, 18), (18, 9)])
            self.screen.blit(heart_surf, (x, y))

        # ── Poderes activos (panel derecho) ──────────────────
        decs = self._collect_decorators()
        active_decs = [d for d in decs if not d.expired]

        if active_decs:
            # Panel de fondo semitransparente
            panel_h = len(active_decs) * 30 + 10
            panel = pygame.Surface((120, panel_h), pygame.SRCALPHA)
            panel.fill((10, 10, 20, 140))
            pygame.draw.rect(panel, (60, 60, 80, 100), (0, 0, 120, panel_h), 1,
                             border_radius=6)
            self.screen.blit(panel, (SCREEN_WIDTH - 130, 6))

        for i, dec in enumerate(active_decs):
            ratio = dec.remaining / dec.duration
            bar_w = 90
            x, y  = SCREEN_WIDTH - 124, 12 + i * 30

            # Barra de fondo
            pygame.draw.rect(self.screen, (30, 30, 50),
                             (x, y, bar_w, 20), border_radius=5)
            # Barra de duración con gradiente
            if ratio > 0:
                bar_color = dec.COLOR
                # Color se oscurece al expirar
                if ratio < 0.25:
                    t = ratio / 0.25
                    bar_color = tuple(int(c * t) for c in dec.COLOR)
                pygame.draw.rect(self.screen, bar_color,
                                 (x, y, int(bar_w * ratio), 20), border_radius=5)
            # Borde
            pygame.draw.rect(self.screen, (*dec.COLOR, 120),
                             (x, y, bar_w, 20), 1, border_radius=5)
            # Nombre del poder
            name = dec.NAME.split("+")[0].strip()
            txt = self.font_sm.render(name, True, WHITE)
            self.screen.blit(txt, (x + 4, y + 2))

        # ── Instrucción al inicio ────────────────────────────
        if self.frame < 240:
            alpha = max(0, 255 - self.frame)
            hint_surf = self.font_sm.render(
                "← ↑ ↓ → Muévete  |  Recoge gemas para obtener poderes",
                True, (150, 150, 150)
            )
            # Fade out
            fade = pygame.Surface(hint_surf.get_size(), pygame.SRCALPHA)
            fade.fill((0, 0, 0, 255 - alpha))
            hint_surf.set_alpha(alpha)
            self.screen.blit(hint_surf,
                             (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2,
                              SCREEN_HEIGHT - 32))

    # ═══════════════════════════════════════════════════════════
    #  Loop principal
    # ═══════════════════════════════════════════════════════════
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        self.frame += 1
        self.score += 1

        # Actualizar entidades
        self.player.update()
        self.enemies.update()
        self.powerups.update()
        self._update_particles()

        # Spawns
        self.maybe_spawn_enemy()
        self.maybe_spawn_powerup()

        # Limpiar decoradores expirados
        self.prune_expired()

        # Colisiones
        self.check_powerup_collision()
        self.check_enemy_collision()

        # Regeneración de vida (NatureDecorator)
        for dec in self._collect_decorators():
            if isinstance(dec, NatureDecorator) and dec.healed > 0:
                self.lives = min(MAX_LIVES, self.lives + dec.healed)
                dec.healed = 0

    def draw(self):
        # Fondo con partículas
        self._draw_background()

        # Power-ups
        for pu in self.powerups:
            pu.draw(self.screen)

        # Enemigos
        for en in self.enemies:
            self.screen.blit(en.image, en.rect)

        # Dinosaurio (con decoradores)
        self.player.draw(self.screen)

        # HUD
        self.draw_hud()

        pygame.display.flip()

    # ═══════════════════════════════════════════════════════════
    #  Game Over — con animación de muerte del dinosaurio
    # ═══════════════════════════════════════════════════════════
    def game_over_screen(self):
        """Pantalla de Game Over con la animación Dead del dinosaurio."""
        base = self._get_base()

        # Reproducir animación de muerte
        dead_frames = base.animations.get("Dead", base.animations["Idle"])
        total_anim_frames = len(dead_frames) * DINO_ANIM_SPEED

        for f in range(total_anim_frames + 120):  # animación + pausa
            self.screen.blit(self._bg_surface, (0, 0))

            # Título GAME OVER con efecto de temblor
            shake_x = random.randint(-2, 2) if f < 30 else 0
            shake_y = random.randint(-2, 2) if f < 30 else 0

            title = self.font_big.render("GAME OVER", True, (220, 50, 50))
            title_shadow = self.font_big.render("GAME OVER", True, (80, 15, 15))
            self.screen.blit(title_shadow,
                             (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3 + shake_x,
                              120 + 3 + shake_y))
            self.screen.blit(title,
                             (SCREEN_WIDTH // 2 - title.get_width() // 2 + shake_x,
                              120 + shake_y))

            # Dinosaurio muerto (centrado, más grande)
            frame_idx = min(f // DINO_ANIM_SPEED, len(dead_frames) - 1)
            dino_img  = dead_frames[frame_idx]
            # Escalar al doble para la pantalla de game over
            big_dino = pygame.transform.smoothscale(
                dino_img, (DINO_SCALE[0] * 2, DINO_SCALE[1] * 2)
            )
            dino_x = SCREEN_WIDTH // 2 - big_dino.get_width() // 2
            dino_y = 200
            self.screen.blit(big_dino, (dino_x, dino_y))

            # Puntaje
            score_text = f"Puntaje final: {self.score // 60}"
            score_surf = self.font_med.render(score_text, True, WHITE)
            self.screen.blit(score_surf,
                             (SCREEN_WIDTH // 2 - score_surf.get_width() // 2,
                              200 + big_dino.get_height() + 20))

            # Mensaje de cierre (aparece después de la animación)
            if f > total_anim_frames:
                close_text = "Cerrando..."
                alpha = min(255, (f - total_anim_frames) * 5)
                close_surf = self.font_sm.render(close_text, True, GREY)
                close_surf.set_alpha(alpha)
                self.screen.blit(close_surf,
                                 (SCREEN_WIDTH // 2 - close_surf.get_width() // 2,
                                  200 + big_dino.get_height() + 60))

            pygame.display.flip()
            self.clock_pg.tick(FPS)

            # Permitir cerrar durante el game over
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

        pygame.time.wait(1000)

    def run(self):
        """Bucle principal del juego."""
        while self.running:
            self.clock_pg.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        self.game_over_screen()
        pygame.quit()