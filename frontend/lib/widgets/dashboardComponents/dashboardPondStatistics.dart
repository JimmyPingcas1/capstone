import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class WaterQualityTrendWidget extends StatelessWidget {
  const WaterQualityTrendWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final temperature = [
      ChartDataNum(0, 20),
      ChartDataNum(3, 21),
      ChartDataNum(6, 22),
      ChartDataNum(9, 23),
      ChartDataNum(12, 23),
      ChartDataNum(15, 24),
      ChartDataNum(18, 25),
      ChartDataNum(21, 26),
      ChartDataNum(24, 28),
    ];

    final oxygen = [
      ChartDataNum(0, 6),
      ChartDataNum(3, 6.2),
      ChartDataNum(6, 5.8),
      ChartDataNum(9, 6.5),
      ChartDataNum(12, 6),
      ChartDataNum(15, 6.8),
      ChartDataNum(18, 7),
      ChartDataNum(21, 7.2),
      ChartDataNum(24, 7),
    ];

    final ph = [
      ChartDataNum(0, 7),
      ChartDataNum(3, 7.1),
      ChartDataNum(6, 7.2),
      ChartDataNum(9, 7),
      ChartDataNum(12, 6.9),
      ChartDataNum(15, 7.1),
      ChartDataNum(18, 7.2),
      ChartDataNum(21, 7.3),
      ChartDataNum(24, 7.2),
    ];

    final ammonia = [
      ChartDataNum(0, 0.2),
      ChartDataNum(3, 0.3),
      ChartDataNum(6, 0.2),
      ChartDataNum(9, 0.4),
      ChartDataNum(12, 0.4),
      ChartDataNum(15, 0.3),
      ChartDataNum(18, 0.2),
      ChartDataNum(21, 0.3),
      ChartDataNum(24, 0.2),
    ];

    final turbidity = [
      ChartDataNum(0, 10),
      ChartDataNum(3, 11),
      ChartDataNum(6, 12),
      ChartDataNum(9, 13),
      ChartDataNum(12, 14),
      ChartDataNum(15, 14),
      ChartDataNum(18, 15),
      ChartDataNum(21, 14),
      ChartDataNum(24, 14),
    ];

    final TrackballBehavior trackballBehavior = TrackballBehavior(
      enable: true,
      activationMode: ActivationMode.singleTap,
      lineType: TrackballLineType.vertical,
      tooltipDisplayMode: TrackballDisplayMode.groupAllPoints,
      tooltipSettings: const InteractiveTooltip(
        enable: true,
        color: Colors.black87,
        textStyle: TextStyle(
          color: Colors.white,
          fontSize: 12,
        ),
      ),
    );

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Water Quality Trend",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            "Last 24 hours overview",
            style: TextStyle(fontSize: 14, color: Colors.grey[600]),
          ),
          const SizedBox(height: 12),
          LayoutBuilder(
            builder: (context, constraints) {
              return ConstrainedBox(
                constraints: BoxConstraints(
                  maxHeight: constraints.maxHeight > 250
                      ? 250
                      : constraints.maxHeight,
                ),
                child: SfCartesianChart(
                  plotAreaBorderWidth: 0,
                  trackballBehavior: trackballBehavior,
                  legend: Legend(
                    isVisible: true,
                    position: LegendPosition.bottom,
                    overflowMode: LegendItemOverflowMode.wrap,
                    alignment: ChartAlignment.center,
                    textStyle: const TextStyle(fontSize: 10),
                    legendItemBuilder:
                        (String name, dynamic series, dynamic point, int index) {
                      Color color;
                      String displayName = name;
                      switch (name) {
                        case 'Temperature':
                          color = Colors.blue;
                          displayName = 'Temp';
                          break;
                        case 'Dissolved Oxygen':
                          color = Colors.green;
                          displayName = 'DO';
                          break;
                        case 'PH':
                          color = Colors.yellow.shade800;
                          break;
                        case 'Ammonia':
                          color = Colors.red;
                          displayName = 'Ammonia';
                          break;
                        case 'Turbidity':
                          color = Colors.brown;
                          displayName = 'Turbidity';
                          break;
                        default:
                          color = Colors.black;
                      }
                      return Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 2, vertical: 1),
                        child: Text(
                          displayName,
                          style: TextStyle(
                            fontSize: 12,
                            color: color,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      );
                    },
                  ),
                  primaryXAxis: NumericAxis(
                    minimum: 0,
                    maximum: 24,
                    interval: 3,
                    majorGridLines: const MajorGridLines(width: 1),
                    edgeLabelPlacement: EdgeLabelPlacement.shift,
                  ),
                  primaryYAxis: NumericAxis(
                    majorGridLines: const MajorGridLines(width: 0),
                    minorGridLines: const MinorGridLines(width: 0),
                  ),
                  series: <SplineAreaSeries<ChartDataNum, double>>[
                    SplineAreaSeries<ChartDataNum, double>(
                      dataSource: temperature,
                      xValueMapper: (d, _) => d.time,
                      yValueMapper: (d, _) => d.value,
                      name: 'Temperature',
                      color: Colors.blue.withOpacity(0.2),
                      borderColor: Colors.blue,
                      borderWidth: 2,
                      splineType: SplineType.natural,
                    ),
                    SplineAreaSeries<ChartDataNum, double>(
                      dataSource: oxygen,
                      xValueMapper: (d, _) => d.time,
                      yValueMapper: (d, _) => d.value,
                      name: 'Dissolved Oxygen',
                      color: Colors.green.withOpacity(0.2),
                      borderColor: Colors.green,
                      borderWidth: 2,
                      splineType: SplineType.natural,
                    ),
                    SplineAreaSeries<ChartDataNum, double>(
                      dataSource: ph,
                      xValueMapper: (d, _) => d.time,
                      yValueMapper: (d, _) => d.value,
                      name: 'PH',
                      color: Colors.yellow.shade800.withOpacity(0.2),
                      borderColor: Colors.yellow.shade800,
                      borderWidth: 2,
                      splineType: SplineType.natural,
                    ),
                    SplineAreaSeries<ChartDataNum, double>(
                      dataSource: ammonia,
                      xValueMapper: (d, _) => d.time,
                      yValueMapper: (d, _) => d.value,
                      name: 'Ammonia',
                      color: Colors.red.withOpacity(0.2),
                      borderColor: Colors.red,
                      borderWidth: 2,
                      splineType: SplineType.natural,
                    ),
                    SplineAreaSeries<ChartDataNum, double>(
                      dataSource: turbidity,
                      xValueMapper: (d, _) => d.time,
                      yValueMapper: (d, _) => d.value,
                      name: 'Turbidity',
                      color: Colors.brown.withOpacity(0.2),
                      borderColor: Colors.brown,
                      borderWidth: 2,
                      splineType: SplineType.natural,
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class ChartDataNum {
  final double time;
  final double value;
  ChartDataNum(this.time, this.value);
}
