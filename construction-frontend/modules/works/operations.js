// modules/works/operations.js
import { api } from '../../js/api.js';
import { renderMaterialForm } from './material.js'; 
import { renderDieselForm } from './diesel.js';// Import the material logic
import { renderLabourModule } from './labour.js';

// inside openDailyLog...


// Get the IDs from the URL
const urlParams = new URLSearchParams(window.location.search);
const workId = urlParams.get('work_id');
const pId = urlParams.get('panchayath_id');
const pName = urlParams.get('name');

// Load Current Balance at the top of the operations page
async function loadBalance() {
    const work = await api.getWorkDetail(workId);
    if (work) {
        document.getElementById('current-balance').textContent = `₹${work.current_amount || work.deal_amount}`;
    }
}

// Setup the DOM elements for the menu and form area
const opsMenu = document.getElementById('ops-menu');
const logArea = document.getElementById('daily-log-area');
const logContainer = document.getElementById('log-form-container');

// 1. Open the requested form
window.openDailyLog = (type) => {
    opsMenu.style.display = 'none';  // Hide the buttons
    logArea.style.display = 'block'; // Show the form area
    
    if (type === 'material') {
        renderMaterialForm(workId, logContainer);
    }
    if (type === 'labour') {
    renderLabourModule(workId, logContainer);
    }
    if (type === 'diesel') {
        renderDieselForm(workId, logContainer);    }
};

// 2. Close the form and go back to the 3 buttons
window.closeDailyLog = () => {
    logArea.style.display = 'none';
    opsMenu.style.display = 'grid';
    logContainer.innerHTML = ""; // Clear the form
};

// Start the page
if (workId) loadBalance();