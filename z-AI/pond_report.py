from fpdf import FPDF


class PDFReport(FPDF):

    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "IoT Fishpond AI Control Report", 0, 1, "C")
        self.ln(5)

    def section_title(self, title):
        self.set_font("Arial", "B", 14)
        self.set_fill_color(220, 230, 250)
        self.cell(0, 8, title, 0, 1, "L", fill=True)
        self.ln(3)

    def add_text(self, text):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def add_json_block(self, json_text):
        self.set_font("Courier", "", 10)
        self.set_fill_color(240, 240, 240)
        self.multi_cell(0, 6, json_text, border=1, fill=True)
        self.ln(4)

    def add_table(self, headers, rows):
        self.set_font("Arial", "B", 11)
        col_width = self.epw / len(headers)

        # Header row
        for header in headers:
            self.cell(col_width, 8, header, border=1, align="C")
        self.ln()

        # Data rows
        self.set_font("Arial", "", 11)
        for row in rows:
            for item in row:
                self.cell(col_width, 8, str(item), border=1, align="C")
            self.ln()

        self.ln(5)


pdf = PDFReport()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()


# 1. Sensor Reading
pdf.section_title("1. Sensor Reading (ESP32 to AI backend)")

pdf.add_text(
    "1. ESP32 reads sensors every 1 minute:\n"
    "   - Temperature, pH, Dissolved Oxygen, Turbidity, Ammonia.\n"
    "2. ESP32 sends HTTP POST request to FastAPI endpoint:\n"
    "   /api/sensor-ai"
)

json_sensor = """{
  "temperature": 33.0,
  "turbidity": 2.5,
  "do": 3.5,
  "ph": 7.2,
  "ammonia": 0.5
}"""

pdf.add_json_block(json_sensor)

pdf.add_text(
    "3. FastAPI stores this data inside MongoDB sensors_collection."
)


# 2. AI Prediction Logic
pdf.section_title("2. AI Prediction Logic (Server side)")

pdf.add_text(
    "1. FastAPI checks the latest document in aiPrediction_collection.\n"
    "2. For each pond parameter, it checks the _fixed_at field.\n"
    "   - If _fixed_at is None: parameter is still being fixed.\n"
    "   - If _fixed_at has a timestamp: parameter is safe.\n"
    "3. Based on status:"
)

pdf.add_text("If any parameter is still being fixed:")

json_fixing = """{
  "ai_mode": true,
  "danger": false,
  "devices": {},
  "fixing_parameters": ["Temperature", "Ammonia"]
}"""

pdf.add_json_block(json_fixing)

pdf.add_text("If all parameters are fixed:")

json_ai_active = """{
  "ai_mode": true,
  "danger": true,
  "devices": {
      "waterpump": "ON",
      "heater": "ON"
  },
  "fixing_parameters": []
}"""

pdf.add_json_block(json_ai_active)


# 3. AI to ESP32 Command
pdf.section_title("3. AI to ESP32 Command (WebSocket)")

pdf.add_text(
    "1. ESP32 opens one WebSocket connection to the AI backend:\n"
    "   ws://server_ip:8000/ws/ai-mode\n"
    "2. FastAPI sends JSON whenever AI decides devices should turn ON or pause.\n"
    "3. If danger is false: ESP32 does nothing.\n"
    "4. If danger is true: ESP32 turns ON instructed devices."
)


# 4. ESP32 Fixing Detection
pdf.section_title("4. ESP32 Fixing Detection")

pdf.add_text(
    "1. ESP32 compares live sensor readings against safe limits.\n"
    "2. When a parameter returns to safe range, ESP32 sends POST request:\n"
    "   /api/parameter-fixed"
)

json_fixed = """{
  "parameter_name": "Temperature",
  "parameter_value": 28.0
}"""

pdf.add_json_block(json_fixed)

pdf.add_text(
    "3. FastAPI updates the _fixed_at field in MongoDB.\n"
    "4. AI now knows that the parameter is fixed."
)


# 5. AI Resumes Control
pdf.section_title("5. AI Resumes Control")

pdf.add_text(
    "Once all parameters have timestamps in _fixed_at fields:\n"
    "- AI resumes predictions.\n"
    "- Dangerous parameters are identified.\n"
    "- Devices are instructed through the same WebSocket connection."
)


# Key Points Table
pdf.section_title("Key Points Summary")

headers = ["Step", "Direction", "Purpose", "Notes"]

rows = [
    ["1", "ESP32 to FastAPI", "Send sensor readings", "POST /api/sensor-ai"],
    ["2", "FastAPI to MongoDB", "Store sensor data", "sensors_collection"],
    ["3", "FastAPI", "Check fixing status", "_fixed_at fields"],
    ["4", "FastAPI to ESP32", "Send AI command", "WebSocket JSON"],
    ["5", "ESP32", "Apply devices", "Only if danger is true"],
    ["6", "ESP32 to FastAPI", "Report fixed parameter", "POST /api/parameter-fixed"],
    ["7", "FastAPI to MongoDB", "Update _fixed_at", "Marks parameter safe"]
]

pdf.add_table(headers, rows)


# Final Summary
pdf.section_title("System Flow Summary")

pdf.add_text(
    "1. ESP32 continuously sends sensor readings.\n"
    "2. AI checks MongoDB for fixing status.\n"
    "3. If parameters are still being fixed, AI pauses predictions.\n"
    "4. When ESP32 reports parameters fixed, MongoDB updates _fixed_at.\n"
    "5. AI resumes control and sends device commands via WebSocket.\n\n"
    "The AI determines whether a problem is fixed by checking the _fixed_at timestamp."
)


# Save File
pdf.output("pond_ai_report.pdf")

print("PDF generated successfully: pond_ai_report.pdf")