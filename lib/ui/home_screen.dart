import 'package:flutter/material.dart';
import '../data/storage.dart';
import '../ai/ai_engine.dart';
import 'game_screen.dart';
import 'rule_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Player? currentPlayer;
  List<Player> players = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    players = await StorageManager.getPlayers();
    final currentId = await StorageManager.getCurrentPlayerId();
    currentPlayer = players.firstWhere((p) => p.id == currentId);
    setState(() {
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('五子棋'),
        centerTitle: true,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(height: 30),
                  const Text(
                    '五子棋',
                    style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: Colors.brown,
                    ),
                  ),
                  const SizedBox(height: 20),
                  if (currentPlayer != null)
                    InkWell(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => PlayerManagerScreen(
                              players: players,
                              currentPlayerId: currentPlayer!.id,
                              onChanged: (player) {
                                setState(() {
                                  currentPlayer = player;
                                });
                                _loadData();
                              },
                            ),
                          ),
                        );
                      },
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              width: 32,
                              height: 32,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.brown,
                              ),
                              child: const Icon(
                                Icons.person,
                                color: Colors.white,
                                size: 18,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Text(
                              '当前玩家：${currentPlayer!.name}',
                              style: const TextStyle(
                                fontSize: 16,
                                color: Colors.brown,
                              ),
                            ),
                            const Icon(Icons.arrow_forward, size: 16),
                          ],
                        ),
                      ),
                    ),
                  const SizedBox(height: 30),
                  SizedBox(
                    width: 220,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                        backgroundColor: Colors.brown,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => GameSettingsDialog(
                            player: currentPlayer!,
                          ),
                        );
                      },
                      child: const Text(
                        '人机对战',
                        style: TextStyle(fontSize: 20),
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  SizedBox(
                    width: 220,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                        backgroundColor: Colors.brown[700],
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const GameScreen(
                              gameMode: GameMode.pvp,
                            ),
                          ),
                        );
                      },
                      child: const Text(
                        '人人对战',
                        style: TextStyle(fontSize: 20),
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  SizedBox(
                    width: 220,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                        backgroundColor: Colors.blueGrey,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => RecordsScreen(
                              player: currentPlayer!,
                            ),
                          ),
                        );
                      },
                      child: const Text(
                        '历史战绩',
                        style: TextStyle(fontSize: 20),
                      ),
                    ),
                  ),
                  const SizedBox(height: 30),
                  SizedBox(
                    width: 200,
                    child: TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const RuleScreen(),
                          ),
                        );
                      },
                      child: const Text(
                        '禁手规则说明',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.brown,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class GameSettingsDialog extends StatefulWidget {
  final Player player;

  const GameSettingsDialog({
    super.key,
    required this.player,
  });

  @override
  State<GameSettingsDialog> createState() => _GameSettingsDialogState();
}

class _GameSettingsDialogState extends State<GameSettingsDialog> {
  Difficulty selectedDifficulty = Difficulty.medium;
  int selectedColor = 1;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('游戏设置'),
      content: SizedBox(
        width: 300,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 10),
            const Text(
              '选择难度',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildDifficultyButton(Difficulty.easy, '简单'),
                const SizedBox(width: 10),
                _buildDifficultyButton(Difficulty.medium, '中等'),
                const SizedBox(width: 10),
                _buildDifficultyButton(Difficulty.hard, '困难'),
              ],
            ),
            const SizedBox(height: 20),
            const Text(
              '选择棋子颜色',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                GestureDetector(
                  onTap: () {
                    setState(() {
                      selectedColor = 1;
                    });
                  },
                  child: Column(
                    children: [
                      Container(
                        width: 50,
                        height: 50,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.black,
                          border: selectedColor == 1
                              ? Border.all(color: Colors.blue, width: 3)
                              : null,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text('黑棋'),
                      const Text('(先手)'),
                    ],
                  ),
                ),
                const SizedBox(width: 30),
                GestureDetector(
                  onTap: () {
                    setState(() {
                      selectedColor = 2;
                    });
                  },
                  child: Column(
                    children: [
                      Container(
                        width: 50,
                        height: 50,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.white,
                          border: selectedColor == 2
                              ? Border.all(color: Colors.blue, width: 3)
                              : Border.all(color: Colors.black, width: 2),
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text('白棋'),
                      const Text('(后手)'),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('取消'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => GameScreen(
                  gameMode: GameMode.pve,
                  playerColor: selectedColor,
                  player: widget.player,
                  difficulty: selectedDifficulty,
                ),
              ),
            );
          },
          child: const Text('开始游戏'),
        ),
      ],
    );
  }

  Widget _buildDifficultyButton(Difficulty difficulty, String label) {
    bool isSelected = selectedDifficulty == difficulty;
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected ? Colors.brown : Colors.grey[200],
        foregroundColor: isSelected ? Colors.white : Colors.black,
      ),
      onPressed: () {
        setState(() {
          selectedDifficulty = difficulty;
        });
      },
      child: Text(label),
    );
  }
}

class PlayerManagerScreen extends StatefulWidget {
  final List<Player> players;
  final String currentPlayerId;
  final Function(Player) onChanged;

  const PlayerManagerScreen({
    super.key,
    required this.players,
    required this.currentPlayerId,
    required this.onChanged,
  });

  @override
  State<PlayerManagerScreen> createState() => _PlayerManagerScreenState();
}

