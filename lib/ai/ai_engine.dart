import 'dart:isolate';
import '../logic/board.dart';
import '../logic/rules.dart';
import '../logic/forbidden_moves.dart';
import 'evaluation.dart';

enum Difficulty {
  easy,
  medium,
  hard,
}

class AIEngine {
  final Difficulty difficulty;
  final int aiPlayer;

  AIEngine({
    required this.difficulty,
    required this.aiPlayer,
  });

  int _getDepth() {
    switch (difficulty) {
      case Difficulty.easy:
        return 2;
      case Difficulty.medium:
        return 3;
      case Difficulty.hard:
        return 5;
    }
  }

  Future<List<int>> getBestMove(Board board) async {
    int depth = _getDepth();
    Map<String, dynamic> args = {
      'board': board.toJson(),
      'depth': depth,
      'aiPlayer': aiPlayer,
    };

    final result = await Isolate.run(() => _minimaxAsync(args));
    return result;
  }

  static List<int> _minimaxAsync(Map<String, dynamic> args) {
    Board board = Board.fromJson(args['board']);
    int depth = args['depth'];
    int aiPlayer = args['aiPlayer'];
    return _minimax(board, depth, -1000000, 1000000, aiPlayer);
  }

  static List<int> _minimax(
    Board board,
    int depth,
    int alpha,
    int beta,
    int player,
  ) {
    int winner = Rules.checkWin(board);
    if (depth == 0 || winner != 0) {
      int score = Evaluation.evaluate(board, player);
      return [-1, -1, score];
    }

    List<List<int>> candidates = Evaluation.getCandidates(board);
    if (candidates.isEmpty) {
      return [-1, -1, 0];
    }

    candidates.sort((a, b) {
      int scoreA = _quickScore(board, a[0], a[1], player);
      int scoreB = _quickScore(board, b[0], b[1], player);
      return scoreB - scoreA;
    });

    List<int> bestMove = candidates[0];
    int bestScore = player == 1 ? -1000000 : 1000000;

    for (var move in candidates) {
      if (ForbiddenMoves.isForbidden(board, move[0], move[1])) {
        continue;
      }

      Board newBoard = board.clone();
      newBoard.placeStone(move[0], move[1]);

      List<int> result = _minimax(newBoard, depth - 1, alpha, beta, player == 1 ? 2 : 1);

      if (player == 1) {
        if (result[2] > bestScore) {
          bestScore = result[2];
          bestMove = move;
        }
        alpha = alpha > bestScore ? alpha : bestScore;
      } else {
        if (result[2] < bestScore) {
          bestScore = result[2];
          bestMove = move;
        }
        beta = beta < bestScore ? beta : bestScore;
      }

      if (beta <= alpha) {
        break;
      }
    }

    return [...bestMove, bestScore];
  }

  static int _quickScore(Board board, int row, int col, int player) {
    int score = 0;
    int centerBonus = 15 - (row - 7).abs() - (col - 7).abs();
    score += centerBonus * 5;

    for (var dir in Rules.DIRECTIONS) {
      int count = 0;
      int empty = 0;

      for (int i = -4; i <= 4; i++) {
        int r = row + dir[0] * i;
        int c = col + dir[1] * i;
        if (r >= 0 && r < Board.SIZE && c >= 0 && c < Board.SIZE) {
          int cell = board.getCell(r, c);
          if (cell == player) count++;
          else if (cell == 0) empty++;
          else break;
        }
      }

      if (count >= 4) return 100000;
      if (count == 3 && empty >= 2) score += 1000;
      else if (count == 3 && empty >= 1) score += 500;
      else if (count == 2 && empty >= 2) score += 200;
      else if (count == 2 && empty >= 1) score += 100;
    }

    return score;
  }
}
