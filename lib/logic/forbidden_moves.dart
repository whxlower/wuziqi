import 'board.dart';

class ForbiddenMoves {
  static const List<List<int>> DIRECTIONS = [
    [0, 1],
    [1, 0],
    [1, 1],
    [1, -1],
  ];

  static bool isForbidden(Board board, int row, int col) {
    if (board.getCell(row, col) != 0) {
      return false;
    }

    Board testBoard = board.clone();
    testBoard.placeStone(row, col);

    if (testBoard.currentPlayer == 1) {
      return false;
    }

    if (_isOverline(testBoard, row, col)) {
      return true;
    }

    if (_isDoubleThree(testBoard, row, col)) {
      return true;
    }

    if (_isDoubleFour(testBoard, row, col)) {
      return true;
    }

    return false;
  }

  static bool _isOverline(Board board, int row, int col) {
    int player = board.getCell(row, col);
    for (var dir in DIRECTIONS) {
      int count = 1;
      count += _countInDirection(board, row, col, dir[0], dir[1], player);
      count += _countInDirection(board, row, col, -dir[0], -dir[1], player);
      if (count > 5) {
        return true;
      }
    }
    return false;
  }

  static bool _isDoubleThree(Board board, int row, int col) {
    int player = board.getCell(row, col);
    int openThreeCount = 0;

    for (var dir in DIRECTIONS) {
      var pattern = _getLinePattern(board, row, col, dir, player);
      if (_countOpenThree(pattern) > 0) {
        openThreeCount++;
      }
    }

    return openThreeCount >= 2;
  }

  static bool _isDoubleFour(Board board, int row, int col) {
    int player = board.getCell(row, col);
    int fourCount = 0;

    for (var dir in DIRECTIONS) {
      var pattern = _getLinePattern(board, row, col, dir, player);
      if (_countFour(pattern) > 0) {
        fourCount++;
      }
    }

    return fourCount >= 2;
  }

  static List<int> _getLinePattern(
    Board board,
    int row,
    int col,
    List<int> dir,
    int player,
  ) {
    List<int> pattern = [];

    int r = row;
    int c = col;
    while (r >= 0 && r < Board.SIZE && c >= 0 && c < Board.SIZE) {
      r -= dir[0];
      c -= dir[1];
    }
    r += dir[0];
    c += dir[1];

    while (r >= 0 && r < Board.SIZE && c >= 0 && c < Board.SIZE) {
      pattern.add(board.getCell(r, c));
      r += dir[0];
      c += dir[1];
    }

    return pattern;
  }

  static int _countOpenThree(List<int> pattern) {
    String s = pattern.join('');
    int count = 0;

    if (s.contains('01110')) count++;
    if (s.contains('010110')) count++;
    if (s.contains('011010')) count++;
    if (s.contains('10110')) count++;
    if (s.contains('11010')) count++;
    if (s.contains('01101')) count++;
    if (s.contains('01011')) count++;

    return count;
  }

  static int _countFour(List<int> pattern) {
    String s = pattern.join('');
    int count = 0;

    if (s.contains('011110')) count++;
    if (s.contains('01111')) count++;
    if (s.contains('11110')) count++;
    if (s.contains('11011')) count++;
    if (s.contains('10111')) count++;
    if (s.contains('11101')) count++;
    if (s.contains('101101')) count++;

    return count;
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

  static String getForbiddenType(Board board, int row, int col) {
    if (board.getCell(row, col) != 0) {
      return '';
    }

    Board testBoard = board.clone();
    testBoard.placeStone(row, col);

    if (testBoard.currentPlayer == 1) {
      return '';
    }

    if (_isOverline(testBoard, row, col)) {
      return '长连禁手';
    }

    if (_isDoubleThree(testBoard, row, col)) {
      return '三三禁手';
    }

    if (_isDoubleFour(testBoard, row, col)) {
      return '四四禁手';
    }

    return '';
  }
}
