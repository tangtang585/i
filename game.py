"""Pixel Grove — a tiny, asset-free pixel adventure. Run: python game.py."""
import math
import random
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT, SCALE = 320, 240, 3
ARENA = pygame.Rect(12, 48, 296, 160)
PLAYER_SPEED = 78
CRYSTAL_POSITIONS = [(34, 67), (153, 63), (282, 65), (78, 111),
                     (237, 111), (38, 185), (155, 184), (282, 183)]
TREE_POSITIONS = [(98, 67), (202, 67), (45, 132), (144, 117),
                  (263, 139), (96, 167), (207, 169)]
COLORS = {"outline": "#122f36", "grass": "#224c43", "mint": "#9fe8b7",
          "white": "#e5f4d6", "muted": "#7eac96", "gold": "#ffd879"}

PLAYER_ART = ["...kkkk...", "..kbbbbk..", "..kbbbbk..", "..kssssk..",
              "..kskskk..", "...ssss...", "..kcccck..", ".ksccccsk.",
              "..kcccck..", "...k..k...", "..kk..kk.."]
TREE_ART = [".....kk.....", "....kggk....", "...kggggk...", "..kgglgggk..",
            ".kggllggggk.", "kggglggggggk", ".kggggggggk.", "..kkkkkkkk..",
            "....kttk....", "....kttk....", "...kkttkk..."]
SLIME_ART = ["...kkkk...", "..krrrrk..", ".krrrrrrk.", "krrwrrwrrk",
             "krrkrrkrrk", "krrrrrrrrk", ".kkkkkkkk."]


def sprite(surface, art, x, y, palette, scale=1):
    for row, line in enumerate(art):
        for column, pixel in enumerate(line):
            if pixel in palette:
                pygame.draw.rect(surface, palette[pixel],
                                 (x + column * scale, y + row * scale, scale, scale))


@dataclass
class Slime:
    x: float
    y: float
    left: float
    right: float
    speed: float

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), 12, 10)

    def update(self, dt):
        self.x += self.speed * dt
        if self.x <= self.left or self.x >= self.right:
            self.x = max(self.left, min(self.right, self.x))
            self.speed *= -1


class Game:
    def __init__(self):
        self.reset()
        self.state = "ready"

    def reset(self):
        self.player = pygame.Vector2(155, 142)
        self.walls = [pygame.Rect(x, y + 7, 18, 15) for x, y in TREE_POSITIONS]
        self.crystals = [pygame.Rect(x, y, 8, 10) for x, y in CRYSTAL_POSITIONS]
        self.slimes = [Slime(55, 91, 25, 125, 28), Slime(215, 91, 184, 286, -34),
                       Slime(133, 163, 125, 174, 24)]
        self.health = 3
        self.invulnerable = 0.0
        self.time = 0.0
        self.state = "playing"

    @property
    def player_rect(self):
        return pygame.Rect(round(self.player.x), round(self.player.y), 10, 11)

    @property
    def collected(self):
        return len(CRYSTAL_POSITIONS) - len(self.crystals)

    def move(self, direction, dt):
        direction = pygame.Vector2(direction)
        if direction.length_squared() > 0:
            direction = direction.normalize() * PLAYER_SPEED * dt
        # Resolve each axis separately so the player can slide along trees.
        for axis in (0, 1):
            self.player[axis] += direction[axis]
            rect = self.player_rect.clamp(ARENA)
            for wall in self.walls:
                if rect.colliderect(wall):
                    if axis == 0:
                        if direction.x > 0:
                            rect.right = wall.left
                        elif direction.x < 0:
                            rect.left = wall.right
                    else:
                        if direction.y > 0:
                            rect.bottom = wall.top
                        elif direction.y < 0:
                            rect.top = wall.bottom
            # Preserve subpixel movement unless a boundary actually corrected it.
            if axis == 0 and rect.x != round(self.player.x):
                self.player.x = rect.x
            if axis == 1 and rect.y != round(self.player.y):
                self.player.y = rect.y

    def update(self, dt, direction=(0, 0)):
        if self.state != "playing":
            return
        self.time += dt
        self.invulnerable = max(0, self.invulnerable - dt)
        self.move(direction, dt)
        for slime in self.slimes:
            slime.update(dt)
        rect = self.player_rect
        self.crystals = [crystal for crystal in self.crystals if not rect.colliderect(crystal)]
        if self.invulnerable == 0 and any(rect.colliderect(slime.rect) for slime in self.slimes):
            self.health -= 1
            self.invulnerable = 1.5
            if self.health == 0:
                self.state = "lost"
        if not self.crystals and self.health > 0:
            self.state = "won"


class Renderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 16)
        self.small = pygame.font.Font(None, 12)
        self.title = pygame.font.Font(None, 30)
        self.background = self.make_background()

    def text(self, surface, message, pos, color="white", font=None, center=False):
        label = (font or self.font).render(message, False, COLORS.get(color, color))
        rect = label.get_rect(center=pos) if center else label.get_rect(topleft=pos)
        surface.blit(label, rect)

    def make_background(self):
        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill(COLORS["outline"])
        pygame.draw.rect(surface, "#376554", ARENA.inflate(4, 4))
        pygame.draw.rect(surface, COLORS["grass"], ARENA)
        rng = random.Random(7)
        for _ in range(400):
            x, y = rng.randrange(14, 304), rng.randrange(50, 205)
            color = rng.choice(["#2b5748", "#315d4b", "#1d443e"])
            pygame.draw.rect(surface, color, (x, y, 2, 2))
        for x, y in [(24, 104), (181, 192), (292, 126), (122, 56), (62, 194)]:
            pygame.draw.rect(surface, "#72926a", (x, y, 2, 4))
            pygame.draw.rect(surface, "#e4ab88", (x - 1, y, 4, 2))
        return surface

    def draw(self, surface, game):
        surface.blit(self.background, (0, 0))
        self.text(surface, "PIXEL GROVE", (12, 10), "mint")
        self.text(surface, "A LITTLE FOREST ADVENTURE", (12, 27), "muted", self.small)
        for i in range(3):
            color = "#ee8f83" if i < game.health else "#36554c"
            sprite(surface, [".rr.rr.", "rrrrrrr", "rrrrrrr", ".rrrrr.", "..rrr..", "...r..."],
                   268 + i * 12, 13, {"r": color})
        for crystal in game.crystals:
            x, y = crystal.topleft
            y += round(math.sin(game.time * 3 + x) * 2)
            pygame.draw.ellipse(surface, "#193d37", (x - 1, crystal.y + 10, 10, 3))
            pygame.draw.polygon(surface, "#ffe1a0", [(x + 4, y), (x + 8, y + 5),
                                                    (x + 4, y + 10), (x, y + 5)])
            pygame.draw.line(surface, "#fff4d0", (x + 4, y + 2), (x + 4, y + 7))
        # Sort sprites by their feet so walking behind a tree looks natural.
        objects = [(y + 22, "tree", x, y) for x, y in TREE_POSITIONS]
        objects.extend((s.y + 10, "slime", s.x, s.y) for s in game.slimes)
        objects.append((game.player.y + 11, "player", game.player.x, game.player.y))
        for _, kind, x, y in sorted(objects):
            x, y = round(x), round(y)
            if kind == "tree":
                pygame.draw.ellipse(surface, "#193d37", (x - 2, y + 17, 27, 8))
                sprite(surface, TREE_ART, x - 3, y, {"k": "#153c35", "g": "#49835d",
                                                    "l": "#70aa6c", "t": "#a28057"}, 2)
            elif kind == "slime":
                sprite(surface, SLIME_ART, x, y + 2, {"k": "#3f3842", "r": "#d87976", "w": "#fff0cf"})
            elif game.invulnerable == 0 or int(game.time * 12) % 2 == 0:
                sprite(surface, PLAYER_ART, x, y, {"k": "#17363c", "b": "#a5d2dc",
                                                  "s": "#f3c896", "c": "#dbe8cc"})
        self.text(surface, f"CRYSTALS  {game.collected} / 8", (12, 218), "gold", self.small)
        self.text(surface, "WASD MOVE   R RESTART   ESC QUIT", (126, 218), "muted", self.small)
        if game.state != "playing":
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((9, 27, 29, 175))
            surface.blit(shade, (0, 0))
            pygame.draw.rect(surface, "#102e32", (35, 77, 250, 92))
            pygame.draw.rect(surface, "#62957a", (35, 77, 250, 92), 1)
            title = {"ready": "PIXEL GROVE", "won": "FOREST RESTORED!", "lost": "TRY AGAIN?"}[game.state]
            subtitle = {"ready": "Collect 8 crystals. Watch out for slimes!",
                        "won": "You found every crystal. Nice work!",
                        "lost": "The slimes caught you. Keep moving!"}[game.state]
            self.text(surface, title, (160, 99), "mint", self.title, True)
            self.text(surface, subtitle, (160, 127), "white", self.small, True)
            prompt = "SPACE TO START  /  WASD TO MOVE" if game.state == "ready" else "R TO PLAY AGAIN  /  ESC TO QUIT"
            self.text(surface, prompt, (160, 151), "gold", self.small, True)


def main():
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption("Pixel Grove | WASD adventure")
    window = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), pygame.RESIZABLE)
    canvas = pygame.Surface((WIDTH, HEIGHT))
    renderer, game, clock = Renderer(), Game(), pygame.time.Clock()
    running = True
    try:
        while running:
            dt = min(clock.tick(60) / 1000, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r or (event.key == pygame.K_SPACE and game.state == "ready"):
                        game.reset()
            keys = pygame.key.get_pressed()
            game.update(dt, (int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
                             int(keys[pygame.K_s]) - int(keys[pygame.K_w])))
            renderer.draw(canvas, game)
            # Whole-number scaling keeps the pixels crisp; letterbox resized windows.
            scale = max(1, min(window.get_width() // WIDTH, window.get_height() // HEIGHT))
            scaled = pygame.transform.scale(canvas, (WIDTH * scale, HEIGHT * scale))
            window.fill(COLORS["outline"])
            window.blit(scaled, scaled.get_rect(center=window.get_rect().center))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
