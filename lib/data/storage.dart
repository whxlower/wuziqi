import 'package:shared_preferences/shared_preferences.dart';

class Storage {
  static const String _keyPlayerColor = 'player_color';
  static const String _keyDifficulty = 'difficulty';
  static const String _keyWinCount = 'win_count';
  static const String _keyLoseCount = 'lose_count';
  static const String _keyDrawCount = 'draw_count';

  static Future<void> setPlayerColor(int color) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_keyPlayerColor, color);
  }

  static Future<int> getPlayerColor() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_keyPlayerColor) ?? 1;
  }

  static Future<void> setDifficulty(String difficulty) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyDifficulty, difficulty);
  }

  static Future<String> getDifficulty() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyDifficulty) ?? 'medium';
  }

  static Future<void> incrementWinCount() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    int count = prefs.getInt(_keyWinCount) ?? 0;
    await prefs.setInt(_keyWinCount, count + 1);
  }

  static Future<int> getWinCount() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_keyWinCount) ?? 0;
  }

  static Future<void> incrementLoseCount() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    int count = prefs.getInt(_keyLoseCount) ?? 0;
    await prefs.setInt(_keyLoseCount, count + 1);
  }

  static Future<int> getLoseCount() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_keyLoseCount) ?? 0;
  }

  static Future<void> incrementDrawCount() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    int count = prefs.getInt(_keyDrawCount) ?? 0;
    await prefs.setInt(_keyDrawCount, count + 1);
  }

  static Future<int> getDrawCount() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_keyDrawCount) ?? 0;
  }

  static Future<void> resetStats() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_keyWinCount, 0);
    await prefs.setInt(_keyLoseCount, 0);
    await prefs.setInt(_keyDrawCount, 0);
  }
}
