import '../logic/board.dart';
import '../logic/rules.dart';

class PatternType {
  static const int NONE = 0;
  static const int ONE = 1;
  static const int SLEEP_TWO = 2;
  static const int LIVE_TWO = 3;
  static const int SLEEP_THREE = 4;
  static const int LIVE_THREE = 5;
  static const int SLEEP_FOUR = 6;
  static const int LIVE_FOUR = 7;
  static const int FIVE = 8;
  static const int DOUBLE_LIVE_THREE = 9;
  static const int LIVE_THREE_AND_LIVE_TWO = 10;
  static const int DOUBLE_LIVE_TWO = 11;
  static const int CHONG_FOUR = 12;
}

class PatternResult {
  final int type;
  final int count;
  final int leftOpen;
  final int rightOpen;

  PatternResult(this.type, this.count, this.leftOpen, this.rightOpen);

  bool get isLiveFour => type == PatternType.LIVE_FOUR;
  bool get isLiveThree => type == PatternType.LIVE_THREE;
  bool get isLiveTwo => type == PatternType.LIVE_TWO;
  bool get isChongFour => type == PatternType.CHONG_FOUR;
}

class Evaluation {
  static const int WIN_SCORE = 1000000;
  static const int LIVE_FOUR = 100000;
  static const int CHONG_FOUR = 50000;
  static const int LIVE_THREE = 10000;
  static const int DOUBLE_LIVE_THREE = 50000;
  static const int SLEEP_THREE = 3000;
  static const int LIVE_TWO = 1000;
  static const int DOUBLE_LIVE_TWO = 5000;
  static const int SLEEP_TWO = 300;
  static const int ONE = 50;
  static const int CENTER_BONUS = 10;

  static int evaluate(Board board, int player) {
    int score = 0;
    int opponent = player == 1 ? 2 : 1;

    score += _evaluatePlayer(board, player);
    score -= _evaluatePlayer(board, opponent);

    return score;
  }

  static int _evaluatePlayer(Board board, int player) {
    int score = 0;

    Map<int, int> patternCounts = {
      PatternType.FIVE: 0,
      PatternType.LIVE_FOUR: 0,
      PatternType.CHONG_FOUR: 0,
      PatternType.LIVE_THREE: 0,
      PatternType.SLEEP_THREE: 0,
      PatternType.LIVE_TWO: 0,
      PatternType.SLEEP_TWO: 0,
    };

    Set<String> evaluatedPositions = {};

    for (int i = 0; i < Board.SIZE; i++) {
      for (int j = 0; j < Board.SIZE; j++) {
        if (board.getCell(i, j) == player) {
          for (var dir in Rules.DIRECTIONS) {
            String key = '$i,$j,${dir[0]},${dir[1]}';
            if (evaluatedPositions.contains(key)) continue;
            evaluatedPositions.add(key);

            PatternResult result = analyzePattern(testBoard, i, j, dir, player);
            patternCounts[result.type] = (patternCounts[result.type] ?? 0) + 1;
          }
        }
      }
    }

    if (patternCounts[PatternType.FIVE]! > 0) return WIN_SCORE;
    if (patternCounts[PatternType.LIVE_FOUR]! > 0) return LIVE_FOUR;

    score += patternCounts[PatternType.CHONG_FOUR]! * CHONG_FOUR;

    if (patternCounts[PatternType.LIVE_THREE]! >= 2) {
      score += DOUBLE_LIVE_THREE;
    } else {
      score += patternCounts[PatternType.LIVE_THREE]! * LIVE_THREE;
    }

    score += patternCounts[PatternType.SLEEP_THREE]! * SLEEP_THREE;

    if (patternCounts[PatternType.LIVE_TWO]! >= 2) {
      score += DOUBLE_LIVE_TWO;
    } else {
      score += patternCounts[PatternType.LIVE_TWO]! * LIVE_TWO;
    }

    score += patternCounts[PatternType.SLEEP_TWO]! * SLEEP_TWO;

    return score;
  }

