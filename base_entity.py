# base_entity.py
"""
Clase base abstracta (Component) del patrón Decorador.

Define la interfaz completa que deben implementar tanto el jugador
concreto (Player) como todos los decoradores (AuraDecorator y sus hijos).

Métodos de interfaz:
  - update()          → lógica de cada frame
  - draw(screen)      → renderizado
  - get_rect()        → hitbox para colisiones
  - get_speed()       → velocidad actual (afectada por decoradores)
  - is_invincible()   → ¿el jugador es invulnerable?
  - get_state()       → estado de animación actual ("idle", "run", etc.)
  - set_animation()   → establecer la animación del sprite
  - force_animation() → un decorador fuerza una animación específica
  - get_attack_bonus()→ daño adicional por decoradores activos
"""

import pygame


class EntityComponent:
    """Interfaz base del patrón Decorator — Component."""

    # ── Métodos obligatorios ────────────────────────────────
    def update(self):
        raise NotImplementedError("El método update() debe ser implementado por las subclases.")

    def draw(self, screen):
        raise NotImplementedError("El método draw() debe ser implementado por las subclases.")

    def get_rect(self) -> pygame.Rect:
        raise NotImplementedError("El método get_rect() debe ser implementado por las subclases.")

    def get_speed(self) -> int:
        raise NotImplementedError("El método get_speed() debe ser implementado por las subclases.")

    def is_invincible(self) -> bool:
        raise NotImplementedError("El método is_invincible() debe ser implementado por las subclases.")

    # ── Animación ───────────────────────────────────────────
    def get_state(self) -> str:
        """Retorna el estado de animación actual ('idle', 'run', etc.)."""
        return "idle"

    def set_animation(self, name: str):
        """Establece la animación activa por nombre."""
        pass

    def force_animation(self, name: str):
        """Un decorador fuerza una animación (ej: Jump durante Thunder)."""
        pass

    # ── Combate ─────────────────────────────────────────────
    def get_attack_bonus(self) -> int:
        """Retorna el bonus de daño otorgado por decoradores activos."""
        return 0