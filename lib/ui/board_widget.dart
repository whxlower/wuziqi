import 'package:flutter/material.dart';
import '../logic/board.dart';
import '../logic/rules.dart';
import '../logic/forbidden_moves.dart';

class BoardWidget extends StatelessWidget {
  final Board board;
  final List<List<int>> winningLine;
  final bool showForbidden;
  final Function(int, int) onTap;

  const BoardWidget({
    super.key,
    required this.board,
    required this.winningLine,
    this.showForbidden = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        double size = constraints.maxWidth;
        return GestureDetector(
          onTapUp: (details) {
            double dx = details.localPosition.dx;
            double dy = details.localPosition.dy;
            double cellSize = size / (Board.SIZE - 1);
            int col = (dx / cellSize).round().clamp(0, Board.SIZE - 1);
            int row = (dy / cellSize).round().clamp(0, Board.SIZE - 1);
            onTap(row, col);
          },
          child: CustomPaint(
            size: Size(size, size),
            painter: BoardPainter(
              board: board,
              winningLine: winningLine,
              showForbidden: showForbidden,
            ),
          ),
        );
      },
    );
  }
}

class BoardPainter extends CustomPainter {
  final Board board;
  final List<List<int>> winningLine;
  final bool showForbidden;

  BoardPainter({
    required this.board,
    required this.winningLine,
    required this.showForbidden,
  });

  @override
  void paint(Canvas canvas, Size size) {
    double cellSize = size.width / (Board.SIZE - 1);

    Paint linePaint = Paint()
      ..color = Colors.black
      ..strokeWidth = 1.0;

    for (int i = 0; i < Board.SIZE; i++) {
      canvas.drawLine(
        Offset(0, i * cellSize),
        Offset(size.width, i * cellSize),
        linePaint,
      );
      canvas.drawLine(
        Offset(i * cellSize, 0),
        Offset(i * cellSize, size.height),
        linePaint,
      );
    }

    Paint starPaint = Paint()..color = Colors.black;
    List<List<int>> starPoints = [
      [3, 3], [3, 7], [3, 11],
      [7, 3], [7, 7], [7, 11],
      [11, 3], [11, 7], [11, 11],
    ];
    for (var point in starPoints) {
      canvas.drawCircle(
        Offset(point[1] * cellSize, point[0] * cellSize),
        4.0,
        starPaint,
      );
    }

    if (showForbidden) {
      Paint forbiddenPaint = Paint()
        ..color = Colors.red.withOpacity(0.5)
        ..style = PaintingStyle.fill;
      for (int i = 0; i < Board.SIZE; i++) {
        for (int j = 0; j < Board.SIZE; j++) {
          if (board.isEmpty(i, j) && ForbiddenMoves.isForbidden(board, i, j)) {
            canvas.drawCircle(
              Offset(j * cellSize, i * cellSize),
              cellSize * 0.3,
              forbiddenPaint,
            );
          }
        }
      }
    }

    for (int i = 0; i < Board.SIZE; i++) {
      for (int j = 0; j < Board.SIZE; j++) {
        int stone = board.getCell(i, j);
        if (stone != 0) {
          bool isWinning = winningLine.any((p) => p[0] == i && p[1] == j);
          _drawStone(canvas, i, j, cellSize, stone, isWinning);
        }
      }
    }

    if (board.lastMove[0] != -1) {
      int row = board.lastMove[0];
      int col = board.lastMove[1];
      Paint lastMovePaint = Paint()
        ..color = board.getCell(row, col) == 1 ? Colors.white : Colors.black
        ..style = PaintingStyle.fill;
      canvas.drawCircle(
        Offset(col * cellSize, row * cellSize),
        4.0,
        lastMovePaint,
      );
    }
  }

  void _drawStone(
    Canvas canvas,
    int row,
    int col,
    double cellSize,
    int player,
    bool isWinning,
  ) {
    Offset center = Offset(col * cellSize, row * cellSize);
    double radius = cellSize * 0.42;

    Paint paint = Paint();
    if (player == 1) {
      paint.color = Colors.black;
    } else {
      paint.color = Colors.white;
      paint.style = PaintingStyle.fill;
    }

    canvas.drawCircle(center, radius, paint);

    if (player == 2) {
      Paint borderPaint = Paint()
        ..color = Colors.black
        ..strokeWidth = 1.5
        ..style = PaintingStyle.stroke;
      canvas.drawCircle(center, radius, borderPaint);
    }

    if (isWinning) {
      Paint winningPaint = Paint()
        ..color = Colors.red
        ..strokeWidth = 3.0;
      canvas.drawCircle(center, radius * 0.6, winningPaint);
    }
  }

  @override
  bool shouldRepaint(covariant BoardPainter oldDelegate) {
    return board != oldDelegate.board ||
        winningLine != oldDelegate.winningLine ||
        showForbidden != oldDelegate.showForbidden;
  }
}
