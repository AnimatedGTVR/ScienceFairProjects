# tests/test_board.py

import unittest
from backend.board import MinesweeperBoard

class TestMinesweeperBoard(unittest.TestCase):

    def test_board_dimensions(self):
        board = MinesweeperBoard(width=5, height=4, num_mines=3)
        self.assertEqual(len(board.board), 4)
        self.assertEqual(len(board.board[0]), 5)

    def test_mine_count(self):
        board = MinesweeperBoard(width=5, height=5, num_mines=5)
        board.reveal(2, 2)  # Mines are placed on the first reveal.
        mine_count = sum(1 for row in board.board for cell in row if cell == -1)
        self.assertEqual(mine_count, 5)
        for row in range(1, 4):
            for col in range(1, 4):
                self.assertNotEqual(board.board[row][col], -1)

    def test_reveal_non_mine(self):
        board = MinesweeperBoard(width=3, height=3, num_mines=0)
        hit_mine = board.reveal(0, 0)
        self.assertFalse(hit_mine)
        self.assertTrue(board.revealed[0][0])

if __name__ == "__main__":
    unittest.main()