class _PlayerManagerScreenState extends State<PlayerManagerScreen> {
  late List<Player> _players;
  late String _currentPlayerId;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _players = List.from(widget.players);
    _currentPlayerId = widget.currentPlayerId;
  }

  Future<void> _addPlayer() async {
    String? newName;
    await showDialog(
      context: context,
      builder: (context) {
        TextEditingController controller = TextEditingController();
        return AlertDialog(
          title: const Text('添加玩家'),
          content: Container(
            width: 300,
            child: TextField(
              controller: controller,
              decoration: const InputDecoration(hintText: '输入玩家名称'),
              autofocus: true,
              onSubmitted: (value) {
                if (value.trim().isNotEmpty) {
                  newName = value.trim();
                  Navigator.pop(context);
                }
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () {
                String name = controller.text.trim();
                if (name.isNotEmpty) {
                  newName = name;
                  Navigator.pop(context);
                }
              },
              child: const Text('确定'),
            ),
          ],
        );
      },
    );
    if (newName != null && newName!.isNotEmpty) {
      await _doAddPlayer(newName!);
    }
  }

  Future<void> _doAddPlayer(String name) async {
    setState(() => _isLoading = true);
    try {
      await StorageManager.addPlayer(name);
      await _refreshPlayers();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('添加失败: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _deletePlayer(String playerId) async {
    bool? confirmed = await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: const Text('删除后该玩家的历史记录也会被删除，确定继续？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('删除'),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await _doDeletePlayer(playerId);
    }
  }

  Future<void> _doDeletePlayer(String playerId) async {
    setState(() => _isLoading = true);
    try {
      await StorageManager.deletePlayer(playerId);
      await _refreshPlayers();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('删除失败: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _selectPlayer(String playerId) async {
    setState(() => _isLoading = true);
    try {
      await StorageManager.setCurrentPlayerId(playerId);
      setState(() {
        _currentPlayerId = playerId;
      });
      Player selected = _players.firstWhere((p) => p.id == playerId);
      widget.onChanged(selected);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('选择失败: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _refreshPlayers() async {
    try {
      _players = await StorageManager.getPlayers();
      _currentPlayerId = await StorageManager.getCurrentPlayerId();
      setState(() {});
    } catch (e) {
      print('Failed to refresh players: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('玩家管理'),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _players.length + 1,
              itemBuilder: (context, index) {
                if (index == _players.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 10),
                    child: ElevatedButton.icon(
                      onPressed: _addPlayer,
                      icon: const Icon(Icons.add),
                      label: const Text('添加玩家'),
                    ),
                  );
                }
                Player player = _players[index];
                bool isCurrent = player.id == _currentPlayerId;
                return Card(
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: Colors.brown,
                      child: Text(
                        player.name.isNotEmpty ? player.name[0] : '?',
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                    title: Text(player.name),
                    subtitle: Text('胜${player.wins} 负${player.losses} 平${player.draws}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (!isCurrent)
                          TextButton(
                            onPressed: () => _selectPlayer(player.id),
                            child: const Text('选择'),
                          ),
                        if (isCurrent)
                          const Icon(Icons.check, color: Colors.green),
                        IconButton(
                          onPressed: () => _deletePlayer(player.id),
                          icon: const Icon(Icons.delete, color: Colors.red),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}

class RecordsScreen extends StatefulWidget {
  final Player player;

  const RecordsScreen({
    super.key,
    required this.player,
  });

  @override
  State<RecordsScreen> createState() => _RecordsScreenState();
}

class _RecordsScreenState extends State<RecordsScreen> {
  List<GameRecord> records = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadRecords();
  }

  Future<void> _loadRecords() async {
    records = await StorageManager.getRecordsByPlayer(widget.player.id);
    setState(() {
      isLoading = false;
    });
  }

  Future<void> _clearRecords() async {
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认清除'),
        content: const Text('确定清除所有历史战绩吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await StorageManager.clearRecords();
              setState(() {
                records = [];
              });
            },
            child: const Text('清除'),
          ),
        ],
      ),
    );
  }

  String _formatDuration(int seconds) {
    int mins = seconds ~/ 60;
    int secs = seconds % 60;
    return '${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('历史战绩'),
        centerTitle: true,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '玩家：${widget.player.name}',
                        style: const TextStyle(fontSize: 16),
                      ),
                      ElevatedButton(
                        onPressed: _clearRecords,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                        ),
                        child: const Text('清除记录'),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: records.isEmpty
                      ? const Center(child: Text('暂无对战记录'))
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: records.length,
                          itemBuilder: (context, index) {
                            GameRecord record = records[index];
                            return Card(
                              child: ListTile(
                                leading: Container(
                                  width: 36,
                                  height: 36,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: record.result == 'win'
                                        ? Colors.green
                                        : record.result == 'loss'
                                            ? Colors.red
                                            : Colors.grey,
                                  ),
                                  child: Center(
                                    child: Text(
                                      record.result == 'win'
                                          ? '胜'
                                          : record.result == 'loss'
                                              ? '负'
                                              : '平',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ),
                                title: Text(
                                  '难度：${record.aiDifficulty} · ${record.playerColor == 1 ? '黑棋' : '白棋'}',
                                ),
                                subtitle: Text(
                                  '${_formatDate(record.date)} · ${_formatDuration(record.duration)}',
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }
}

enum GameMode {
  pvp,
  pve,
}
