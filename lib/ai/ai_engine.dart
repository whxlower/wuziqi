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
        return 4;
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
        return 12;
    }
  }

  Future<List<int>> getBestMove(Board board) async {
    int opponent = aiPlayer == 1 ? 2 : 1;

    List<List<int>> candidates = Evaluation.getCandidates(board);
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

    List<int> liveFourMove = _findPatternMove(board, candidates, aiPlayer, Evaluation.PatternType.LIVE_FOUR);
    if (liveFourMove.isNotEmpty) {
      return [liveFourMove[0], liveFourMove[1], 999998];
    }

    List<int> blockLiveFourMove = _findPatternMove(board, candidates, opponent, Evaluation.PatternType.LIVE_FOUR);
    if (blockLiveFourMove.isNotEmpty) {
      return [blockLiveFourMove[0], blockLiveFourMove[1], 999997];
    }

    List<int> doubleLiveThreeMove = _findDoubleLiveThree(board, candidates, aiPlayer);
    if (doubleLiveThreeMove.isNotEmpty) {
      return [doubleLiveThreeMove[0], doubleLiveThreeMove[1], 999996];
    }

    List<int> blockDoubleLiveThreeMove = _findDoubleLiveThree(board, candidates, opponent);
    if (blockDoubleLiveThreeMove.isNotEmpty) {
      return [blockDoubleLiveThreeMove[0], blockDoubleLiveThreeMove[1], 999995];
    }

    List<int> liveThreeMove = _findPatternMove(board, candidates, aiPlayer, Evaluation.PatternType.LIVE_THREE);
    if (liveThreeMove.isNotEmpty) {
      return [liveThreeMove[0], liveThreeMove[1], 100000];
    }

    List<int> blockLiveThreeMove = _findPatternMove(board, candidates, opponent, Evaluation.PatternType.LIVE_THREE);
    if (blockLiveThreeMove.isNotEmpty) {
      return [blockLiveThreeMove[0], blockLiveThreeMove[1], 99000];
    }

    List<int> openingMove = Evaluation.getOpeningMove(board);
    if (openingMove[0] != -1 && board.isEmpty(openingMove[0], openingMove[1])) {
      return [openingMove[0], openingMove[1], 50000];
    }

    int depth = _getDepth();
    int candidateLimit = _getCandidateLimit();
    Map<String, dynamic> args = {
      'board': board.toJson(),
      'depth': depth,
      'aiPlayer': aiPlayer,
      'candidates': candidates,
      'candidateLimit': candidateLimit,
    };

    try {
      final result = await Isolate.run(() => _minimaxAsync(args)).timeout(
        const Duration(seconds: 10),
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

      Map<int, int> patternCounts = {};
      Set<String> evaluatedPositions = {};

      for (int i = 0; i < Board.SIZE; i++) {
        for (int j = 0; j < Board.SIZE; j++) {
          if (testBoard.getCell(i, j) == player) {
            for (var dir in Rules.DIRECTIONS) {
              String key = '$i,$j,${dir[0]},${dir[1]}';
              if (evaluatedPositions.contains(key)) continue;
              evaluatedPositions.add(key);

              Evaluation.PatternResult result = Evaluation._analyzePattern(testBoard, i, j, dir, player);
              patternCounts[result.type] = (patternCounts[result.type] ?? 0) + 1;
            }
          }
        }
      }

      if (patternCounts[patternType] != null && patternCounts[patternType]! > 0) {
        return move;
      }
    }
    return [];
  }

  List<int> _findDoubleLiveThree(Board board, List<List<int>> candidates, int player) {
    for (var move in candidates) {
      Board testBoard = board.clone();
      testBoard.placeStone(move[0], move[1]);

      int liveThreeCount = 0;
      Set<String> evaluatedPositions = {};

      for (var dir in Rules.DIRECTIONS) {
        String key = '${move[0]},${move[1]},${dir[0]},${dir[1]}';
        if (evaluatedPositions.contains(key)) continue;
        evaluatedPositions.add(key);

        Evaluation.PatternResult result = Evaluation._analyzePattern(testBoard, move[0], move[1], dir, player);
        if (result.type == Evaluation.PatternType.LIVE_THREE) {
          liveThreeCount++;
        }
      }

      if (liveThreeCount >= 2) {
        return move;
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

  static List<int> _minimaxAsync(Map<String, dynamic> args) {
    Board board = Board.fromJson(args['board']);
    int depth = args['depth'];
    int aiPlayer = args['aiPlayer'];
    int candidateLimit = args['candidateLimit'];
    List<List<int>> candidates = [];
    if (args['candidates'] != null) {
      for (var c in args['candidates']) {
        candidates.add([c[0], c[1]]);
      }
    }
    return _minimax(board, depth, -1000000, 1000000, aiPlayer, candidates, candidateLimit);
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
      candidates = Evaluation.getCandidates(board);
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

      List<List<int>> newCandidates = Evaluation.getCandidates(newBoard);
      List<int> result = _minimax(newBoard, depth - 1, alpha, beta, player == 1 ? 2 : 1, newCandidates, candidateLimit);

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
