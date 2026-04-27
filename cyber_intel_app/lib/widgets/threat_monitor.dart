import 'package:flutter/material.dart';

class ThreatMonitor extends StatelessWidget {
  final double threatLevel; // 0.0 to 100.0

  const ThreatMonitor({super.key, required this.threatLevel});

  @override
  Widget build(BuildContext context) {
    // Determine color based on threat level
    Color glowColor;
    if (threatLevel < 30) {
      glowColor = const Color(0xFF4CAF50); // Safe Green
    } else if (threatLevel < 70) {
      glowColor = const Color(0xFFFFC857); // Warning Yellow
    } else {
      glowColor = const Color(0xFFFF5252); // Critical Red
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Threat Level',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              '${threatLevel.toStringAsFixed(1)}%',
              style: TextStyle(
                color: glowColor,
                fontWeight: FontWeight.bold,
                shadows: [
                  Shadow(
                    color: glowColor.withOpacity(0.8),
                    blurRadius: 8,
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 12,
          decoration: BoxDecoration(
            color: const Color(0xFF161F28),
            borderRadius: BorderRadius.circular(6),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.5),
                blurRadius: 4,
              )
            ]
          ),
          child: Stack(
            children: [
              // Animated progress bar
              AnimatedContainer(
                duration: const Duration(milliseconds: 800),
                curve: Curves.easeOutCubic,
                width: MediaQuery.of(context).size.width * (threatLevel / 100).clamp(0.0, 1.0),
                decoration: BoxDecoration(
                  color: glowColor,
                  borderRadius: BorderRadius.circular(6),
                  boxShadow: [
                    BoxShadow(
                      color: glowColor.withOpacity(0.6),
                      blurRadius: 10,
                      spreadRadius: 1,
                    )
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// Extension to allow inset box shadow (rough approximation since true inset isn't native without extra code)
// Here we just use a normal container background for simplicity, the inset shadow was a comment for design intent.
