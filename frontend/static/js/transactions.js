/* FinTrack transaction */

import { api } from './api.js';
import { formatCurrency, formatDate } from './format.js';
import { getCategoryColour, INCOME_CATEGORIES, EXPENSE_CATEGORIES } from './palette.js';

/* SVG icons (https://heroicons.com/) for the Actions column */
const PENCIL_ICON = `
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
</svg>`;

const TRASH_ICON = `
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
</svg>`;

/* Load all transactions and display them as a table */
const loadTransactions = async () => {
    const transactions = await api.getTransactions();
    display(transactions);
};

const display = (transactions) => {
    const body = document.getElementById('transactions_body');
    const count = document.getElementById('transaction_count');
    const table = document.getElementById('transaction_table');
    const empty = document.getElementById('transaction_empty');

    count.textContent = `${transactions.length} ${transactions.length === 1 ? 'transaction' : 'transactions'}`;
    /* When there are no transactions hide the table */
    if (transactions.length === 0) {
        table.hidden = true;
        empty.hidden = false;
        return;
    }

    /* If transactions present show the table */
    table.hidden = false;
    empty.hidden = true;

    body.innerHTML = transactions.map(t => {
        const sign = t.type === 'income' ? '+' : '-';
        const colour = getCategoryColour(t.category);
        return `
            <tr class="transaction-row transaction-row--${t.type}">
                <td class="transaction-date">${formatDate(t.date)}</td>
                <td class="transaction-description">${t.description}</td>
                <td class="transaction-category"><span style="color:${colour}">${t.category}</span></td>
                <td class="transaction-method">${t.method}</td>
                <td class="transaction-amount">${sign}${formatCurrency(t.amount)}</td>
                <td class="transaction-actions">
                    <button class="transaction-action-btn" data-action="edit" data-id="${t.id}" aria-label="Edit">${PENCIL_ICON}</button>
                    <button class="transaction-action-btn" data-action="delete" data-id="${t.id}" aria-label="Delete">${TRASH_ICON}</button>
                </td>
            </tr>
        `;
    }).join('');
};

/* Load the modal */
const initModal = async () => {
    const response = await fetch('/modals/transaction');
    const html = await response.text();
    document.getElementById('modal-root').innerHTML = html;

    await loadPaymentSources();

    /* List categories */
    const typeSelect = document.querySelector('select[name="type"]');
    loadCategories(typeSelect.value);
    typeSelect.addEventListener('change', (event) => loadCategories(event.target.value));

    /* Close handlers */
    document.getElementById('transaction_close').addEventListener('click', closeTransactionModal);
    document.getElementById('transaction_modal').addEventListener('click', (event) => {
        if (event.target.id === 'transaction_modal') closeTransactionModal();
    });

    /* Submit handler */
    document.getElementById('transaction_form').addEventListener('submit', handleSubmit);
};

/* Load payment methods */
const loadPaymentSources = async () => {
    const sources = await api.getPaymentSources();
    const select = document.querySelector('select[name="method"]');
    /* No payment methods */
    if (sources.length === 0) {
        select.innerHTML = '<option value="" disabled selected>No payment methods. Add one in Settings.</option>';
        select.disabled = true;
        return;
    }

    select.innerHTML = '<option value="" disabled selected>Choose a method</option>' +
        sources.map(s => `<option>${s.name}</option>`).join('');
    select.disabled = false;
};

/* Choose category */
const loadCategories = (type, selected = '') => {
    const categories = type === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;
    const select = document.querySelector('select[name="category"]');

    select.innerHTML =
        `<option value="" disabled${selected ? '' : ' selected'}>Choose a category</option>` +
        categories.map(c => `<option${c === selected ? ' selected' : ''}>${c}</option>`).join('');
};

const openTransactionModal = () => {
    /* Show today's date by default */
    document.querySelector('[name="date"]').value = new Date().toISOString().slice(0, 10);
    document.getElementById('transaction_modal').hidden = false;
};

const closeTransactionModal = () => {
    document.getElementById('transaction_form').reset();
    document.getElementById('transaction_error').hidden = true;
    document.getElementById('transaction_edit_id').value = '';
    document.getElementById('transaction_modal').hidden = true;
};

/* Read form and update list */
const handleSubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    data.amount = parseFloat(data.amount);

    try {
        await api.createTransaction(data);
        closeTransactionModal();
        await loadTransactions();
    } catch (err) {
        const errorDiv = document.getElementById('transaction_error');
        errorDiv.textContent = err.message;
        errorDiv.hidden = false;
    }
};

/* Connect Add Transaction button */
document.querySelectorAll('[data-action="add-transaction"]').forEach(btn => {
    btn.addEventListener('click', openTransactionModal);
});

/* Escape key closes any open modall */
document.addEventListener('keydown', (event) => {
    const modal = document.getElementById('transaction_modal');
    if (event.key === 'Escape' && modal && !modal.hidden) {
        closeTransactionModal();
    }
});

loadTransactions();
initModal();