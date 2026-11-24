# 🦕 Dino Aura — Patrón Decorador con Power-ups

> Juego 2D en Python/Pygame donde un dinosaurio prehistórico recolecta auras elementales para sobrevivir a una lluvia de meteoritos, implementando el **Patrón de Diseño Decorator** como núcleo arquitectónico.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Arquitectura — Patrón Decorator](#arquitectura--patrón-decorator)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Mecánicas de Juego](#mecánicas-de-juego)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Reporte SonarQube](#reporte-sonarqube)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Licencia](#licencia)

---

## Descripción del Proyecto

**Dino Aura** es un videojuego de acción 2D desarrollado con Python y Pygame. El jugador controla un dinosaurio animado que se mueve en un ambiente prehistórico nocturno, recogiendo gemas de poder para activar auras elementales que le otorgan habilidades especiales mientras esquiva —o destruye— rocas que caen del cielo.

El proyecto fue construido como ejercicio académico del **Patrón de Diseño Decorator (GoF)**, demostrando cómo se pueden apilar comportamientos sobre un objeto base en tiempo de ejecución sin modificar su clase.

---

## Arquitectura — Patrón Decorator

### Diagrama de la cadena de decoradores

```
┌─────────────────────────────────────────────────────┐
│  ThunderDecorator  ← decorador más externo          │
│    └── IceDecorator                                 │
│          └── FireDecorator                          │
│                └── Player  ← componente concreto   │
└─────────────────────────────────────────────────────┘
```

Cada decorador **envuelve** al jugador (o a otro decorador) y extiende su comportamiento delegando hacia adentro en cada llamada a `update()` y `draw()`.

### Clases principales

| Clase | Rol | Archivo |
|---|---|---|
| `EntityComponent` | Interfaz abstracta (Component) | `base_entity.py` |
| `Player` | Componente Concreto | `player.py` |
| `AuraDecorator` | Decorator Abstracto | `decorators.py` |
| `FireDecorator` | Decorator Concreto — Velocidad 🔥 | `decorators.py` |
| `IceDecorator` | Decorator Concreto — Escudo ❄️ | `decorators.py` |
| `ThunderDecorator` | Decorator Concreto — Invencibilidad ⚡ | `decorators.py` |
| `NatureDecorator` | Decorator Concreto — Regeneración 🌿 | `decorators.py` |
| `Game` | Orquestador principal | `game.py` |
| `Enemy` | Enemigos que caen | `enemy.py` |
| `PowerUp` | Gemas recolectables | `powerup.py` |

### Flujo del Patrón Decorator en el juego

1. El `Player` existe como `EntityComponent` concreto.
2. Al recoger una gema, `Game.apply_power(kind)` envuelve al jugador actual con el decorador correspondiente.
3. Los decoradores pueden apilarse: `Thunder(Ice(Fire(Player)))`.
4. Cada frame, `Game.prune_expired()` reconstruye la cadena eliminando decoradores cuyo timer venció.
5. El HUD muestra barras de duración para cada decorador activo.

---

## Estructura del Repositorio

```
Game-Decorator/
│
├── main.py              # Punto de entrada
├── game.py              # Bucle principal, colisiones, HUD, spawn
├── player.py            # Dinosaurio animado (ConcreteComponent)
├── decorators.py        # AuraDecorator + Fire/Ice/Thunder/Nature
├── base_entity.py       # Interfaz EntityComponent (Component)
├── enemy.py             # Rocas prehistóricas enemigas
├── powerup.py           # Gemas recolectables
├── setting.py           # Constantes globales del juego
│
├── src/                 # 🖼️ Sprites del dinosaurio (no incluidos en repo por peso)
│   ├── Idle (1).png     # 10 frames — estado en reposo
│   ├── Walk (1).png     # 10 frames — caminar
│   ├── Run (1).png      #  8 frames — correr (FireDecorator)
│   ├── Jump (1).png     # 12 frames — saltar (ThunderDecorator)
│   └── Dead (1).png     #  8 frames — muerte (Game Over)
│
├── .gitignore
└── LICENSE              # MIT
```

> **Nota sobre `src/`:** La carpeta de sprites no se versiona en este repositorio debido a su tamaño. Contiene los spritesheets del dinosaurio animado divididos en frames individuales con nomenclatura `Animación (N).png`. Sin estos archivos, el juego usa sprites de respaldo generados proceduralmente.

---

## Mecánicas de Juego

### Controles

| Tecla | Acción |
|---|---|
| ← ↑ ↓ → | Mover al dinosaurio |
| `ESC` | Salir del juego |

### Power-ups (Gemas)

| Gema | Color | Efecto | Animación |
|---|---|---|---|
| 🔥 Fuego | Naranja | +3 velocidad, +2 ataque | Fuerza **Run** |
| ❄️ Hielo | Cyan | Escudo (absorbe 1 golpe) | Normal |
| ⚡ Rayo | Amarillo | Invencibilidad total, destruye enemigos | Fuerza **Jump** |
| 🌿 Natura | Verde | Regenera 1 vida cada 1.5 s | Normal |

### Sistema de colisiones

```
Colisión con enemigo:
  ├── ¿Thunder activo?  → enemigo destruido (+300 pts)
  ├── ¿Ice con escudo?  → golpe absorbido (+100 pts)
  └── Sin protección   → -1 vida (Game Over si vidas = 0)
```

### Progresión de dificultad

La frecuencia de spawn de enemigos aumenta con el puntaje (`intervalo = max(30, 60 - score // 200)`), y la velocidad de los enemigos crece con `score // 3000`.

---

## Instalación y Ejecución

### Requisitos

- Python 3.10+
- Pygame 2.x

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/nikkaoyy/Game-Decorator.git
cd Game-Decorator

# Instalar dependencias
pip install pygame

# Ejecutar
python main.py
```

> Si los sprites de `src/` no están presentes, el juego arranca con figuras geométricas de respaldo y funciona correctamente.

---

## Reporte SonarQube

Análisis estático realizado con **SonarCloud** sobre el código fuente del repositorio.

> 🔗 Proyecto: [`nikkaoyy_Game-Decorator`](https://sonarcloud.io/summary/new_code?id=nikkaoyy_Game-Decorator)

### Resumen ejecutivo

| Dimensión | Calificación | Detalle |
|---|---|---|
| **Seguridad** | 🟢 A | 0 problemas de seguridad abiertos |
| **Confiabilidad** | 🟢 A | 0 problemas de confiabilidad |
| **Mantenibilidad** | 🟢 A | 11 problemas de mantenibilidad |
| **Duplicación** | ✅ 0.0% | Sin código duplicado detectado |
| **Cobertura** | ⚪ N/D | No hay pruebas unitarias configuradas |
| **Security Review** | 🔴 E | 33 hotspots de seguridad pendientes de revisión |

### Problemas abiertos — 11 en total

Todos los issues abiertos impactan **Mantenibilidad** (ninguno afecta Seguridad ni Confiabilidad).

Los tipos más comunes en proyectos Python/Pygame de esta naturaleza incluyen:

- Variables o parámetros definidos y no utilizados
- Funciones con complejidad cognitiva elevada (como `game_over_screen` y `draw_hud`)
- Métodos que podrían extraerse a funciones auxiliares
- Cadenas de comparación que pueden simplificarse

> Para ver el listado completo y detallado: [Ver issues en SonarCloud](https://sonarcloud.io/project/issues?issueStatuses=OPEN&id=nikkaoyy_Game-Decorator)

### Security Hotspots — 33 pendientes de revisión

La calificación **E** en Security Review se debe a que **33 hotspots** están marcados como "To Review" (100% sin revisar). Es importante aclarar que un hotspot **no es una vulnerabilidad confirmada**: SonarCloud los señala como patrones que requieren revisión manual para determinar si representan un riesgo real.

En un proyecto de juego con Pygame, los hotspots típicos son:

- Uso de `random` estándar (no criptográficamente seguro) para generación de posiciones y valores de juego — **no es un riesgo** en este contexto.
- Llamadas a `pygame.Surface` con flags que pueden ser mal interpretados.
- Ausencia de validación de inputs externos (no aplica, es un juego local).

**Acción recomendada:** Revisar cada hotspot en SonarCloud y marcarlo como "Safe" o "Acknowledged" según corresponda para mejorar la calificación.

> Ver hotspots: [Security Hotspots en SonarCloud](https://sonarcloud.io/project/security_hotspots?id=nikkaoyy_Game-Decorator)

### Tendencia de mantenibilidad

Los 11 issues de mantenibilidad se mantienen **estables** (sin cambio vs. los últimos 30 días), lo que indica que el código no está acumulando deuda técnica nueva.

```
may 20 ──────────────────── may 21 ─────────── may 22
   [11]                        [11]               [11]   ← sin cambio
```

### Métricas de calidad del código

| Métrica | Valor |
|---|---|
| Líneas de código analizadas | ~600 (6 módulos Python) |
| Duplicación | 0.0% |
| Issues de seguridad | 0 |
| Issues de confiabilidad | 0 |
| Issues de mantenibilidad | 11 |
| Hotspots de seguridad | 33 (pendientes de revisión manual) |
| Cobertura de pruebas | Sin datos (no hay tests) |

### Recomendaciones de mejora

Basado en el análisis:

1. **Cobertura:** Agregar pruebas unitarias con `pytest` para las clases de decoradores — al menos verificar que la cadena se construye y expira correctamente.
2. **Hotspots:** Realizar la revisión manual de los 33 hotspots en SonarCloud; la mayoría deberían marcarse como seguros dado el contexto de juego local.
3. **Mantenibilidad:** Considerar refactorizar `draw_hud()` y `game_over_screen()` en `game.py` extrayendo secciones de renderizado a métodos auxiliares para reducir la complejidad cognitiva.
4. **Gate de calidad:** Configurar un Quality Gate en SonarCloud y ejecutar un análisis nuevo para obtener el estado oficial.

---

## Tecnologías Utilizadas

- **Python 3.10+** — Lenguaje principal
- **Pygame 2.x** — Motor gráfico, eventos, audio
- **Patrón Decorator (GoF)** — Arquitectura central del proyecto
- **SonarCloud** — Análisis estático de calidad y seguridad

---

## Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](./LICENSE) para más detalles.

```
MIT License — Copyright (c) 2026 nikkaoyy
```

## Contexto académico

Patrón de comportamiento **Decorator** aplicado a una nave: cada decorador le añade un poder para destruir asteroides, con pygame. Trabajo del curso **Modelos de Programación** de Ingeniería de Sistemas (Universidad Distrital Francisco José
de Caldas), con el docente **Daza**, el mismo curso donde aprendí a revisar la calidad del código con **SonarQube**.
