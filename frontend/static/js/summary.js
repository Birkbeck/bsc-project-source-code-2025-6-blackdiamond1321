/* FinTrack summary */

import { api } from './api.js';
import { formatCurrency } from './format.js';

let transactions = [];

/* Load transactions and set default range to this month */
const load = async () => {
    transactions = await api.getTransactions();
    setThisMonth();
};

/* Set the date inputs to the first and last day of month */
const setThisMonth = () => {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const lastDay = new Date(y, now.getMonth() + 1, 0).getDate();

    document.querySelector('[name="from"]').value = `${y}-${m}-01`;
    document.querySelector('[name="to"]').value   = `${y}-${m}-${String(lastDay).padStart(2, '0')}`;

    display();
};

/* Filter transactions and display stat cards */
const display = () => {
    const from = document.querySelector('[name="from"]').value;
    const to   = document.querySelector('[name="to"]').value;
    if (!from || !to) return;

    /* Date */
    const filtered = transactions.filter(t => t.date >= from && t.date <= to);

    let income = 0, expense = 0;
    for (const t of filtered) {
        if (t.type === 'income') income += t.amount;
        else expense += t.amount;
    }
    const net = income - expense;
    const count = filtered.length;

    document.getElementById('stat_cards').innerHTML = `
        <div class="stat-card">
            <div class="stat-card-label">Total Income</div>
            <div class="stat-card-value stat-card-value--income">${formatCurrency(income)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Total Expenses</div>
            <div class="stat-card-value stat-card-value--expense">${formatCurrency(expense)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Net Savings</div>
            <div class="stat-card-value stat-card-value--net">${formatCurrency(net)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Transactions</div>
            <div class="stat-card-value">${count}</div>
        </div>
    `;
};

/* Connect date inputs */
document.querySelector('[name="from"]').addEventListener('change', display);
document.querySelector('[name="to"]').addEventListener('change', display);
document.getElementById('this_month_btn').addEventListener('click', setThisMonth);

load();