import 'package:shared_preferences/shared_preferences.dart';

class Player {
  final String id;
  final String name;
  final int wins;
  final int losses;
  final int draws;

  Player({
    required this.id,
    required this.name,
    this.wins = 0,
    this.losses = 0,
    this.draws = 0,
  });

  Player copyWith({
    String? id,
    String? name,
    int? wins,
    int? losses,
    int? draws,
  }) {
    return Player(
      id: id ?? this.id,
      name: name ?? this.name,
      wins: wins ?? this.wins,
      losses: losses ?? this.losses,
      draws: draws ?? this.draws,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'wins': wins,
      'losses': losses,
      'draws': draws,
    };
  }

  factory Player.fromJson(Map<String, dynamic> json) {
    return Player(
      id: json['id'],
      name: json['name'],
      wins: json['wins'] ?? 0,
      losses: json['losses'] ?? 0,
      draws: json['draws'] ?? 0,
    );
  }

  double get winRate {
    int total = wins + losses + draws;
    if (total == 0) return 0;
    return wins / total;
  }
}

class GameRecord {
  final String id;
  final String playerId;
  final String playerName;
  final String aiDifficulty;
  final int playerColor;
  final String result;
  final int duration;
  final DateTime date;

  GameRecord({
    required this.id,
    required this.playerId,
    required this.playerName,
    required this.aiDifficulty,
    required this.playerColor,
    required this.result,
    required this.duration,
    required this.date,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'playerId': playerId,
      'playerName': playerName,
      'aiDifficulty': aiDifficulty,
      'playerColor': playerColor,
      'result': result,
      'duration': duration,
      'date': date.toIso8601String(),
    };
  }

  factory GameRecord.fromJson(Map<String, dynamic> json) {
    return GameRecord(
      id: json['id'],
      playerId: json['playerId'],
      playerName: json['playerName'],
      aiDifficulty: json['aiDifficulty'],
      playerColor: json['playerColor'],
      result: json['result'],
      duration: json['duration'],
      date: DateTime.parse(json['date']),
    );
  }
}

class StorageManager {
  static const String _playersKey = 'gomoku_players';
  static const String _recordsKey = 'gomoku_records';
  static const String _currentPlayerKey = 'gomoku_current_player';

  static Future<SharedPreferences> _getPrefs() async {
    return await SharedPreferences.getInstance();
  }

