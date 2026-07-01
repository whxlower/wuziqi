import 'package:flutter/material.dart';

class RuleScreen extends StatelessWidget {
  const RuleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('禁手规则说明'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '禁手规则概述',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              '禁手规则仅对黑棋生效，白棋无禁手限制。这是为了平衡黑白双方的开局优势而设立的规则。',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 20),
            _buildRuleCard(
              '三三禁手',
              '黑棋在落下一子后，同时形成两个或以上的"活三"（两端都有空位的三连）。',
              '● ● ●\n○ ● ● ● ○',
              Colors.red,
            ),
            const SizedBox(height: 16),
            _buildRuleCard(
              '四四禁手',
              '黑棋在落下一子后，同时形成两个或以上的"四"（冲四或活四）。',
              '● ● ● ●\n○ ● ● ● ● ○',
              Colors.orange,
            ),
            const SizedBox(height: 16),
            _buildRuleCard(
              '长连禁手',
              '黑棋在落下一子后，形成六个或以上连续的棋子。',
              '● ● ● ● ● ●',
              Colors.purple,
            ),
            const SizedBox(height: 20),
            const Text(
              '示例图解',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
            const SizedBox(height: 10),
            _buildExampleCard('三三禁手示例', '''
    ○ ● ○
  ○ ● ● ● ○
    ○ ● ○
    
黑棋在中心位置落子后，同时形成了两个活三（横向和纵向），属于三三禁手。
'''),
            const SizedBox(height: 16),
            _buildExampleCard('四四禁手示例', '''
● ● ● ● ○
● ● ● ● ○
○ ○ ○ ○ ○

黑棋在交叉点落子后，同时形成了两个冲四（横向和纵向），属于四四禁手。
'''),
            const SizedBox(height: 16),
            _buildExampleCard('长连禁手示例', '''
● ● ● ● ● ●
○ ○ ○ ○ ○ ○

黑棋形成了六连，属于长连禁手。
'''),
            const SizedBox(height: 20),
            const Text(
              '注意事项',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              '1. 禁手规则只针对黑棋，白棋可以任意落子。',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 8),
            const Text(
              '2. 如果黑棋唯一获胜方式是通过禁手，则该禁手无效，黑棋可以落子。',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 8),
            const Text(
              '3. 禁手必须在落子前声明，落子后不能反悔。',
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRuleCard(String title, String description, String pattern, Color color) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              description,
              style: const TextStyle(fontSize: 15),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                pattern,
                style: const TextStyle(
                  fontSize: 16,
                  fontFamily: 'monospace',
                  letterSpacing: 2,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExampleCard(String title, String content) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              content,
              style: const TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }
}
