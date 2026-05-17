/* Charts builder */

import { RING_COLOURS } from './palette.js';
import { formatCurrency } from './format.js';

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