  static Future<List<Player>> getPlayers() async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_playersKey);
    if (jsonString == null) {
      return [Player(id: '1', name: '玩家', wins: 0, losses: 0, draws: 0)];
    }
    final List<dynamic> jsonList = await Future.microtask(() =>
        _decodeJson(jsonString));
    return jsonList.map((e) => Player.fromJson(e)).toList();
  }

  static Future<void> savePlayers(List<Player> players) async {
    final prefs = await _getPrefs();
    final jsonString = _encodeJson(players.map((p) => p.toJson()).toList());
    await prefs.setString(_playersKey, jsonString);
  }

  static Future<void> addPlayer(String name) async {
    final players = await getPlayers();
    final newPlayer = Player(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: name,
    );
    players.add(newPlayer);
    await savePlayers(players);
  }

  static Future<void> deletePlayer(String playerId) async {
    final players = await getPlayers();
    players.removeWhere((p) => p.id == playerId);
    if (players.isEmpty) {
      players.add(Player(id: '1', name: '玩家'));
    }
    await savePlayers(players);
    final currentPlayerId = await getCurrentPlayerId();
    if (currentPlayerId == playerId) {
      await setCurrentPlayerId(players.first.id);
    }
    final records = await getRecords();
    final filtered = records.where((r) => r.playerId != playerId).toList();
    await saveRecords(filtered);
  }

  static Future<void> updatePlayer(Player player) async {
    final players = await getPlayers();
    final index = players.indexWhere((p) => p.id == player.id);
    if (index != -1) {
      players[index] = player;
      await savePlayers(players);
    }
  }

  static Future<String> getCurrentPlayerId() async {
    final prefs = await _getPrefs();
    final players = await getPlayers();
    final id = prefs.getString(_currentPlayerKey);
    if (id != null && players.any((p) => p.id == id)) {
      return id;
    }
    return players.first.id;
  }

  static Future<void> setCurrentPlayerId(String playerId) async {
    final prefs = await _getPrefs();
    await prefs.setString(_currentPlayerKey, playerId);
  }

  static Future<List<GameRecord>> getRecords() async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_recordsKey);
    if (jsonString == null) return [];
    final List<dynamic> jsonList = await Future.microtask(() =>
        _decodeJson(jsonString));
    return jsonList.map((e) => GameRecord.fromJson(e)).toList()
      ..sort((a, b) => b.date.compareTo(a.date));
  }

  static Future<List<GameRecord>> getRecordsByPlayer(String playerId) async {
    final records = await getRecords();
    return records.where((r) => r.playerId == playerId).toList();
  }

  static Future<void> saveRecords(List<GameRecord> records) async {
    final prefs = await _getPrefs();
    final jsonString = _encodeJson(records.map((r) => r.toJson()).toList());
    await prefs.setString(_recordsKey, jsonString);
  }

  static Future<void> addRecord(GameRecord record) async {
    final records = await getRecords();
    records.insert(0, record);
    if (records.length > 100) {
      records.removeRange(100, records.length);
    }
    await saveRecords(records);
    await updatePlayerStats(record);
  }

  static Future<void> clearRecords() async {
    final prefs = await _getPrefs();
    await prefs.remove(_recordsKey);
    final players = await getPlayers();
    for (var player in players) {
      await updatePlayer(player.copyWith(wins: 0, losses: 0, draws: 0));
    }
  }

  static Future<void> updatePlayerStats(GameRecord record) async {
    final players = await getPlayers();
    final index = players.indexWhere((p) => p.id == record.playerId);
    if (index != -1) {
      final player = players[index];
      Player updated;
      switch (record.result) {
        case 'win':
          updated = player.copyWith(wins: player.wins + 1);
          break;
        case 'loss':
          updated = player.copyWith(losses: player.losses + 1);
          break;
        default:
          updated = player.copyWith(draws: player.draws + 1);
          break;
      }
      players[index] = updated;
      await savePlayers(players);
    }
  }

  static dynamic _decodeJson(String jsonString) {
    try {
      return _parseJson(jsonString);
    } catch (_) {
      return [];
    }
  }

  static String _encodeJson(dynamic value) {
    try {
      return _stringifyJson(value);
    } catch (_) {
      return '[]';
    }
  }

  static dynamic _parseJson(String source) {
    const int maxDepth = 100;
    int depth = 0;
    List<dynamic> stack = [];
    String currentString = '';
    bool inString = false;
    String? escapeChar;

    for (int i = 0; i < source.length; i++) {
      final char = source[i];

      if (escapeChar != null) {
        currentString += char;
        escapeChar = null;
        continue;
      }

      if (char == '\\' && inString) {
        escapeChar = '\\';
        continue;
      }

      if (char == '"') {
        inString = !inString;
        continue;
      }

      if (!inString) {
        if (char == '[' || char == '{') {
          depth++;
          if (depth > maxDepth) return [];
          stack.add(char == '[' ? [] : {});
          continue;
        }

        if (char == ']' || char == '}') {
          depth--;
          final current = stack.removeLast();
          if (stack.isEmpty) return current;
          final parent = stack.last;
          if (parent is List) {
            parent.add(current is String && currentString.isNotEmpty ? currentString : current);
          } else if (parent is Map) {
            parent[currentString] = current;
          }
          currentString = '';
          continue;
        }

        if (char == ':') {
          continue;
        }

        if (char == ',') {
          if (stack.last is List) {
            (stack.last as List).add(_parseValue(currentString));
          }
          currentString = '';
          continue;
        }
      }

      currentString += char;
    }

    return stack.isEmpty ? _parseValue(currentString) : stack.last;
  }

  static dynamic _parseValue(String value) {
    value = value.trim();
    if (value == 'null') return null;
    if (value == 'true') return true;
    if (value == 'false') return false;
    if (value.startsWith('"') && value.endsWith('"')) {
      return value.substring(1, value.length - 1);
    }
    final numValue = num.tryParse(value);
    if (numValue != null) return numValue;
    return value;
  }

  static String _stringifyJson(dynamic value) {
    if (value == null) return 'null';
    if (value is bool) return value ? 'true' : 'false';
    if (value is num) return value.toString();
    if (value is String) {
      String escaped = value
          .replaceAll('\\', '\\\\')
          .replaceAll('"', '\\"')
          .replaceAll('\n', '\\n')
          .replaceAll('\r', '\\r');
      return '"$escaped"';
    }
    if (value is List) {
      return '[${value.map(_stringifyJson).join(',')}]';
    }
    if (value is Map) {
      return '{${value.entries.map((e) => '"${e.key}":${_stringifyJson(e.value)}').join(',')}}';
    }
    return 'null';
  }
}
