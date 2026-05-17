/* Charts builder */

import { RING_COLOURS } from './palette.js';
import { formatCurrency } from './format.js';
// import Chart.js. The library to draw the spending line
import Chart from 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/auto/+esm';

/* Display a donut chart */
export const displayDonut = (target, legendTarget, data) => {
    /* Sort part. Biggest part first */
    const entries = [...data].sort((a, b) => b.value - a.value);
    const total = entries.reduce((sum, e) => sum + e.value, 0);

    if (entries.length === 0 || total === 0) {
        target.style.background = 'rgba(255,255,255,0.06)';
        legendTarget.innerHTML = '<p style="color:var(--text2)">No data</p>';
        return;
    }

    let cumulative = 0;
    const stops = entries.map((e, i) => {
        const share = (e.value / total) * 100;
        const start = cumulative;
        cumulative += share;
        const colour = RING_COLOURS[i % RING_COLOURS.length];
        return `${colour} ${start}% ${cumulative}%`;
    });
    target.style.background = `conic-gradient(${stops.join(', ')})`;

    /* Legend */
    legendTarget.innerHTML = entries.map((e, i) => {
        const pct = (e.value / total * 100).toFixed(0);
        const colour = RING_COLOURS[i % RING_COLOURS.length];
        return `
            <div class="donut-legend-row">
                <span class="donut-legend-dot" style="background:${colour}"></span>
                <span class="donut-legend-name">${e.label}</span>
                <span class="donut-legend-amount">${formatCurrency(e.value)}</span>
                <span class="donut-legend-pct">${pct}%</span>
            </div>
        `;
    }).join('');
};

/* Horizontal bar chart */
export const displayBars = (target, data) => {
    if (data.length === 0) {
        target.innerHTML = '<p style="color:var(--text2)">No data</p>';
        return;
    }

    let grandInc = 0, grandExp = 0;

    /* Build a row for each method */
    const rows = data.map(({ label, income = 0, expense = 0 }) => {
        grandInc += income;
        grandExp += expense;
        const total = income + expense;
        const incPct = total > 0 ? (income / total) * 100 : 0;
        const expPct = total > 0 ? (expense / total) * 100 : 0;
        return { label, income, expense, incPct, expPct, isTotal: false };
    });

    /* Add a Total */
    const grandTotal = grandInc + grandExp;
    rows.push({
        label: 'Total',
        income: grandInc,
        expense: grandExp,
        incPct: grandTotal > 0 ? (grandInc / grandTotal) * 100 : 0,
        expPct: grandTotal > 0 ? (grandExp / grandTotal) * 100 : 0,
        isTotal: true,
    });

    target.innerHTML = rows.map(r => `
        <div class="method-row${r.isTotal ? ' method-row--total' : ''}">
            <div class="method-row-top">
                <span class="method-row-name">${r.label}</span>
                <span class="method-row-amounts">
                    <span class="method-row-income">+${formatCurrency(r.income)}</span>
                    <span class="method-row-sep">/</span>
                    <span class="method-row-expense">-${formatCurrency(r.expense)}</span>
                </span>
            </div>
            <div class="method-row-bar">
                <div class="method-row-fill method-row-fill--income"  style="width:${r.incPct}%"></div>
                <div class="method-row-fill method-row-fill--expense" style="width:${r.expPct}%"></div>
            </div>
        </div>
    `).join('');
};

/* Daily spending line */
/* Draws a red line showing how much was spent each day. */
let lineChart;
export const displayLine = (target, data) => {
    /* If no data display message */
    if (!data.length || data.every(d => d.value === 0)) {
        target.innerHTML = '<p style="color:var(--text2)">No spending in this range</p>';
        return;
    }

    /*Check if canvas inside the target  */
    if (!target.querySelector('canvas')) target.innerHTML = '<canvas></canvas>';
    const canvas = target.querySelector('canvas');

    /* Clear previous chart */
    if (lineChart) lineChart.destroy();

    /* Change date format */
    const labels = data.map(d => +d.label.slice(8) + '/' + +d.label.slice(5, 7));
    const values = data.map(d => d.value);

    lineChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                data: values,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239,68,68,0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: data.length > 60 ? 0 : 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    ticks: {
                        color: '#64748b',
                        maxTicksLimit: 12
                    },
                    grid:  {
                        color: 'rgba(255,255,255,0.04)'
                    },
                },
                y: {
                    ticks: {
                        color: '#64748b', callback: v => '£' + v
                    },
                    grid:  {
                        color: 'rgba(255,255,255,0.04)'
                    },
                },
            },
        },
    });
};