class Board {
  static const int SIZE = 15;
  final List<List<int>> _grid;
  int _currentPlayer;
  List<int> _lastMove;
  List<List<int>> _history;

  Board()
      : _grid = List.generate(SIZE, (_) => List.filled(SIZE, 0)),
        _currentPlayer = 1,
        _lastMove = [-1, -1],
        _history = [];

  Board.fromState(
    List<List<int>> grid,
    int currentPlayer,
    List<int> lastMove,
    List<List<int>> history,
  )   : _grid = grid,
        _currentPlayer = currentPlayer,
        _lastMove = lastMove,
        _history = history;

  int get currentPlayer => _currentPlayer;

  List<int> get lastMove => _lastMove;

  List<List<int>> get history => _history;

  int getCell(int row, int col) {
    if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) {
      return 0;
    }
    return _grid[row][col];
  }

  bool isEmpty(int row, int col) {
    return getCell(row, col) == 0;
  }

  bool placeStone(int row, int col) {
    if (!isEmpty(row, col)) {
      return false;
    }
    _grid[row][col] = _currentPlayer;
    _lastMove = [row, col];
    _history.add([row, col, _currentPlayer]);
    _currentPlayer = _currentPlayer == 1 ? 2 : 1;
    return true;
  }

  void undo() {
    if (_history.isEmpty) {
      return;
    }
    var last = _history.removeLast();
    _grid[last[0]][last[1]] = 0;
    _currentPlayer = last[2];
    _lastMove = _history.isEmpty ? [-1, -1] : [_history.last[0], _history.last[1]];
  }

  void reset() {
    for (var i = 0; i < SIZE; i++) {
      for (var j = 0; j < SIZE; j++) {
        _grid[i][j] = 0;
      }
    }
    _currentPlayer = 1;
    _lastMove = [-1, -1];
    _history = [];
  }

  void setPlayer(int player) {
    _currentPlayer = player;
  }

  Board clone() {
    return Board.fromState(
      _grid.map((row) => List<int>.from(row)).toList(),
      _currentPlayer,
      List<int>.from(_lastMove),
      _history.map((h) => List<int>.from(h)).toList(),
    );
  }

  bool isFull() {
    for (var i = 0; i < SIZE; i++) {
      for (var j = 0; j < SIZE; j++) {
        if (_grid[i][j] == 0) {
          return false;
        }
      }
    }
    return true;
  }
}