  static PatternResult analyzePattern(
    Board board,
    int row,
    int col,
    List<int> dir,
    int player,
  ) {
    int count = 1;
    int leftOpen = 0;
    int rightOpen = 0;

    int r = row - dir[0];
    int c = col - dir[1];
    while (r >= 0 && r < Board.SIZE && c >= 0 && c < Board.SIZE) {
      int cell = board.getCell(r, c);
      if (cell == player) {
        count++;
      } else if (cell == 0) {
        leftOpen = 1;
        break;
      } else {
        break;
      }
      r -= dir[0];
      c -= dir[1];
    }

    r = row + dir[0];
    c = col + dir[1];
    while (r >= 0 && r < Board.SIZE && c >= 0 && c < Board.SIZE) {
      int cell = board.getCell(r, c);
      if (cell == player) {
        count++;
      } else if (cell == 0) {
        rightOpen = 1;
        break;
      } else {
        break;
      }
      r += dir[0];
      c += dir[1];
    }

    int totalOpen = leftOpen + rightOpen;

    if (count >= 5) {
      return PatternResult(PatternType.FIVE, count, leftOpen, rightOpen);
    }

    if (count == 4) {
      if (totalOpen >= 1) {
        return PatternResult(PatternType.LIVE_FOUR, count, leftOpen, rightOpen);
      }
      return PatternResult(PatternType.SLEEP_FOUR, count, leftOpen, rightOpen);
    }

    if (count == 3) {
      if (totalOpen == 2) {
        return PatternResult(PatternType.LIVE_THREE, count, leftOpen, rightOpen);
      }
      if (totalOpen == 1) {
        return PatternResult(PatternType.SLEEP_THREE, count, leftOpen, rightOpen);
      }
      return PatternResult(PatternType.SLEEP_THREE, count, leftOpen, rightOpen);
    }

    if (count == 2) {
      if (totalOpen == 2) {
        return PatternResult(PatternType.LIVE_TWO, count, leftOpen, rightOpen);
      }
      if (totalOpen == 1) {
        return PatternResult(PatternType.SLEEP_TWO, count, leftOpen, rightOpen);
      }
      return PatternResult(PatternType.SLEEP_TWO, count, leftOpen, rightOpen);
    }

    return PatternResult(PatternType.ONE, count, leftOpen, rightOpen);
  }

  static int evaluateMove(Board board, int row, int col, int player) {
    if (!board.isEmpty(row, col)) return -1000000;

    int score = 0;
    int opponent = player == 1 ? 2 : 1;

    Board testBoard = board.clone();
    testBoard.placeStone(row, col);

    score += _evaluatePlayer(testBoard, player);

    Map<int, int> oppPatternCounts = {};
    for (var dir in Rules.DIRECTIONS) {
      PatternResult result = analyzePattern(board, row, col, dir, opponent);
      int type = result.type;
      oppPatternCounts[type] = (oppPatternCounts[type] ?? 0) + 1;
    }

    if (oppPatternCounts[PatternType.LIVE_FOUR] != null) {
      score += LIVE_FOUR;
    }
    if (oppPatternCounts[PatternType.CHONG_FOUR] != null) {
      score += CHONG_FOUR;
    }
    if (oppPatternCounts[PatternType.LIVE_THREE] != null) {
      score += LIVE_THREE;
    }

    int centerBonus = CENTER_BONUS - (row - 7).abs() - (col - 7).abs();
    score += centerBonus;

    return score;
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
      candidates.add([int.parse(parts[0]), int.parse(parts[1])]);
    }

    if (candidates.isEmpty) {
      candidates.add([Board.SIZE ~/ 2, Board.SIZE ~/ 2]);
    }

    return candidates;
  }

  static List<List<int>> openingBook = [
    [7, 7],
    [7, 8],
    [8, 7],
    [7, 6],
    [6, 7],
    [8, 8],
    [6, 6],
    [8, 6],
    [6, 8],
    [9, 7],
    [5, 7],
    [7, 9],
    [7, 5],
  ];

  static List<int> getOpeningMove(Board board) {
    int stoneCount = 0;
    for (int i = 0; i < Board.SIZE; i++) {
      for (int j = 0; j < Board.SIZE; j++) {
        if (board.getCell(i, j) != 0) stoneCount++;
      }
    }

    if (stoneCount <= 4) {
      for (var move in openingBook) {
        if (board.isEmpty(move[0], move[1])) {
          return move;
        }
      }
    }

    return [-1, -1];
  }
}
