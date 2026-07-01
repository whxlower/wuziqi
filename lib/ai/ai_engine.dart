import 'dart:async';
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
        return 4;
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
}
