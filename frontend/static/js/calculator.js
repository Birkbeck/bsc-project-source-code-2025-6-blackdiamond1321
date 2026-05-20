/* FinTrack calculator */

import { api } from './api.js';
import { formatCurrency } from './format.js';

/* Read the form, run the projection, render the cards */
const calculate = async (e) => {
    if (e) e.preventDefault();

    const data = {
        principal: parseFloat(document.querySelector('[name="principal"]').value),
        monthly_contribution: parseFloat(document.querySelector('[name="monthly_contribution"]').value),
        annual_rate_pct: parseFloat(document.querySelector('[name="annual_rate_pct"]').value),
        years: parseInt(document.querySelector('[name="years"]').value, 10),
    };

    try {
        const result = await api.calculate(data);
        renderStats(result);
    } catch (err) {
        alert('Calculation failed: ' + err.message);
    }
};

/* Total invested, total interest and final balance */
const renderStats = (result) => {
    document.getElementById('calc_stats').innerHTML = `
        <div class="stat-card">
            <div class="stat-card-label">Total Invested</div>
            <div class="stat-card-value">${formatCurrency(result.total_invested)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Total Interest</div>
            <div class="stat-card-value stat-card-value--income">${formatCurrency(result.total_interest)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Final Balance</div>
            <div class="stat-card-value stat-card-value--net">${formatCurrency(result.total_balance)}</div>
        </div>
    `;
};

document.getElementById('calc_form').addEventListener('submit', calculate);


calculate();