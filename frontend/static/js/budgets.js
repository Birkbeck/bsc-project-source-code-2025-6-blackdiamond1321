/* FinTrack budgets */

import { api } from './api.js';
import { formatCurrency } from './format.js';
import { getCategoryColour } from './palette.js';

/* Keep recent budget list in memory for edit transaction */
let cachedBudgets = [];

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

    cachedBudgets = budgets;

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

/* Load the modal */
const initModal = async () => {
    const response = await fetch('/modals/budget');
    const html = await response.text();
    document.getElementById('modal-root').innerHTML = html;

    document.getElementById('budget_close').addEventListener('click', closeBudgetModal);
    document.getElementById('budget_modal').addEventListener('click', (event) => {
        if (event.target.id === 'budget_modal') closeBudgetModal();
    });
    document.getElementById('budget_form').addEventListener('submit', handleSubmit);
};

const openBudgetModal = () => {
    document.getElementById('budget_modal').hidden = false;
};

const closeBudgetModal = () => {
    document.getElementById('budget_form').reset();
    document.getElementById('budget_error').hidden = true;
    document.getElementById('budget_original_category').value = '';
    document.getElementById('budget_modal_title').textContent = 'Add Budget';
    document.getElementById('budget_modal').hidden = true;
};

/* Edit budget */
const openEdit = (category) => {
    const b = cachedBudgets.find(bg => bg.category === category);
    if (!b) return;

     /* Fill the form with budget data */
    document.getElementById('budget_original_category').value = b.category;
    document.querySelector('select[name="category"]').value = b.category;
    document.querySelector('input[name="monthly_limit"]').value = b.monthly_limit;

     /* Change the name to Edit Budget */
    document.getElementById('budget_modal_title').textContent = 'Edit Budget';
    document.getElementById('budget_modal').hidden = false;
};

/* Delete budget */
const handleDelete = async (category) => {
    const b = cachedBudgets.find(bg => bg.category === category);
    if (!b) return;

    const ok = confirm(`Delete the "${b.category}" budget?`);
    if (!ok) return;

    await api.deleteBudget(b.category);
    await loadBudgets();
};

/* Read form and update list */
const handleSubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    data.monthly_limit = parseFloat(data.monthly_limit);

    const originalCategory = document.getElementById('budget_original_category').value;

    try {
        if (originalCategory && originalCategory !== data.category) {
            await api.deleteBudget(originalCategory);
        }
        await api.createBudget(data);
        closeBudgetModal();
        await loadBudgets();
    } catch (err) {
        const errorDiv = document.getElementById('budget_error');
        errorDiv.textContent = err.message;
        errorDiv.hidden = false;
    }
};

/* Connect Add Budget button */
document.querySelectorAll('[data-action="add-budget"]').forEach(btn => {
    btn.addEventListener('click', openBudgetModal);
});

/* Escape key closes any open modal */
document.addEventListener('keydown', (event) => {
    const modal = document.getElementById('budget_modal');
    if (event.key === 'Escape' && modal && !modal.hidden) {
        closeBudgetModal();
    }
});

/* Actions for pencil and trash buttons */
document.getElementById('budgets_grid').addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (!button) return;

    const action = button.dataset.action;
    const category = button.dataset.category;

    if (action === 'edit')   openEdit(category);
    if (action === 'delete') handleDelete(category);
});

initModal();

loadBudgets();