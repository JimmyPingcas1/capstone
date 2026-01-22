import 'package:flutter/material.dart';

class BottomTabs extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const BottomTabs({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: onTap,
      type: BottomNavigationBarType.fixed,
      selectedItemColor: Colors.blue,  
      unselectedItemColor: Colors.grey,  
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.dashboard),
          label: 'Dashboard',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.settings),
          label: 'Control',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.water),
          label: 'Pond',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person),
          label: 'Account',
        ),
      ],
    );
  }
}
