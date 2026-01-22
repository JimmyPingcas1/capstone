import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class PondStatistics extends StatefulWidget {
  const PondStatistics({super.key});

  @override
  State<PondStatistics> createState() => _PondStatisticsState();
}

class _PondStatisticsState extends State<PondStatistics> {
  List<ChartDataNum> temperature = [];
  List<ChartDataNum> oxygen = [];
  List<ChartDataNum> ph = [];
  List<ChartDataNum> ammonia = [];
  List<ChartDataNum> turbidity = [];

  @override
  void initState() {
    super.initState();
    loadWaterQualityData();
  }

  Future<void> loadWaterQualityData() async {
    try {
      final String jsonString =
          await rootBundle.loadString('assets/water_quality.json');
      final data = json.decode(jsonString);

      setState(() {
        temperature = (data['temperature'] as List<dynamic>? ?? [])
            .map((e) =>
                ChartDataNum((e['time'] as num).toDouble(), (e['value'] as num).toDouble()))
            .toList();

        oxygen = (data['dissolved_oxygen'] as List<dynamic>? ?? [])
            .map((e) =>
                ChartDataNum((e['time'] as num).toDouble(), (e['value'] as num).toDouble()))
            .toList();

        ph = (data['ph'] as List<dynamic>? ?? [])
            .map((e) =>
                ChartDataNum((e['time'] as num).toDouble(), (e['value'] as num).toDouble()))
            .toList();

        ammonia = (data['ammonia'] as List<dynamic>? ?? [])
            .map((e) =>
                ChartDataNum((e['time'] as num).toDouble(), (e['value'] as num).toDouble()))
            .toList();

        turbidity = (data['turbidity'] as List<dynamic>? ?? [])
            .map((e) =>
                ChartDataNum((e['time'] as num).toDouble(), (e['value'] as num).toDouble()))
            .toList();

        void add24HourPoint(List<ChartDataNum> list) {
          if (list.isNotEmpty && list.last.time < 24) {
            list.add(ChartDataNum(24.0, list.last.value));
          }
        }

        add24HourPoint(temperature);
        add24HourPoint(oxygen);
        add24HourPoint(ph);
        add24HourPoint(ammonia);
        add24HourPoint(turbidity);
      });
    } catch (e) {
      debugPrint('Error loading JSON: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final TrackballBehavior trackballBehavior = TrackballBehavior(
    enable: true,
    activationMode: ActivationMode.singleTap, // Show on touch immediately
    lineType: TrackballLineType.vertical,
    tooltipDisplayMode: TrackballDisplayMode.groupAllPoints,
    shouldAlwaysShow: false,
    tooltipSettings: const InteractiveTooltip(
      enable: true,
      color: Colors.black87,
      textStyle: TextStyle(color: Colors.white, fontSize: 12),
    ),
  );


    return SizedBox(
      height: 270,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.water, color: Colors.blue),
              SizedBox(width: 6),
              Text(
                '24-Hour Water Quality Overview',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 8),

          temperature.isEmpty
              ? const Center(child: CircularProgressIndicator())
              : Expanded(
                  child: SfCartesianChart(
                    enableAxisAnimation: true,
                    plotAreaBorderWidth: 0,
                    trackballBehavior: trackballBehavior,

                    legend: Legend(
                      isVisible: true,
                      position: LegendPosition.bottom,
                      overflowMode: LegendItemOverflowMode.wrap,
                      alignment: ChartAlignment.center,
                      textStyle: const TextStyle(fontSize: 12),
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
                            break;
                          case 'Turbidity':
                            color = Colors.brown;
                            break;
                          default:
                            color = Colors.black;
                        }
                        return Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 2),
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
                      minimum: 1,
                      maximum: 24.1,
                      interval: 1,
                      majorGridLines: const MajorGridLines(width: 1),
                      edgeLabelPlacement: EdgeLabelPlacement.none,
                    ),

                    primaryYAxis: NumericAxis(
                      majorGridLines: const MajorGridLines(width: 0),
                      minorGridLines: const MinorGridLines(width: 0),
                    ),

                    series: <SplineAreaSeries<ChartDataNum, double>>[
                      _buildSeries(
                        data: temperature,
                        name: 'Temperature',
                        fill: Colors.blue,
                      ),
                      _buildSeries(
                        data: oxygen,
                        name: 'Dissolved Oxygen',
                        fill: Colors.green,
                      ),
                      _buildSeries(
                        data: ph,
                        name: 'PH',
                        fill: Colors.yellow.shade800,
                      ),
                      _buildSeries(
                        data: ammonia,
                        name: 'Ammonia',
                        fill: Colors.red,
                      ),
                      _buildSeries(
                        data: turbidity,
                        name: 'Turbidity',
                        fill: Colors.brown,
                      ),
                    ],
                  ),
                ),
        ],
      ),
    );
  }

  SplineAreaSeries<ChartDataNum, double> _buildSeries({
    required List<ChartDataNum> data,
    required String name,
    required Color fill,
  }) {
    return SplineAreaSeries<ChartDataNum, double>(
      dataSource: data,
      xValueMapper: (d, _) => d.time,
      yValueMapper: (d, _) => d.value,
      name: name,
      color: fill.withOpacity(0.2),
      borderColor: fill,
      borderWidth: 2,
      splineType: SplineType.natural,
      animationDuration: 2000,
      animationDelay: 0,
    );
  }
}

class ChartDataNum {
  final double time;
  final double value;
  ChartDataNum(this.time, this.value);
}
