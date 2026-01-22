import 'package:flutter/material.dart';

class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final Color? backgroundColor;
  final Color? hoverColor;
  final Color? textColor;
  final double borderRadius;

  CustomButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.backgroundColor,
    this.hoverColor,
    this.textColor,
    this.borderRadius = 12,
  });

  // Helper function to make a color slightly lighter
  Color lightenColor(Color color, [double amount = 0.1]) {
    assert(amount >= 0 && amount <= 1);
    final hsl = HSLColor.fromColor(color);
    final hslLight = hsl.withLightness(
      (hsl.lightness + amount).clamp(0.0, 1.0),
    );
    return hslLight.toColor();
  }

  @override
  Widget build(BuildContext context) {
    // Base color defaults to Flutter's blue
    final Color baseColor = backgroundColor ?? Colors.blue;
    final Color hoverClr = hoverColor ?? lightenColor(baseColor, 0.03);
    final Color txtColor = textColor ?? Colors.white;

    return ElevatedButton(
      onPressed: onPressed,
      style: ButtonStyle(
        backgroundColor: MaterialStateProperty.resolveWith<Color>(
          (states) {
            if (states.contains(MaterialState.hovered) ||
                states.contains(MaterialState.pressed)) {
              return hoverClr;
            }
            return baseColor;
          },
        ),
        shape: MaterialStateProperty.all(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius),
          ),
        ),
        elevation: MaterialStateProperty.all(2),
        padding: MaterialStateProperty.all(
          const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
        ),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: txtColor,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
