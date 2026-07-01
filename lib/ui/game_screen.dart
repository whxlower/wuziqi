import 'package:flutter/material.dart';
import '../logic/board.dart';
import '../logic/rules.dart';
import '../logic/forbidden_moves.dart';
import '../ai/ai_engine.dart';
import 'board_widget.dart';
import 'home_screen.dart';

class GameScreen extends StatefulWidget {
  final GameMode gameMode;
  final int playerColor;

  const GameScreen({
    super.key,
    required this.gameMode,
    this.playerColor = 1,
  });

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  late Board board;
  late AIEngine aiEngine;
  List<List<int>> winningLine = [];
  String result = '';
  bool isAIMoving = false;
  bool showForbidden = false;

  @override
  void initState() {
    super.initState();
    board = Board();
    int aiPlayer = widget.playerColor == 1 ? 2 : 1;
    aiEngine = AIEngine(
      difficulty: Difficulty.medium,
      aiPlayer: aiPlayer,
    );

    if (widget.gameMode == GameMode.pve && widget.playerColor == 2) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _aiMove();
      });
    }
  }

  Future<void> _aiMove() async {
    if (result.isNotEmpty) return;

    setState(() {
      isAIMoving = true;
    });

    List<int> move = await aiEngine.getBestMove(board);
    if (move[0] != -1) {
      setState(() {
        board.placeStone(move[0], move[1]);
        _checkWin();
      });
    }

    setState(() {
      isAIMoving = false;
    });
  }

  void _handleTap(int row, int col) {
    if (result.isNotEmpty || isAIMoving) return;
    if (!board.isEmpty(row, col)) return;

    if (widget.gameMode == GameMode.pve &&
        board.currentPlayer != widget.playerColor) {
      return;
    }

    if (board.currentPlayer == 1 && ForbiddenMoves.isForbidden(board, row, col)) {
      _showForbiddenWarning(ForbiddenMoves.getForbiddenType(board, row, col));
      return;
    }

    setState(() {
      board.placeStone(row, col);
      _checkWin();

      if (widget.gameMode == GameMode.pve && result.isEmpty) {
        _aiMove();
      }
    });
  }

  void _checkWin() {
    int winner = Rules.checkWin(board);
    if (winner != 0) {
      setState(() {
        winningLine = Rules.getWinningLine(board);
        if (winner == -1) {
          result = '平局！';
        } else {
          String winnerName = winner == 1 ? '黑棋' : '白棋';
          if (widget.gameMode == GameMode.pve) {
            bool isPlayerWin = winner == widget.playerColor;
            result = isPlayerWin ? '恭喜你获胜！' : 'AI获胜！';
          } else {
            result = '$winnerName获胜！';
          }
        }
      });
      _showResultDialog();
    }
  }

  void _showForbiddenWarning(String type) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('禁手'),
        content: Text('此位置属于$type，黑棋不能落子！'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('知道了'),
          ),
        ],
      ),
    );
  }

  void _showResultDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('游戏结束'),
        content: Text(result),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                board.reset();
                winningLine = [];
                result = '';
                if (widget.gameMode == GameMode.pve && widget.playerColor == 2) {
                  _aiMove();
                }
              });
            },
            child: const Text('再来一局'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('返回首页'),
          ),
        ],
      ),
    );
  }

  void _undo() {
    if (result.isNotEmpty || isAIMoving) return;

    setState(() {
      board.undo();
      if (widget.gameMode == GameMode.pve) {
        board.undo();
      }
      winningLine = [];
    });
  }

  void _reset() {
    setState(() {
      board.reset();
      winningLine = [];
      result = '';
      if (widget.gameMode == GameMode.pve && widget.playerColor == 2) {
        _aiMove();
      }
    });
  }

  Widget _buildButtonBar() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          icon: const Icon(Icons.undo, size: 28),
          onPressed: _undo,
          tooltip: '悔棋',
        ),
        const SizedBox(height: 16),
        IconButton(
          icon: const Icon(Icons.refresh, size: 28),
          onPressed: _reset,
          tooltip: '重新开始',
        ),
        if (widget.gameMode == GameMode.pve) ...[
          const SizedBox(height: 16),
          IconButton(
            icon: Icon(
              showForbidden ? Icons.block : Icons.block_outlined,
              size: 28,
              color: showForbidden ? Colors.red : null,
            ),
            onPressed: () {
              setState(() {
                showForbidden = !showForbidden;
              });
            },
            tooltip: showForbidden ? '隐藏禁手' : '显示禁手',
          ),
        ],
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.gameMode == GameMode.pve ? '人机对战' : '人人对战',
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          bool isLandscape = constraints.maxWidth > constraints.maxHeight;
          
          if (isLandscape) {
            return Row(
              children: [
                Expanded(
                  flex: 5,
                  child: Column(
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text('当前玩家：'),
                            const SizedBox(width: 8),
                            Container(
                              width: 20,
                              height: 20,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: board.currentPlayer == 1 ? Colors.black : Colors.white,
                                border: board.currentPlayer == 2
                                    ? Border.all(color: Colors.black, width: 2)
                                    : null,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(board.currentPlayer == 1 ? '黑棋' : '白棋'),
                          ],
                        ),
                      ),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.all(4),
                          child: BoardWidget(
                            board: board,
                            winningLine: winningLine,
                            showForbidden: showForbidden,
                            onTap: _handleTap,
                          ),
                        ),
                      ),
                      Visibility(
                        visible: isAIMoving,
                        maintainSize: true,
                        maintainAnimation: true,
                        maintainState: true,
                        child: const Padding(
                          padding: EdgeInsets.only(bottom: 8),
                          child: CircularProgressIndicator(),
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 60,
                  color: Colors.grey[100],
                  child: _buildButtonBar(),
                ),
              ],
            );
          } else {
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text('当前玩家：'),
                      const SizedBox(width: 8),
                      Container(
                        width: 20,
                        height: 20,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: board.currentPlayer == 1 ? Colors.black : Colors.white,
                          border: board.currentPlayer == 2
                              ? Border.all(color: Colors.black, width: 2)
                              : null,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(board.currentPlayer == 1 ? '黑棋' : '白棋'),
                    ],
                  ),
                ),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(4),
                    child: BoardWidget(
                      board: board,
                      winningLine: winningLine,
                      showForbidden: showForbidden,
                      onTap: _handleTap,
                    ),
                  ),
                ),
                Container(
                  height: 60,
                  color: Colors.grey[100],
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.undo, size: 28),
                        onPressed: _undo,
                        tooltip: '悔棋',
                      ),
                      const SizedBox(width: 20),
                      IconButton(
                        icon: const Icon(Icons.refresh, size: 28),
                        onPressed: _reset,
                        tooltip: '重新开始',
                      ),
                      if (widget.gameMode == GameMode.pve) ...[
                        const SizedBox(width: 20),
                        IconButton(
                          icon: Icon(
                            showForbidden ? Icons.block : Icons.block_outlined,
                            size: 28,
                            color: showForbidden ? Colors.red : null,
                          ),
                          onPressed: () {
                            setState(() {
                              showForbidden = !showForbidden;
                            });
                          },
                          tooltip: showForbidden ? '隐藏禁手' : '显示禁手',
                        ),
                      ],
                    ],
                  ),
                ),
                Visibility(
                  visible: isAIMoving,
                  maintainSize: true,
                  maintainAnimation: true,
                  maintainState: true,
                  child: const Padding(
                    padding: EdgeInsets.only(bottom: 8),
                    child: CircularProgressIndicator(),
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }
}
