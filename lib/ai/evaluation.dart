import '../logic/board.dart';
import '../logic/rules.dart';
import '../logic/forbidden_moves.dart';

class Evaluation {
  static const int WIN_SCORE = 1000000;
  static const int FOUR_SCORE = 100000;
  static const int OPEN_THREE_SCORE = 10000;
  static const int THREE_SCORE = 5000;
  static const int OPEN_TWO_SCORE = 1000;
  static const int TWO_SCORE = 500;
  static const int CENTER_BONUS = 10;

  static int evaluate(Board board, int player) {
    int score = 0;

    for (int i = 0; i < Board.SIZE; i++) {
      for (int j = 0; j < Board.SIZE; j++) {
        if (board.getCell(i, j) == player) {
          score += _evaluatePosition(board, i, j, player);
          score += _getCenterBonus(i, j);
        }
      }
    }

    int opponent = player == 1 ? 2 : 1;
    for (int i = 0; i < Board.SIZE; i++) {
      for (int j = 0; j < Board.SIZE; j++) {
        if (board.getCell(i, j) == opponent) {
          score -= _evaluatePosition(board, i, j, opponent);
          score -= _getCenterBonus(i, j);
        }
      }
    }

    return score;
  }

  static int evaluateMove(Board board, int row, int col, int player) {
    if (!board.isEmpty(row, col)) return -1000000;

    Board testBoard = board.clone();
    testBoard.placeStone(row, col);

    int score = 0;

    for (var dir in Rules.DIRECTIONS) {
      int count = 0;
      int empty = 0;

      for (int i = -4; i <= 4; i++) {
        int r = row + dir[0] * i;
        int c = col + dir[1] * i;
        if (r >= 0 && r < Board.SIZE && c >= 0 && c < Board.SIZE) {
          int cell = testBoard.getCell(r, c);
          if (cell == player) count++;
          else if (cell == 0) empty++;
          else break;
        }
      }

      if (count >= 5) return WIN_SCORE;
      if (count == 4 && empty >= 1) score += FOUR_SCORE;
      else if (count == 4) score += FOUR_SCORE ~/ 2;
      else if (count == 3 && empty >= 2) score += OPEN_THREE_SCORE;
      else if (count == 3 && empty >= 1) score += THREE_SCORE;
      else if (count == 2 && empty >= 2) score += OPEN_TWO_SCORE;
      else if (count == 2 && empty >= 1) score += TWO_SCORE;
    }

    int opponent = player == 1 ? 2 : 1;
    for (var dir in Rules.DIRECTIONS) {
      int count = 0;
      int empty = 0;

      for (int i = -4; i <= 4; i++) {
        int r = row + dir[0] * i;
        int c = col + dir[1] * i;
        if (r >= 0 && r < Board.SIZE && c >= 0 && c < Board.SIZE) {
          int cell = board.getCell(r, c);
          if (cell == opponent) count++;
          else if (cell == 0) empty++;
          else break;
        }
      }

      if (count == 4 && empty >= 1) score += FOUR_SCORE;
      else if (count == 4) score += FOUR_SCORE ~/ 2;
      else if (count == 3 && empty >= 2) score += OPEN_THREE_SCORE;
      else if (count == 3 && empty >= 1) score += THREE_SCORE;
    }

    score += _getCenterBonus(row, col);

    return score;
  }

  static int _evaluatePosition(Board board, int row, int col, int player) {
    int score = 0;

    for (var dir in Rules.DIRECTIONS) {
      var pattern = _getPattern(board, row, col, dir, player);
      score += _patternToScore(pattern);
    }

    return score;
  }

  static List<int> _getPattern(
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
      if (board.getCell(r, c) != player && board.getCell(r, c) != 0) {
        break;
      }
      r += dir[0];
      c += dir[1];
    }

    return pattern;
  }

  static int _patternToScore(List<int> pattern) {
    String str = pattern.join('');

    if (str.contains('11111') || str.contains('22222')) {
      return WIN_SCORE;
    }

    if (str.contains('011110') || str.contains('022220')) {
      return FOUR_SCORE;
    }

    if (str.contains('01111') || str.contains('11110') ||
        str.contains('02222') || str.contains('22220')) {
      return FOUR_SCORE ~/ 2;
    }

    if (str.contains('01110') || str.contains('02220')) {
      return OPEN_THREE_SCORE;
    }

    if (str.contains('0111') || str.contains('1110') ||
        str.contains('0222') || str.contains('2220')) {
      return THREE_SCORE;
    }

    if (str.contains('1011') || str.contains('1101') ||
        str.contains('2022') || str.contains('2202')) {
      return THREE_SCORE;
    }

    if (str.contains('0110') || str.contains('0220')) {
      return OPEN_TWO_SCORE;
    }

    if (str.contains('011') || str.contains('110') ||
        str.contains('022') || str.contains('220')) {
      return TWO_SCORE;
    }

    return 0;
  }

  static int _getCenterBonus(int row, int col) {
    int center = Board.SIZE ~/ 2;
    int distance = (row - center).abs() + (col - center).abs();
    return CENTER_BONUS - distance;
  }

  static List<List<int>> getCandidates(Board board) {
    Set<String> candidateSet = {};

    for (int i = 0; i < Board.SIZE; i++) {
      for (int j = 0; j < Board.SIZE; j++) {
        if (board.getCell(i, j) != 0) {
          for (int dr = -2; dr <= 2; dr++) {
            for (int dc = -2; dc <= 2; dc++) {
              int nr = i + dr;
              int nc = j + dc;
              if (nr >= 0 && nr < Board.SIZE && nc >= 0 && nc < Board.SIZE) {
                if (board.isEmpty(nr, nc)) {
                  candidateSet.add('$nr,$nc');
                }
              }
            }
          }
        }
      }
    }

    List<List<int>> candidates = [];
    for (var key in candidateSet) {
      var parts = key.split(',');
      int row = int.parse(parts[0]);
      int col = int.parse(parts[1]);
      if (!ForbiddenMoves.isForbidden(board, row, col)) {
        candidates.add([row, col]);
      }
    }

    if (candidates.isEmpty) {
      candidates.add([Board.SIZE ~/ 2, Board.SIZE ~/ 2]);
    }

    return candidates;
  }
}
