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