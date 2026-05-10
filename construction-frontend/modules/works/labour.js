// modules/works/labour.js
import { api } from '../../js/api.js';

export async function renderLabourModule(workId, logContainer) {
    // 1. Setup the main menu with 4 tabs
    logContainer.innerHTML = `
        <h3 style="color: #9b59b6;">Labour Management</h3>
        <div style="display: flex; gap: 5px; margin-bottom: 20px; flex-wrap: wrap;">
            <button id="tab-add-worker" style="flex:1; min-width:80px; padding:10px; border-radius:5px; border:none; background:#8e44ad; color:white; cursor:pointer; font-size:0.8rem;">+ Worker</button>
            <button id="tab-attendance" style="flex:1; min-width:80px; padding:10px; border-radius:5px; border:none; background:#2980b9; color:white; cursor:pointer; font-size:0.8rem;">Attendance</button>
            <button id="tab-pay-worker" style="flex:1; min-width:80px; padding:10px; border-radius:5px; border:none; background:#e67e22; color:white; cursor:pointer; font-size:0.8rem;">$ Cash</button>
            <button id="tab-view-team" style="flex:1; min-width:80px; padding:10px; border-radius:5px; border:none; background:#34495e; color:white; cursor:pointer; font-size:0.8rem;">Balances</button>
        </div>
        <div id="labour-sub-form" style="background: #f9f9f9; padding: 15px; border-radius: 8px;"></div>
    `;

    const subForm = document.getElementById('labour-sub-form');

    // --- TAB 1: ADD WORKER ---
    document.getElementById('tab-add-worker').onclick = () => {
        subForm.innerHTML = `
            <h4 style="margin-top:0;">Add New Worker</h4>
            <input type="text" id="lab_name" placeholder="Full Name" style="width:100%; padding:10px; margin-bottom:10px; box-sizing:border-box; border:1px solid #ccc; border-radius:4px;">
            <input type="number" id="lab_wage" placeholder="Daily Wage (₹)" style="width:100%; padding:10px; margin-bottom:10px; box-sizing:border-box; border:1px solid #ccc; border-radius:4px;">
            <button id="save-worker" style="width:100%; padding:12px; background:#27ae60; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Save to Roster</button>
        `;
        
        document.getElementById('save-worker').onclick = async () => {
            const name = document.getElementById('lab_name').value;
            const wage = document.getElementById('lab_wage').value;
            if(!name || !wage) return alert("Please enter name and wage.");
            
            await api.addLabourer({ work_id: parseInt(workId), name, daily_wage: parseFloat(wage) });
            alert("Worker added!");
            renderLabourModule(workId, logContainer); 
        };
    };

    // --- TAB 2: MARK ATTENDANCE (WITH DATE LOGIC) ---
    document.getElementById('tab-attendance').onclick = async () => {
        subForm.innerHTML = "<p style='text-align:center;'>Loading roster...</p>";
        
        // 1. Fetch data
        const [labourers, allAttendance] = await Promise.all([
            api.getLabourers(workId),
            api.getAttendance(workId)
        ]);

        // 2. Create the Header with Date Picker
        subForm.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; background: #fff; padding: 10px; border-radius: 6px; border: 1px solid #ddd;">
                <h4 style="margin:0; font-size:0.9rem;">Attendance for:</h4>
                <input type="date" id="att_date_picker" style="border:1px solid #ccc; padding:5px; border-radius:4px; font-family:inherit;">
            </div>
            <div id="attendance-list-container"></div>
        `;

        const datePicker = document.getElementById('att_date_picker');
        const listContainer = document.getElementById('attendance-list-container');
        
        // Set default date to today (Kozhikode time)
        datePicker.valueAsDate = new Date();

        // 3. Function to render the list based on selected date
        const renderList = (selectedDate) => {
            listContainer.innerHTML = "";
            
            if (!labourers || labourers.length === 0) {
                listContainer.innerHTML = "<p style='text-align:center; color:#999;'>No workers in roster.</p>";
                return;
            }

            labourers.forEach(worker => {
                // Check if this worker was already marked present on THIS specific date
                const isPresent = (allAttendance || []).some(a => 
                    a.labourer_id === worker.id && 
                    a.date === selectedDate && 
                    a.present === true
                );

                const div = document.createElement('div');
                div.style = "display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #eee; background:white; margin-bottom:5px; border-radius:6px;";
                div.innerHTML = `
                    <span style="font-weight:bold; color:#2c3e50;">${worker.name}</span>
                    <button id="btn-att-${worker.id}" 
                        style="padding:8px 15px; border-radius:5px; border:none; font-weight:bold; cursor:pointer; transition: 0.3s;
                        ${isPresent ? 'background:#27ae60; color:white;' : 'background:#bdc3c7; color:white;'}"
                        ${isPresent ? 'disabled' : ''}>
                        ${isPresent ? '✓ Present' : 'Mark Present'}
                    </button>
                `;
                listContainer.appendChild(div);

                // Marking Logic
                div.querySelector('button').onclick = async (e) => {
                    const res = await api.markAttendance({
                        work_id: parseInt(workId),
                        labourer_id: worker.id,
                        date: selectedDate,
                        present: true
                    });
                    
                    if(res) {
                        e.target.style.background = "#27ae60";
                        e.target.innerText = "✓ Present";
                        e.target.disabled = true;
                        // Refresh local attendance data so Balances tab updates correctly
                        allAttendance.push({ labourer_id: worker.id, date: selectedDate, present: true });
                    }
                };
            });
        };

        // Initial render for today
        renderList(datePicker.value);

        // Listen for date changes
        datePicker.onchange = (e) => {
            renderList(e.target.value);
        };
    };

    // --- TAB 3: GIVE CASH ---
    document.getElementById('tab-pay-worker').onclick = async () => {
        const labourers = await api.getLabourers(workId);
        if (!labourers || labourers.length === 0) {
            subForm.innerHTML = "<p style='text-align:center; color:#666;'>No workers found.</p>";
            return;
        }

        let options = labourers.map(l => `<option value="${l.id}">${l.name} (Wage: ₹${l.daily_wage})</option>`).join('');
        
        subForm.innerHTML = `
            <h4 style="margin-top:0;">Give Cash Advance</h4>
            <select id="sel_labourer" style="width:100%; padding:10px; margin-bottom:10px; border-radius:4px; border:1px solid #ccc;">
                <option value="">-- Select Worker --</option>
                ${options}
            </select>
            <input type="number" id="pay_amt" placeholder="Amount (₹)" style="width:100%; padding:10px; margin-bottom:10px; box-sizing:border-box; border-radius:4px; border:1px solid #ccc;">
            <input type="text" id="pay_note" placeholder="Note (Optional)" style="width:100%; padding:10px; margin-bottom:10px; box-sizing:border-box; border-radius:4px; border:1px solid #ccc;">
            <button id="save-pay" style="width:100%; padding:12px; background:#e67e22; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Confirm Payment</button>
        `;

        document.getElementById('save-pay').onclick = async () => {
            const labId = document.getElementById('sel_labourer').value;
            const amt = parseFloat(document.getElementById('pay_amt').value);
            
            if(!labId || !amt) return alert("Select worker and amount");

            const [cashLogs, attendance, labourersList] = await Promise.all([
                api.getLabourCashByWork(workId),
                api.getAttendance(workId),
                api.getLabourers(workId)
            ]);

            const worker = labourersList.find(l => l.id == labId);
            const paidTotal = (cashLogs || []).filter(l => l.labourer_id == labId).reduce((s, l) => s + l.amount, 0);
            const daysCount = (attendance || []).filter(a => a.labourer_id == labId && a.present).length;
            const earnedTotal = daysCount * worker.daily_wage;

            if (paidTotal >= earnedTotal) {
                const proceed = confirm(`Note: ${worker.name} is already fully paid (Earned: ₹${earnedTotal}, Paid: ₹${paidTotal}). Record this as advance for future work?`);
                if (!proceed) return;
            }

            const res = await api.addLabourCash({
                work_id: parseInt(workId),
                labourer_id: parseInt(labId),
                type: 'Advance',
                amount: amt,
                note: document.getElementById('pay_note').value || "Advance",
                date: new Date().toISOString().split('T')[0]
            });
            
            if(res) {
                const updatedWork = await api.getWorkDetail(workId);
                document.getElementById('current-balance').textContent = `₹${updatedWork.current_amount}`;
                alert("Payment recorded!");
                document.getElementById('tab-view-team').click();
            }
        };
    };

    // --- TAB 4: TEAM BALANCES (HORIZONTAL BOARD VIEW) ---
    document.getElementById('tab-view-team').onclick = async () => {
        subForm.innerHTML = "<p style='text-align:center;'>Loading site board...</p>";
        
        const [labourers, cashLogs, attendance] = await Promise.all([
            api.getLabourers(workId),
            api.getLabourCashByWork(workId),
            api.getAttendance(workId)
        ]);

        if (!labourers || labourers.length === 0) {
            subForm.innerHTML = "<p style='text-align:center; color:#666;'>No workers registered.</p>";
            return;
        }

        let pendingCards = "";
        let advanceCards = "";
        let settledCards = "";
        
        let totalOwed = 0;
        let totalAdvance = 0;
        let pCount = 0, aCount = 0, sCount = 0;

        labourers.forEach(worker => {
            const workerPayments = (cashLogs || []).filter(l => l.labourer_id === worker.id);
            const paid = workerPayments.reduce((s, l) => s + l.amount, 0);
            const days = (attendance || []).filter(a => a.labourer_id === worker.id && a.present).length;
            const earned = days * worker.daily_wage;
            const diff = earned - paid;

            const card = `
                <div style="background: white; padding: 10px; border-radius: 6px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid ${diff > 0 ? '#e74c3c' : (diff < 0 ? '#f39c12' : '#27ae60')}">
                    <div style="font-weight: bold; font-size: 0.85rem; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${worker.name}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #444;">
                        <span>${diff > 0 ? 'Owed: <b>₹'+diff+'</b>' : (diff < 0 ? 'Adv: <b>₹'+Math.abs(diff)+'</b>' : '<b>SETTLED</b>')}</span>
                        <span style="color:#888;">${days}d</span>
                    </div>
                </div>
            `;

            if (diff > 0) { pendingCards += card; totalOwed += diff; pCount++; }
            else if (diff < 0) { advanceCards += card; totalAdvance += Math.abs(diff); aCount++; }
            else { settledCards += card; sCount++; }
        });

        subForm.innerHTML = `
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <div style="flex:1; background:#e74c3c; color:white; padding:8px; border-radius:6px; text-align:center;">
                    <small style="font-size:0.65rem; text-transform:uppercase; opacity:0.8;">Total Debt</small>
                    <div style="font-weight:bold; font-size:1rem;">₹${totalOwed}</div>
                </div>
                <div style="flex:1; background:#f39c12; color:white; padding:8px; border-radius:6px; text-align:center;">
                    <small style="font-size:0.65rem; text-transform:uppercase; opacity:0.8;">Total Advance</small>
                    <div style="font-weight:bold; font-size:1rem;">₹${totalAdvance}</div>
                </div>
            </div>

            <div style="display: flex; gap: 10px; overflow-x: auto; padding-bottom: 10px; scrollbar-width: thin; -webkit-overflow-scrolling: touch;">
                
                <div style="flex: 0 0 200px; background: #fee2e2; padding: 10px; border-radius: 8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px; color:#b91c1c; font-weight:bold; font-size:0.75rem;">
                        <span>PENDING</span> <span>${pCount}</span>
                    </div>
                    ${pendingCards || '<div style="color:#f87171; font-size:0.7rem; text-align:center; padding:10px;">Clear</div>'}
                </div>

                <div style="flex: 0 0 200px; background: #fef3c7; padding: 10px; border-radius: 8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px; color:#92400e; font-weight:bold; font-size:0.75rem;">
                        <span>IN ADVANCE</span> <span>${aCount}</span>
                    </div>
                    ${advanceCards || '<div style="color:#fbbf24; font-size:0.7rem; text-align:center; padding:10px;">None</div>'}
                </div>

                <div style="flex: 0 0 200px; background: #dcfce7; padding: 10px; border-radius: 8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px; color:#166534; font-weight:bold; font-size:0.75rem;">
                        <span>SETTLED</span> <span>${sCount}</span>
                    </div>
                    ${settledCards || '<div style="color:#4ade80; font-size:0.7rem; text-align:center; padding:10px;">Empty</div>'}
                </div>

            </div>
        `;
    };
}