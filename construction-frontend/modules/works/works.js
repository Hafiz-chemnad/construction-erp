// modules/works/works.js
import { api } from '../../js/api.js';

const urlParams = new URLSearchParams(window.location.search);
const panchayathId = urlParams.get('panchayath_id');
const panchayathName = urlParams.get('name');

if (!panchayathId || panchayathId === 'null') {
    window.location.href = '../../index.html';
}

const pageTitle = document.getElementById('page-title');
const grid = document.getElementById('works-grid');
const addBtn = document.getElementById('add-work-btn');

if (panchayathName) {
    pageTitle.textContent = `${panchayathName} Projects`;
}

// --- THE TRANSLATOR FUNCTION ---
function getFriendlyStatus(status) {
    switch(status) {
        case 'PENDING': return 'Tender Not Submitted';
        case 'WAITING_VERDICT': return 'Waiting for Client Response';
        case 'ACCEPTED': return 'Waiting for Selection Notice';
        case 'NOTICE_RECEIVED': return 'Pending Final Agreement';
        case 'AGREEMENT_DONE': return 'Waiting for Site Handover';
        case 'INITIALIZED': return 'Work in Progress';
        case 'REJECTED': return 'Rejected';
        case 'FINISHED': return 'Completed';
        default: return status;
    }
}

// Color logic so the user immediately knows if action is needed
function getStatusColor(status) {
    if (status === 'INITIALIZED' || status === 'FINISHED') return '#27ae60'; // Green
    if (status === 'REJECTED') return '#e74c3c'; // Red
    return '#f39c12'; // Orange for all "Waiting" stages
}

async function loadWorks() {
    if (!panchayathId) return;

    const works = await api.getWorks(panchayathId);
    if (!works) return;

    works.forEach(w => {
        const card = document.createElement('div');
        card.className = 'card';
        
        // Use our new translator functions!
        const displayText = getFriendlyStatus(w.status);
        const displayColor = getStatusColor(w.status);
        
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="card-title">${w.name}</div>
                    <p style="font-size: 0.9em; font-weight: bold; color: ${displayColor};">
                        Status: ${displayText}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.8rem; color: #666;">Balance</div>
                    <div style="font-weight: bold; color: #2c3e50;">₹${w.current_amount || w.deal_amount}</div>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            // We now pass the panchayath_id and name into the URL too!
            window.location.href = `project_detail.html?work_id=${w.id}&panchayath_id=${panchayathId}&name=${panchayathName}`;
        });

        grid.insertBefore(card, addBtn);
    });
}

// --- NEW FORM LOGIC (Unwrapped so it runs immediately!) ---
const addWorkForm = document.getElementById('add-work-form');

// 1. When clicking the "+ Add New Work" card, show the form
if (addBtn) {
    addBtn.addEventListener('click', () => {
        addWorkForm.style.display = 'block'; // Show the form
        addBtn.style.display = 'none';       // Hide the "+ Add" card temporarily
    });
}

// 2. When clicking Cancel, hide the form again
document.getElementById('btn-cancel-work').addEventListener('click', () => {
    addWorkForm.style.display = 'none';  // Hide the form
    addBtn.style.display = 'flex';       // Bring back the "+ Add" card
    
    // Clear out the inputs so it's fresh next time
    document.getElementById('new_work_name').value = '';
    document.getElementById('new_work_deal').value = '';
});

// 3. When clicking Save, send the data to Python!
document.getElementById('btn-save-work').addEventListener('click', async () => {
    const name = document.getElementById('new_work_name').value;
    const dealStr = document.getElementById('new_work_deal').value;

    if (!name || !dealStr) {
        return alert("Please enter both the Project Name and Deal Amount.");
    }

    const workData = {
        panchayath_id: parseInt(panchayathId),
        name: name,
        deal_amount: parseFloat(dealStr)
    };

    const response = await api.addWork(workData);
    if (response) {
        window.location.reload();
    }
});

// Force the browser to refresh data if the user clicked the "Back" button
window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        window.location.reload();
    }
});

// Start the page!
loadWorks();