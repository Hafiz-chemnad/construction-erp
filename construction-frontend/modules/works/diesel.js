// modules/works/diesel.js
import { api } from '../../js/api.js';

export function renderDieselForm(workId, logContainer) {
    // 1. Inject the Diesel Form AND the History Button
    logContainer.innerHTML = `
        <h3 style="margin-top: 0; color: #e67e22;">Log Vehicle Fuel</h3>
        <input type="text" id="dsl_vehicle" placeholder="Vehicle/Machine Name (e.g., JCB, Truck #1234)" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px;">
        <input type="number" id="dsl_amt" placeholder="Cost Amount (₹)" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px;">
        <input type="date" id="dsl_date" title="Fill Date" style="width:100%; padding:10px; margin-bottom:15px; border:1px solid #ccc; border-radius:5px;">
        
        <button id="btn-save-dsl" style="width:100%; padding:12px; background:#e67e22; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
            Save Diesel & Update Balance
        </button>

        <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;">
        
        <button id="btn-view-dsl-history" style="width:100%; padding:10px; background:#f39c12; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
            View Fuel History
        </button>
        
        <div id="dsl-history-container" style="margin-top: 15px;"></div>
    `;

    document.getElementById('dsl_date').valueAsDate = new Date();

    // 2. Attach the Save Logic
    document.getElementById('btn-save-dsl').onclick = async () => {
        const vehicle = document.getElementById('dsl_vehicle').value;
        const amt = parseFloat(document.getElementById('dsl_amt').value);
        const date = document.getElementById('dsl_date').value;

        if (!vehicle || !amt) return alert("Please enter the vehicle name and amount.");

        const data = {
            work_id: parseInt(workId),
            vehicle_name: vehicle,
            amount: amt,
            date: date,
            note: "Fuel"
        };

        const res = await api.addDiesel(data);
        if (res) {
            // 1. Clear the inputs
            document.getElementById('dsl_vehicle').value = '';
            document.getElementById('dsl_amt').value = '';

            // 2. Update the Live Balance instantly
            const updatedWork = await api.getWorkDetail(workId);
            if (updatedWork) {
                document.getElementById('current-balance').textContent = `₹${updatedWork.current_amount || updatedWork.deal_amount}`;
            }

            // 3. Refresh the history table if it's open
            const historyContainer = document.getElementById('dsl-history-container');
            if (historyContainer.innerHTML !== "") {
                document.getElementById('btn-view-dsl-history').click();
            }
        } 
    };

    // 3. Attach the View History Logic
    document.getElementById('btn-view-dsl-history').onclick = async () => {
        const historyContainer = document.getElementById('dsl-history-container');
        historyContainer.innerHTML = "<p>Loading data...</p>";

        const dieselLogs = await api.getDieselByWork(workId);

        if (!dieselLogs || dieselLogs.length === 0) {
            historyContainer.innerHTML = "<p style='color: #666; text-align: center;'>No fuel logged yet.</p>";
            return;
        }

        let tableHTML = `
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                <tr style="background: #f4f6f9; border-bottom: 2px solid #ccc;">
                    <th style="padding: 10px; text-align: left;">Date</th>
                    <th style="padding: 10px; text-align: left;">Vehicle</th>
                    <th style="padding: 10px; text-align: right;">Cost</th>
                </tr>
        `;

        dieselLogs.forEach(d => {
            tableHTML += `
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px;">${d.date}</td>
                    <td style="padding: 10px;">${d.vehicle_name}</td>
                    <td style="padding: 10px; text-align: right; color: #e74c3c; font-weight: bold;">₹${d.amount}</td>
                </tr>
            `;
        });

        tableHTML += "</table>";
        historyContainer.innerHTML = tableHTML;
    };
}