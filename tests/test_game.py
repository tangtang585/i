import os
import unittest
from unittest.mock import patch

import pygame

from game import ARENA, CRYSTAL_POSITIONS, Game, HEIGHT, PLAYER_SPEED, WIDTH, main


class GameplayTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.reset()

    def test_title_screen_freezes_game(self):
        game = Game()
        before = game.player.copy()
        game.update(0.1, (1, 0))
        self.assertEqual(game.player, before)

    def test_wasd_directions_and_diagonal_speed(self):
        for direction in [(0, -1), (-1, 0), (0, 1), (1, 0), (1, 1)]:
            with self.subTest(direction=direction):
                self.game.reset()
                self.game.player.update(155, 150)
                before = self.game.player.copy()
                self.game.update(0.05, direction)
                delta = self.game.player - before
                self.assertAlmostEqual(delta.length(), PLAYER_SPEED * 0.05)
                self.assertGreater(delta.dot(pygame.Vector2(direction)), 0)

    def test_arena_keeps_player_inside(self):
        self.game.player.update(13, 50)
        self.game.update(0.05, (-1, -1))
        self.assertTrue(ARENA.contains(self.game.player_rect))

    def test_tree_blocks_movement(self):
        wall = self.game.walls[0]
        self.game.player.update(wall.left - 10, wall.top)
        self.game.update(0.05, (1, 0))
        self.assertEqual(self.game.player_rect.right, wall.left)

    def test_all_crystals_are_reachable_and_win(self):
        for crystal in list(self.game.crystals):
            self.assertTrue(ARENA.contains(crystal))
            self.assertFalse(any(crystal.colliderect(wall) for wall in self.game.walls))
            self.game.player.update(crystal.topleft)
            self.game.update(0)
        self.assertEqual(self.game.collected, len(CRYSTAL_POSITIONS))
        self.assertEqual(self.game.state, "won")
        before = self.game.player.copy()
        self.game.update(0.05, (1, 0))
        self.assertEqual(self.game.player, before)

    def test_damage_cooldown_loss_and_restart(self):
        slime = self.game.slimes[0]
        self.game.player.update(slime.x, slime.y)
        self.game.update(0)
        self.assertEqual(self.game.health, 2)
        self.game.update(0)
        self.assertEqual(self.game.health, 2)
        for _ in range(2):
            self.game.invulnerable = 0
            self.game.update(0)
        self.assertEqual(self.game.state, "lost")
        self.game.reset()
        self.assertEqual(self.game.health, 3)
        self.assertEqual(self.game.collected, 0)
        self.assertEqual(self.game.state, "playing")

    def test_slimes_reverse_at_patrol_bounds(self):
        slime = self.game.slimes[0]
        slime.x = slime.right - 0.1
        slime.update(0.05)
        self.assertLess(slime.speed, 0)
        self.assertEqual(slime.x, slime.right)


class WindowTests(unittest.TestCase):
    def test_resize_preserves_minimum_canvas_size(self):
        for requested, expected in [
            ((WIDTH - 1, HEIGHT - 1), (WIDTH, HEIGHT)),
            ((WIDTH - 1, HEIGHT * 2), (WIDTH, HEIGHT * 2)),
            ((WIDTH * 2, HEIGHT - 1), (WIDTH * 2, HEIGHT)),
            ((WIDTH, HEIGHT), (WIDTH, HEIGHT)),
            ((WIDTH * 2, HEIGHT * 2), (WIDTH * 2, HEIGHT * 2)),
        ]:
            with self.subTest(requested=requested):
                displayed_sizes = []
                flip = pygame.display.flip

                def capture_frame():
                    window = pygame.display.get_surface()
                    displayed_sizes.append(window.get_size())
                    self.assertTrue(window.get_flags() & pygame.RESIZABLE)
                    flip()

                events = [pygame.event.Event(pygame.VIDEORESIZE,
                                             w=requested[0], h=requested[1]),
                          pygame.event.Event(pygame.QUIT)]
                with patch.dict(os.environ, {"SDL_VIDEODRIVER": "dummy"}), \
                        patch("pygame.event.get", return_value=events), \
                        patch("pygame.display.flip", side_effect=capture_frame):
                    main()
                self.assertEqual(displayed_sizes, [expected])


if __name__ == "__main__":
    unittest.main()
