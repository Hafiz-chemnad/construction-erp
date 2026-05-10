// modules/works/panchayath.js

// 1. Import your API hub
import { api } from '../../js/api.js';

// 2. Select the HTML elements we need to interact with
const grid = document.getElementById('panchayath-grid');
const addBtn = document.getElementById('add-panchayath-btn');

/**
 * Fetch data from the backend and draw the cards on the screen
 */
async function loadDashboard() {
    // Talk to the Python API
    const panchayaths = await api.getPanchayaths();

    // If the API failed, stop here
    if (!panchayaths) return; 

    // Loop through the database records
    panchayaths.forEach(p => {
        // Create a new div for the card
        const card = document.createElement('div');
        card.className = 'card';
        
        // Add the content to the card
        card.innerHTML = `<div class="card-title">${p.name}</div>`;
        
        // Make it clickable! (For now it just alerts, later it will open the Work Details)
        // Make it clickable! (Changes the URL and passes the ID and Name)
        card.addEventListener('click', () => {
            window.location.href = `modules/works/works.html?panchayath_id=${p.id}&name=${p.name}`;
        });

        // Insert the card right before the "+ Add New" button
        grid.insertBefore(card, addBtn);
    });
}

/**
 * Handle adding a new Panchayath
 */
async function handleAddClick() {
    const name = prompt("Enter the name of the new Panchayath:");
    
    // If they clicked cancel or left it blank, do nothing
    if (!name || name.trim() === "") return; 

    // Send it to the Python API
    const response = await api.addPanchayath(name);

    if (response) {
        // Reload the page to show the fresh data
        window.location.reload();
    }
}

// 3. Attach the click event to the Add button
addBtn.addEventListener('click', handleAddClick);

// 4. Run the load function the moment the script starts
loadDashboard();