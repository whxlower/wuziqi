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

  int _getMaxDepth() {
    switch (difficulty) {
      case Difficulty.easy:
        return 2;
      case Difficulty.medium:
        return 3;
      case Difficulty.hard:
        return 5;
    }
  }

  int _getCandidateLimit() {
    switch (difficulty) {
      case Difficulty.easy:
        return 5;
      case Difficulty.medium:
        return 8;
      case Difficulty.hard:
        return 15;
    }
  }

  Future<List<int>> getBestMove(Board board) async {
    int opponent = aiPlayer == 1 ? 2 : 1;

    List<List<int>> candidates = Evaluation.getCandidates(board, radius: 3);
    candidates.removeWhere((m) => ForbiddenMoves.isForbidden(board, m[0], m[1]));

    if (candidates.isEmpty) {
      return _getFallbackMove(board);
    }

    List<int> winMove = _findWinningMove(board, candidates, aiPlayer);
    if (winMove.isNotEmpty) {
      return [winMove[0], winMove[1], 1000000];
    }

    List<int> blockMove = _findWinningMove(board, candidates, opponent);
    if (blockMove.isNotEmpty) {
      return [blockMove[0], blockMove[1], 999999];
    }

    List<int> liveFourMove = _findPatternMove(board, candidates, aiPlayer, PatternType.LIVE_FOUR);
    if (liveFourMove.isNotEmpty) {
      return [liveFourMove[0], liveFourMove[1], 999998];
    }

    List<int> blockLiveFourMove = _findPatternMove(board, candidates, opponent, PatternType.LIVE_FOUR);
    if (blockLiveFourMove.isNotEmpty) {
      return [blockLiveFourMove[0], blockLiveFourMove[1], 999997];
    }

    List<int> chongFourMove = _findPatternMove(board, candidates, aiPlayer, PatternType.CHONG_FOUR);
    if (chongFourMove.isNotEmpty) {
      return [chongFourMove[0], chongFourMove[1], 999996];
    }

    List<int> blockChongFourMove = _findPatternMove(board, candidates, opponent, PatternType.CHONG_FOUR);
    if (blockChongFourMove.isNotEmpty) {
      return [blockChongFourMove[0], blockChongFourMove[1], 999995];
    }

    List<int> liveThreeMove = _findPatternMove(board, candidates, aiPlayer, PatternType.LIVE_THREE);
    if (liveThreeMove.isNotEmpty) {
      return [liveThreeMove[0], liveThreeMove[1], 100000];
    }

    List<int> blockLiveThreeMove = _findPatternMove(board, candidates, opponent, PatternType.LIVE_THREE);
    if (blockLiveThreeMove.isNotEmpty) {
      return [blockLiveThreeMove[0], blockLiveThreeMove[1], 99000];
    }

    List<int> openingMove = Evaluation.getOpeningMove(board);
    if (openingMove[0] != -1 && board.isEmpty(openingMove[0], openingMove[1])) {
      return [openingMove[0], openingMove[1], 50000];
    }

    int maxDepth = _getMaxDepth();
    int candidateLimit = _getCandidateLimit();
    Map<String, dynamic> args = {
      'board': board.toJson(),
      'maxDepth': maxDepth,
      'aiPlayer': aiPlayer,
      'candidates': candidates,
      'candidateLimit': candidateLimit,
    };

    try {
      int timeoutSeconds = difficulty == Difficulty.hard ? 12 : 8;
      final result = await Isolate.run(() => _iterativeDeepening(args)).timeout(
        Duration(seconds: timeoutSeconds),
        onTimeout: () => [-1, -1, 0],
      );
      if (result[0] == -1) {
        return _getFallbackMove(board);
      }
      return result;
    } catch (_) {
      return _getFallbackMove(board);
    }
  }

  List<int> _findWinningMove(Board board, List<List<int>> candidates, int player) {
    for (var move in candidates) {
      Board testBoard = board.clone();
      testBoard.placeStone(move[0], move[1]);
      if (Rules.checkWin(testBoard) == player) {
        return move;
      }
    }
    return [];
  }

  List<int> _findPatternMove(Board board, List<List<int>> candidates, int player, int patternType) {
    for (var move in candidates) {
      Board testBoard = board.clone();
      testBoard.placeStone(move[0], move[1]);

      Set<String> evaluatedPositions = {};
      for (int i = 0; i < Board.SIZE; i++) {
        for (int j = 0; j < Board.SIZE; j++) {
          if (testBoard.getCell(i, j) == player) {
            for (var dir in Rules.DIRECTIONS) {
              String key = '$i,$j,${dir[0]},${dir[1]}';
              if (evaluatedPositions.contains(key)) continue;
              evaluatedPositions.add(key);

              PatternResult result = Evaluation.analyzePattern(testBoard, i, j, dir, player);
              if (result.type == patternType) {
                return move;
              }
            }
          }
        }
      }
    }
    return [];
  }

  List<int> _getFallbackMove(Board board) {
    List<List<int>> candidates = Evaluation.getCandidates(board);
    candidates.removeWhere((m) => ForbiddenMoves.isForbidden(board, m[0], m[1]));

    if (candidates.isEmpty) {
      for (int i = 0; i < Board.SIZE; i++) {
        for (int j = 0; j < Board.SIZE; j++) {
          if (board.isEmpty(i, j)) {
            return [i, j];
          }
        }
      }
      return [-1, -1];
    }

    int bestScore = -1000000;
    List<int> bestMove = candidates[0];

    for (var move in candidates) {
      int score = Evaluation.evaluateMove(board, move[0], move[1], aiPlayer);
      if (score > bestScore) {
        bestScore = score;
        bestMove = move;
      }
    }

    return [bestMove[0], bestMove[1], bestScore];
  }

  static List<int> _iterativeDeepening(Map<String, dynamic> args) {
    Board board = Board.fromJson(args['board']);
    int maxDepth = args['maxDepth'];
    int aiPlayer = args['aiPlayer'];
    int candidateLimit = args['candidateLimit'];
    List<List<int>> candidates = [];
    if (args['candidates'] != null) {
      for (var c in args['candidates']) {
        candidates.add([c[0], c[1]]);
      }
    }

    List<int> bestMove = candidates.isNotEmpty ? candidates[0] : [-1, -1];
    int bestScore = -1000000;

    for (int depth = 1; depth <= maxDepth; depth++) {
      List<int> result = _minimax(board, depth, -1000000, 1000000, aiPlayer, candidates, candidateLimit);
      if (result[0] != -1) {
        bestMove = [result[0], result[1]];
        bestScore = result[2];

        if (bestScore >= 1000000) {
          break;
        }
      }
    }

    return [...bestMove, bestScore];
  }

  static List<int> _minimax(
    Board board,
    int depth,
    int alpha,
    int beta,
    int player,
    List<List<int>> candidates,
    int candidateLimit,
  ) {
    int winner = Rules.checkWin(board);
    if (depth == 0 || winner != 0) {
      int score = Evaluation.evaluate(board, player);
      if (winner == player) score += 1000000;
      else if (winner != 0 && winner != -1) score -= 1000000;
      return [-1, -1, score];
    }

    if (candidates.isEmpty) {
      candidates = Evaluation.getCandidates(board, radius: 2);
    }

    candidates.removeWhere((m) => ForbiddenMoves.isForbidden(board, m[0], m[1]));

    if (candidates.isEmpty) {
      return [-1, -1, 0];
    }

    candidates.sort((a, b) {
      int scoreA = Evaluation.evaluateMove(board, a[0], a[1], player);
      int scoreB = Evaluation.evaluateMove(board, b[0], b[1], player);
      return scoreB - scoreA;
    });

    if (candidates.length > candidateLimit) {
      candidates = candidates.take(candidateLimit).toList();
    }

    List<int> bestMove = candidates[0];
    int bestScore = player == 1 ? -1000000 : 1000000;

    for (var move in candidates) {
      Board newBoard = board.clone();
      newBoard.placeStone(move[0], move[1]);

      List<List<int>> newCandidates = Evaluation.getCandidates(newBoard, radius: 2);
      List<int> result = _minimax(newBoard, depth - 1, alpha, beta, player == 1 ? 2 : 1, newCandidates, candidateLimit);

      if (player == 1) {
        if (result[2] > bestScore) {
          bestScore = result[2];
          bestMove = move;
        }
        if (bestScore > alpha) {
          alpha = bestScore;
        }
      } else {
        if (result[2] < bestScore) {
          bestScore = result[2];
          bestMove = move;
        }
        if (bestScore < beta) {
          beta = bestScore;
        }
      }

      if (beta <= alpha) {
        break;
      }
    }

    return [...bestMove, bestScore];
  }
}
