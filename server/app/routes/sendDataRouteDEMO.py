from fastapi import APIRouter, Body
from fastapi.responses import HTMLResponse, JSONResponse
from ..controller.SendDataDEMO import predict_water_quality

router = APIRouter()


@router.get("/AiPrediction", response_class=HTMLResponse)
def home():
        # Simple HTML form that posts JSON to the same endpoint and displays result
        html = """
        <!doctype html>
        <html>
            <head>
                <meta charset="utf-8" />
                <title>AI Prediction</title>
                <style>
                    body { font-family: Arial, Helvetica, sans-serif; padding: 20px; background:#f7fafc }
                    label { display:block; margin:6px 0 }
                    input[type=number] { width:120px }
                    .panel { margin-top:16px; padding:12px; border-radius:8px; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,0.06) }
                    .status-safe { border-left:6px solid #2ecc71 }
                    .status-danger { border-left:6px solid #e74c3c }
                    .label-row { display:flex; justify-content:space-between; padding:6px 8px; border-radius:6px; margin:6px 0 }
                    .label-safe { background:#e8f8f1; color:#117a4a }
                    .label-danger { background:#fdecea; color:#7a1b1b }
                    .devices { margin-top:8px }
                </style>
            </head>
            <body>
                <h2>AI Water Quality Prediction</h2>
                <div>
                    <label>Temperature: <input id="temperature" type="number" step="any" value="25"></label>
                    <label>Turbidity: <input id="turbidity" type="number" step="any" value="1"></label>
                    <label>Dissolved Oxygen: <input id="dissolved_oxygen" type="number" step="any" value="7"></label>
                    <label>pH: <input id="ph" type="number" step="any" value="7"></label>
                    <label>Ammonia: <input id="ammonia" type="number" step="any" value="0.1"></label>
                    <button id="predict">Predict</button>
                </div>

                <div id="output" class="panel" style="display:none">
                    <h3 id="overallStatus">Prediction Result</h3>

                    <div><strong>Parameters:</strong>
                        <div id="params"></div>
                    </div>

                    <div class="devices">
                        <strong>Devices Needed:</strong>
                        <div id="devicesList">-</div>
                    </div>

                    <div style="margin-top:10px"><strong>Label Confidences:</strong>
                        <div id="confidences"></div>
                    </div>
                </div>

                <script>
                    function setPanelState(ok) {
                        const out = document.getElementById('output');
                        out.style.display = 'block';
                        out.classList.remove('status-safe','status-danger');
                        out.classList.add(ok ? 'status-safe' : 'status-danger');
                        document.getElementById('overallStatus').style.color = ok ? '#117a4a' : '#7a1b1b';
                        document.getElementById('overallStatus').textContent = ok ? 'Safe — No devices needed' : 'Attention — Devices recommended';
                    }

                    document.getElementById('predict').addEventListener('click', async () => {
                        const data = {
                            temperature: document.getElementById('temperature').value,
                            turbidity: document.getElementById('turbidity').value,
                            dissolved_oxygen: document.getElementById('dissolved_oxygen').value,
                            ph: document.getElementById('ph').value,
                            ammonia: document.getElementById('ammonia').value
                        };

                        const res = await fetch('/AiPrediction', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });

                        const json = await res.json();

                        // Show parameters
                        const paramsDiv = document.getElementById('params');
                        paramsDiv.innerHTML = '';
                        ['temperature','turbidity','dissolved_oxygen','ph','ammonia'].forEach(k => {
                            const v = data[k];
                            const row = document.createElement('div');
                            row.textContent = `${k}: ${v}`;
                            paramsDiv.appendChild(row);
                        });

                        // Devices
                        const devices = json.devices || [];
                        document.getElementById('devicesList').textContent = devices.length ? devices.join(', ') : 'None';

                        // Overall state: safe if no devices recommended
                        setPanelState(devices.length === 0);

                        // Confidences and labels
                        const confDiv = document.getElementById('confidences');
                        confDiv.innerHTML = '';
                        const labels = json.labels || {};
                        const confidences = json.confidences || {};
                        for (const k of Object.keys(confidences)) {
                            const val = confidences[k];
                            const lbl = labels[k] === 1 ? 'issue' : 'ok';
                            const row = document.createElement('div');
                            row.className = 'label-row ' + (lbl === 'ok' ? 'label-safe' : 'label-danger');
                            row.innerHTML = `<div>${k}</div><div>${lbl.toUpperCase()} — ${val}%</div>`;
                            confDiv.appendChild(row);
                        }
                    });
                </script>
            </body>
        </html>
        """
        return HTMLResponse(html)


@router.post("/AiPrediction")
async def predictWaterParameters(data: dict = Body(...)):
        def _float(v):
                try:
                        return float(v)
                except (TypeError, ValueError):
                        return 0.0

        temperature = _float(data.get("temperature"))
        dissolved_oxygen = _float(data.get("dissolved_oxygen"))
        ammonia = _float(data.get("ammonia"))
        ph = _float(data.get("ph"))
        turbidity = _float(data.get("turbidity"))
        ai_enabled = bool(data.get("ai_enabled", True))

        # Correct feature order! Do not save to DB for form requests (save=False)
        result = await predict_water_quality(
            temp=temperature,
            turbidity=turbidity,
            do=dissolved_oxygen,
            ph=ph,
            ammonia=ammonia,
            ai_enabled=ai_enabled
        )

        return JSONResponse(result)

