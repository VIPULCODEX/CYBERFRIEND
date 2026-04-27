import 'dart:math';
import 'package:flutter/material.dart';

class NeuralBackground extends StatefulWidget {
  final Widget child;

  const NeuralBackground({super.key, required this.child});

  @override
  State<NeuralBackground> createState() => _NeuralBackgroundState();
}

class _NeuralBackgroundState extends State<NeuralBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  List<Node> nodes = [];

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (nodes.isEmpty) {
      final size = MediaQuery.of(context).size;
      _generateNodes(size);
    }
  }

  void _generateNodes(Size size) {
    final random = Random();
    // Reduce number of nodes for mobile performance
    int nodeCount = 35;
    for (int i = 0; i < nodeCount; i++) {
      nodes.add(
        Node(
          position: Offset(
            random.nextDouble() * size.width,
            random.nextDouble() * size.height,
          ),
          velocity: Offset(
            (random.nextDouble() - 0.5) * 1.5,
            (random.nextDouble() - 0.5) * 1.5,
          ),
        ),
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Dark background
        Container(color: const Color(0xFF0B0F14)),
        
        // Animated Mesh
        AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            _updateNodes(MediaQuery.of(context).size);
            return CustomPaint(
              painter: NeuralPainter(nodes: nodes),
              size: Size.infinite,
            );
          },
        ),
        
        // Content on top
        widget.child,
      ],
    );
  }

  void _updateNodes(Size size) {
    for (var node in nodes) {
      node.position += node.velocity;

      // Bounce off walls
      if (node.position.dx < 0 || node.position.dx > size.width) {
        node.velocity = Offset(-node.velocity.dx, node.velocity.dy);
      }
      if (node.position.dy < 0 || node.position.dy > size.height) {
        node.velocity = Offset(node.velocity.dx, -node.velocity.dy);
      }
    }
  }
}

class Node {
  Offset position;
  Offset velocity;

  Node({required this.position, required this.velocity});
}

class NeuralPainter extends CustomPainter {
  final List<Node> nodes;
  final double connectionDistance = 120.0;

  NeuralPainter({required this.nodes});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF4CAF50).withOpacity(0.5) // QuantX Green
      ..style = PaintingStyle.fill;

    final linePaint = Paint()
      ..color = const Color(0xFF4CAF50).withOpacity(0.15)
      ..strokeWidth = 1.0;

    // Draw lines between close nodes
    for (int i = 0; i < nodes.length; i++) {
      for (int j = i + 1; j < nodes.length; j++) {
        final distance = (nodes[i].position - nodes[j].position).distance;
        if (distance < connectionDistance) {
          // Opacity based on distance
          linePaint.color = const Color(0xFF4CAF50).withOpacity(
            (0.3 * (1 - distance / connectionDistance)).clamp(0.0, 0.3),
          );
          canvas.drawLine(nodes[i].position, nodes[j].position, linePaint);
        }
      }
    }

    // Draw nodes
    for (var node in nodes) {
      canvas.drawCircle(node.position, 2.0, paint);
      
      // Add subtle glow to nodes
      final glowPaint = Paint()
        ..color = const Color(0xFF4CAF50).withOpacity(0.1)
        ..style = PaintingStyle.fill
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3);
      canvas.drawCircle(node.position, 4.0, glowPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
