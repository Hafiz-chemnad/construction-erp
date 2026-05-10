// modules/works/project_detail.js
import { api } from '../../js/api.js';
import './operations.js';

const urlParams = new URLSearchParams(window.location.search);
const workId = urlParams.get('work_id');
// --- ADD THESE 3 LINES ---
const pId = urlParams.get('panchayath_id');
const pName = urlParams.get('name');
document.getElementById('back-btn').href = `works.html?panchayath_id=${pId}&name=${pName}`;
const container = document.getElementById('form-container');

async function loadProjectFlow() {
    const work = await api.getWorkDetail(workId);
    if (!work) return;

    document.getElementById('proj-name').textContent = work.name;
    document.getElementById('current-balance').textContent = `₹${work.current_amount || work.deal_amount}`;
    
    // Grab the header so we can update the title
    const flowStatusHeader = document.getElementById('flow-status');
    
// --- UPDATE THE LOGIC GATE (Inside loadProjectFlow) ---
    if (work.status === 'PENDING') {
        if(flowStatusHeader) flowStatusHeader.textContent = "Stage 1: Tender Submission";
        showTenderStage();
    } else if (work.status === 'WAITING_VERDICT') {
        if(flowStatusHeader) flowStatusHeader.textContent = "Stage 2: Client Verdict";
        showVerdictStage(); 
    } else if (work.status === 'ACCEPTED') {
        if(flowStatusHeader) flowStatusHeader.textContent = "Stage 3: Selection Notice";
        showNoticeStage(); 
    } else if (work.status === 'NOTICE_RECEIVED') {
        if(flowStatusHeader) flowStatusHeader.textContent = "Stage 4: Agreement Details";
        showAgreementStage();
    } else if (work.status === 'AGREEMENT_DONE') {
        if(flowStatusHeader) flowStatusHeader.textContent = "Stage 5: Site Handover";
        showHandoverStage(); // <-- NEW STAGE!
   } else if (work.status === 'INITIALIZED') {
        // Change the title
        const flowStatusHeader = document.getElementById('flow-status');
        if(flowStatusHeader) flowStatusHeader.textContent = "Stage 6: Active Work";
        
        // Build the bridge button
        container.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <h3 style="color: #27ae60;">Project is Active</h3>
                <p style="color: #666; margin-bottom: 20px;">Agreement signed and site handed over.</p>
                
                <button id="btn-goto-ops" class="card" style="width: 100%; padding: 15px; background: #27ae60; color: white; border: none; font-weight: bold; font-size: 1.1rem; cursor: pointer;">
                    Open Daily Site Logs &rarr;
                </button>
            </div>
        `;
        
        // Make the button navigate to your brand new HTML file, passing the IDs along!
        document.getElementById('btn-goto-ops').onclick = () => {
            const pId = urlParams.get('panchayath_id');
            const pName = urlParams.get('name');
            window.location.href = `operations.html?work_id=${workId}&panchayath_id=${pId}&name=${pName}`;
        };
    }
      else if (work.status === 'REJECTED') {
        container.innerHTML = `<h3 style="color: red;">Work Rejected</h3><p>This project is closed.</p>`;
    }
}

// STAGE 1: SUBMIT TENDER
function showTenderStage() {
    container.innerHTML = `
        <h3>Step 1: Submit Tender</h3>
        <input type="number" id="t_amt" placeholder="Tender Amount" style="display:block; margin-bottom:10px; width:100%; padding:8px;">
        <input type="number" id="e_amt" placeholder="EMD Amount" style="display:block; margin-bottom:10px; width:100%; padding:8px;">
        <button id="btn-submit-tender" class="card" style="width:100%; background:#3498db; color:white;">Submit Tender & Wait</button>
    `;
    
    document.getElementById('btn-submit-tender').onclick = async () => {
        const tAmt = document.getElementById('t_amt').value;
        const eAmt = document.getElementById('e_amt').value;
        
        if(!tAmt || !eAmt) return alert("Please enter both amounts.");

        // "Remember" these numbers in the browser for later
        localStorage.setItem(`tender_${workId}`, tAmt);
        localStorage.setItem(`emd_${workId}`, eAmt);

        // Move to the Waiting Room
        await api.updateWorkStatus(workId, 'WAITING_VERDICT');
        location.reload();
    };
}

// STAGE 2: THE WAITING ROOM (Days/Weeks pass...)
function showVerdictStage() {
    // Retrieve the amounts we saved earlier
    const tAmt = localStorage.getItem(`tender_${workId}`) || "Unknown";
    const eAmt = localStorage.getItem(`emd_${workId}`) || "Unknown";

    container.innerHTML = `
        <h3>Step 2: Awaiting Client Verdict</h3>
        <p style="color: #666;">Tender Submitted: ₹${tAmt} | EMD: ₹${eAmt}</p>
        <p><i>Waiting for client response...</i></p>
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <button id="btn-accept" class="card" style="flex: 1; background:#2ecc71; color:white;">Client Accepted</button>
            <button id="btn-reject" class="card" style="flex: 1; background:#e74c3c; color:white;">Client Rejected</button>
        </div>
    `;

    document.getElementById('btn-accept').onclick = async () => {
        await api.updateWorkStatus(workId, 'ACCEPTED');
        location.reload();
    };

    document.getElementById('btn-reject').onclick = async () => {
        await api.updateWorkStatus(workId, 'REJECTED');
        location.reload();
    };
}

// STAGE 3: SELECTION NOTICE
function showNoticeStage() {
    container.innerHTML = `
        <h3>Step 3: Selection Notice</h3>
        <p style="color: green; font-weight: bold;">✓ Client Accepted</p>
        <p>When did you receive the official selection notice?</p>
        <input type="date" id="notice_date" style="display:block; margin-bottom:10px; width:100%; padding:8px;">
        <button id="btn-submit-notice" class="card" style="width:100%; background:#f1c40f; color:#333; font-weight:bold;">Log Notice Received</button>
    `;
    
    document.getElementById('btn-submit-notice').onclick = async () => {
        const date = document.getElementById('notice_date').value;
        if(!date) return alert("Please select the date.");
        
        localStorage.setItem(`notice_date_${workId}`, date);
        await api.updateWorkStatus(workId, 'NOTICE_RECEIVED');
        location.reload();
    };
}

// STAGE 4: THE AGREEMENT (The 4 Pillars)
// STAGE 4: THE AGREEMENT (Handover removed)
function showAgreementStage() {
    container.innerHTML = `
        <h3>Step 4: Final Agreement Details</h3>
        <div style="text-align:left;">
            <label><b>Supervision</b></label>
            <input type="number" id="sup_amt" placeholder="Amount" style="width:100%; padding:8px; margin-bottom:5px;">
            <label><input type="checkbox" id="sup_cert"> Certificate Received</label>
            <hr>
            <label><b>Stamp</b></label>
            <input type="number" id="stmp_amt" placeholder="Stamp Amount" style="width:100%; padding:8px; margin-bottom:10px;">
            <hr>
            <label><b>Security</b></label>
            <input type="number" id="sec_amt" placeholder="Security Amount" style="width:100%; padding:8px; margin-bottom:5px;">
            <input type="number" id="sec_period" placeholder="Period (Months)" style="width:100%; padding:8px; margin-bottom:5px;">
            <input type="date" id="sec_date" title="Closing Date" style="width:100%; padding:8px; margin-bottom:10px;">
            <hr>
            <label><b>Insurance</b></label>
            <input type="number" id="ins_amt" placeholder="Insurance Amount" style="width:100%; padding:8px; margin-bottom:10px;">
        </div>
        <button id="btn-save-agreement" class="card" style="width:100%; background:#3498db; color:white;">Sign Agreement & Wait for Site</button>
    `;

    document.getElementById('btn-save-agreement').onclick = async () => {
        // Save agreement data in the browser temporarily
        localStorage.setItem(`sup_amt_${workId}`, document.getElementById('sup_amt').value || 0);
        localStorage.setItem(`sup_cert_${workId}`, document.getElementById('sup_cert').checked);
        localStorage.setItem(`stmp_amt_${workId}`, document.getElementById('stmp_amt').value || 0);
        localStorage.setItem(`sec_amt_${workId}`, document.getElementById('sec_amt').value || 0);
        localStorage.setItem(`sec_period_${workId}`, document.getElementById('sec_period').value || 0);
        localStorage.setItem(`sec_date_${workId}`, document.getElementById('sec_date').value || '');
        localStorage.setItem(`ins_amt_${workId}`, document.getElementById('ins_amt').value || 0);

        // Move to the final waiting room
        await api.updateWorkStatus(workId, 'AGREEMENT_DONE');
        location.reload();
    };
}

// STAGE 5: SITE HANDOVER (The Final Gate!)
function showHandoverStage() {
    container.innerHTML = `
        <h3>Step 5: Site Handover</h3>
        <p style="color: green; font-weight: bold;">✓ Agreement Signed</p>
        <p>Enter the details once the client officially hands over the site.</p>
        <input type="text" id="site_no" placeholder="Site Number" style="display:block; margin-bottom:10px; width:100%; padding:8px;">
        <input type="date" id="h_date" title="Handover Date" style="display:block; margin-bottom:10px; width:100%; padding:8px;">
        <button id="btn-submit-handover" class="card" style="width:100%; background:#27ae60; color:white;">Accept Handover & Open Site</button>
    `;

    document.getElementById('btn-submit-handover').onclick = async () => {
        const siteNo = document.getElementById('site_no').value;
        const hDate = document.getElementById('h_date').value;

        if(!siteNo || !hDate) return alert("Please enter Site Number and Date.");

        // Retrieve ALL the data we saved from the previous days/weeks
        const data = {
            work_id: parseInt(workId),
            tender_amount: parseFloat(localStorage.getItem(`tender_${workId}`)) || 0,
            emd_amount: parseFloat(localStorage.getItem(`emd_${workId}`)) || 0,
            selection_notice_received: true,
            selection_notice_date: localStorage.getItem(`notice_date_${workId}`) || null,
            supervision_amount: parseFloat(localStorage.getItem(`sup_amt_${workId}`)) || 0,
            supervision_cert_received: localStorage.getItem(`sup_cert_${workId}`) === 'true',
            stamp_amount: parseFloat(localStorage.getItem(`stmp_amt_${workId}`)) || 0,
            security_amount: parseFloat(localStorage.getItem(`sec_amt_${workId}`)) || 0,
            security_period: parseInt(localStorage.getItem(`sec_period_${workId}`)) || 0,
            security_closing_date: localStorage.getItem(`sec_date_${workId}`) || null,
            insurance_amount: parseFloat(localStorage.getItem(`ins_amt_${workId}`)) || 0,
            site_number: siteNo,
            site_handover_date: hDate
        };

        // Send the COMPLETE package to Python
        const res = await api.createAgreement(data);
        if (res) location.reload();
    };
}

// Initialize the page
loadProjectFlow();