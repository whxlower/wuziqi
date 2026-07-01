import 'board.dart';

class Rules {
  static const int WIN_COUNT = 5;
  static const List<List<int>> DIRECTIONS = [
    [0, 1],
    [1, 0],
    [1, 1],
    [1, -1],
  ];

  static int checkWin(Board board) {
    var lastMove = board.lastMove;
    if (lastMove[0] == -1) {
      return 0;
    }

    int row = lastMove[0];
    int col = lastMove[1];
    int player = board.getCell(row, col);

    for (var dir in DIRECTIONS) {
      int count = 1;
      count += _countInDirection(board, row, col, dir[0], dir[1], player);
      count += _countInDirection(board, row, col, -dir[0], -dir[1], player);
      if (count >= WIN_COUNT) {
        return player;
      }
    }

    if (board.isFull()) {
      return -1;
    }

    return 0;
  }

  static int _countInDirection(
    Board board,
    int row,
    int col,
    int dRow,
    int dCol,
    int player,
  ) {
    int count = 0;
    int r = row + dRow;
    int c = col + dCol;
    while (board.getCell(r, c) == player) {
      count++;
      r += dRow;
      c += dCol;
    }
    return count;
  }

  static List<List<int>> getWinningLine(Board board) {
    var lastMove = board.lastMove;
    if (lastMove[0] == -1) {
      return [];
    }

    int row = lastMove[0];
    int col = lastMove[1];
    int player = board.getCell(row, col);

    for (var dir in DIRECTIONS) {
      List<List<int>> line = [[row, col]];
      _collectInDirection(board, row, col, dir[0], dir[1], player, line);
      _collectInDirection(board, row, col, -dir[0], -dir[1], player, line);
      if (line.length >= WIN_COUNT) {
        return line;
      }
    }

    return [];
  }

  static void _collectInDirection(
    Board board,
    int row,
    int col,
    int dRow,
    int dCol,
    int player,
    List<List<int>> line,
  ) {
    int r = row + dRow;
    int c = col + dCol;
    while (board.getCell(r, c) == player) {
      line.add([r, c]);
      r += dRow;
      c += dCol;
    }
  }
}
