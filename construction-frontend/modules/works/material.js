// modules/works/material.js
import { api } from '../../js/api.js';

export function renderMaterialForm(workId, logContainer) {
    // 1. Inject the Material Form AND the History Button
    logContainer.innerHTML = `
        <h3 style="margin-top: 0; color: #3498db;">Log Material Purchase</h3>
        <input type="text" id="mat_name" placeholder="Material Name (e.g., Cement, Sand)" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px;">
        <input type="number" id="mat_amt" placeholder="Cost Amount (₹)" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px;">
        <input type="date" id="mat_date" title="Purchase Date" style="width:100%; padding:10px; margin-bottom:15px; border:1px solid #ccc; border-radius:5px;">
        
        <button id="btn-save-mat" style="width:100%; padding:12px; background:#3498db; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
            Save Material & Update Balance
        </button>

        <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;">
        
        <button id="btn-view-history" style="width:100%; padding:10px; background:#f39c12; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
            View Purchase History
        </button>
        
        <div id="mat-history-container" style="margin-top: 15px;"></div>
    `;

    document.getElementById('mat_date').valueAsDate = new Date();

    // 2. Attach the Save Logic
    document.getElementById('btn-save-mat').onclick = async () => {
        const name = document.getElementById('mat_name').value;
        const amt = parseFloat(document.getElementById('mat_amt').value);
        const date = document.getElementById('mat_date').value;

        if (!name || !amt) return alert("Please enter the material name and amount.");

        const data = {
            work_id: parseInt(workId),
            name: name,
            amount: amt,
            date: date,
            note: "Purchased"
        };

        const res = await api.addMaterial(data);
        if (res) {
            // 1. Clear the inputs so they can add another item
            document.getElementById('mat_name').value = '';
            document.getElementById('mat_amt').value = '';

            // 2. Update the Live Balance at the top instantly
            const updatedWork = await api.getWorkDetail(workId);
            if (updatedWork) {
                document.getElementById('current-balance').textContent = `₹${updatedWork.current_amount || updatedWork.deal_amount}`;
            }

            // 3. If they are looking at the history table, refresh it
            const historyContainer = document.getElementById('mat-history-container');
            if (historyContainer.innerHTML !== "") {
                document.getElementById('btn-view-history').click();
            }
        } 
    };

    // 3. Attach the View History Logic
    document.getElementById('btn-view-history').onclick = async () => {
        const historyContainer = document.getElementById('mat-history-container');
        historyContainer.innerHTML = "<p>Loading data...</p>";

        // Fetch from Python!
        const materials = await api.getMaterialsByWork(workId);

        if (!materials || materials.length === 0) {
            historyContainer.innerHTML = "<p style='color: #666; text-align: center;'>No materials purchased yet.</p>";
            return;
        }

        // Build the table
        let tableHTML = `
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                <tr style="background: #f4f6f9; border-bottom: 2px solid #ccc;">
                    <th style="padding: 10px; text-align: left;">Date</th>
                    <th style="padding: 10px; text-align: left;">Material</th>
                    <th style="padding: 10px; text-align: right;">Amount</th>
                </tr>
        `;

        // Loop through the data and add rows
        materials.forEach(m => {
            tableHTML += `
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px;">${m.date}</td>
                    <td style="padding: 10px;">${m.name}</td>
                    <td style="padding: 10px; text-align: right; color: #e74c3c; font-weight: bold;">₹${m.amount}</td>
                </tr>
            `;
        });

        tableHTML += "</table>";
        
        // Push the table to the screen
        historyContainer.innerHTML = tableHTML;
    };
}