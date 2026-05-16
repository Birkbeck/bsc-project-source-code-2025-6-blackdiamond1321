/* FinTrack budgets */

import { api } from './api.js';
import { formatCurrency } from './format.js';
import { getCategoryColour } from './palette.js';

/* SVG icons (https://heroicons.com/) for the Actions column */
const PENCIL_ICON = `
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
</svg>`;

const TRASH_ICON = `
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
</svg>`;

/* Load budgets and transactions */
const loadBudgets = async () => {
    const [budgets, transactions] = await Promise.all([
        api.getBudgets(),
        api.getTransactions(),
    ]);
    display(budgets, transactions);
};

const display = (budgets, transactions) => {
    const grid = document.getElementById('budgets_grid');
    const empty = document.getElementById('budgets_empty');

     /* When there are no budgets hide the table */
    if (budgets.length === 0) {
        grid.hidden = true;
        empty.hidden = false;
        return;
    }

    /* If present show the grid */
    grid.hidden = false;
    empty.hidden = true;

    /* Current month  */
    const currentMonth = new Date().toISOString().slice(0, 7);

    grid.innerHTML = budgets.map(b => {
        /* Sum expenses in this category */
        const spent = b.category === 'Total Spending'
        ? transactions
                .filter(t => t.date.startsWith(currentMonth) && t.type === 'expense')
                .reduce((sum, t) => sum + t.amount, 0)
        : transactions
                .filter(t => t.category === b.category
                    && t.date.startsWith(currentMonth)
                    && t.type === 'expense')
                .reduce((sum, t) => sum + t.amount, 0);

        /* Bar displaying limit. Max 100% */
        const percent = (spent / b.monthly_limit) * 100;
        const barWidth = Math.min(100, percent);
        const colour = getCategoryColour(b.category);

        return `
            <div class="budget-card" data-category="${b.category}">
                <div class="budget-header">
                    <span class="budget-category" style="color:${colour}">${b.category}</span>
                    <div class="budget-actions">
                        <button class="budget-action-btn" data-action="edit" data-category="${b.category}" aria-label="Edit">${PENCIL_ICON}</button>
                        <button class="budget-action-btn" data-action="delete" data-category="${b.category}" aria-label="Delete">${TRASH_ICON}</button>
                    </div>
                </div>
                <div class="budget-amounts">
                    <strong>${formatCurrency(spent)}</strong>
                    <span class="budget-limit">/ ${formatCurrency(b.monthly_limit)}</span>
                </div>
                <div class="budget-bar">
                    <div class="budget-bar-fill" style="width:${barWidth}%"></div>
                </div>
                <div class="budget-status">${Math.round(percent)}% used</div>
            </div>
        `;
    }).join('');
};

loadBudgets();