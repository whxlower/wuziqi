import 'dart:convert';
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
      id: json['id'] ?? '',
      name: json['name'] ?? '',
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
      id: json['id'] ?? '',
      playerId: json['playerId'] ?? '',
      playerName: json['playerName'] ?? '',
      aiDifficulty: json['aiDifficulty'] ?? '',
      playerColor: json['playerColor'] ?? 1,
      result: json['result'] ?? '',
      duration: json['duration'] ?? 0,
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
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
    try {
      final prefs = await _getPrefs();
      final jsonString = prefs.getString(_playersKey);
      if (jsonString == null || jsonString.isEmpty) {
        return [Player(id: '1', name: '玩家', wins: 0, losses: 0, draws: 0)];
      }
      final List<dynamic> jsonList = json.decode(jsonString);
      return jsonList.map((e) => Player.fromJson(e)).toList();
    } catch (e) {
      return [Player(id: '1', name: '玩家', wins: 0, losses: 0, draws: 0)];
    }
  }

  static Future<void> savePlayers(List<Player> players) async {
    try {
      final prefs = await _getPrefs();
      final jsonString = json.encode(players.map((p) => p.toJson()).toList());
      await prefs.setString(_playersKey, jsonString);
    } catch (e) {
      print('Failed to save players: $e');
    }
  }

  static Future<void> addPlayer(String name) async {
    try {
      final players = await getPlayers();
      final newPlayer = Player(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: name,
      );
      players.add(newPlayer);
      await savePlayers(players);
    } catch (e) {
      print('Failed to add player: $e');
    }
  }

  static Future<void> deletePlayer(String playerId) async {
    try {
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
    } catch (e) {
      print('Failed to delete player: $e');
    }
  }

  static Future<void> updatePlayer(Player player) async {
    try {
      final players = await getPlayers();
      final index = players.indexWhere((p) => p.id == player.id);
      if (index != -1) {
        players[index] = player;
        await savePlayers(players);
      }
    } catch (e) {
      print('Failed to update player: $e');
    }
  }

  static Future<String> getCurrentPlayerId() async {
    try {
      final prefs = await _getPrefs();
      final players = await getPlayers();
      final id = prefs.getString(_currentPlayerKey);
      if (id != null && players.any((p) => p.id == id)) {
        return id;
      }
      return players.first.id;
    } catch (e) {
      return '1';
    }
  }

  static Future<void> setCurrentPlayerId(String playerId) async {
    try {
      final prefs = await _getPrefs();
      await prefs.setString(_currentPlayerKey, playerId);
    } catch (e) {
      print('Failed to set current player: $e');
    }
  }

  static Future<List<GameRecord>> getRecords() async {
    try {
      final prefs = await _getPrefs();
      final jsonString = prefs.getString(_recordsKey);
      if (jsonString == null || jsonString.isEmpty) return [];
      final List<dynamic> jsonList = json.decode(jsonString);
      return jsonList.map((e) => GameRecord.fromJson(e)).toList()
        ..sort((a, b) => b.date.compareTo(a.date));
    } catch (e) {
      return [];
    }
  }

  static Future<List<GameRecord>> getRecordsByPlayer(String playerId) async {
    final records = await getRecords();
    return records.where((r) => r.playerId == playerId).toList();
  }

  static Future<void> saveRecords(List<GameRecord> records) async {
    try {
      final prefs = await _getPrefs();
      final jsonString = json.encode(records.map((r) => r.toJson()).toList());
      await prefs.setString(_recordsKey, jsonString);
    } catch (e) {
      print('Failed to save records: $e');
    }
  }

  static Future<void> addRecord(GameRecord record) async {
    try {
      final records = await getRecords();
      records.insert(0, record);
      if (records.length > 100) {
        records.removeRange(100, records.length);
      }
      await saveRecords(records);
      await updatePlayerStats(record);
    } catch (e) {
      print('Failed to add record: $e');
    }
  }

  static Future<void> clearRecords() async {
    try {
      final prefs = await _getPrefs();
      await prefs.remove(_recordsKey);
      final players = await getPlayers();
      for (var player in players) {
        await updatePlayer(player.copyWith(wins: 0, losses: 0, draws: 0));
      }
    } catch (e) {
      print('Failed to clear records: $e');
    }
  }

  static Future<void> updatePlayerStats(GameRecord record) async {
    try {
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
    } catch (e) {
      print('Failed to update player stats: $e');
    }
  }
}
