/* FinTrack loans */

import { api } from './api.js';
import { formatCurrency } from './format.js';

/* Keep recent loans list in memory for editing */
let cachedLoans = [];

/* Load all loans and display them as a table */
const loadList = async () => {
    cachedLoans = await api.getLoans();

    /* Group loans by borrower and currency */
    const sums = {};
    for (const l of cachedLoans) {
        const key = `${l.borrower}|${l.currency}`;
        if (!sums[key]) sums[key] = {
            name: l.borrower, currency: l.currency,
            count: 0, principal: 0, due: 0, paid: 0,
        };
        const s = sums[key];
        s.count++;
        s.principal += l.principal;
        s.due += l.principal * (1 + l.interest_rate / 100);
        s.paid += l.amount_paid;
    }
    const rows = Object.values(sums);

    document.getElementById('borrower_count').textContent =
        `${rows.length} ${rows.length === 1 ? 'borrower' : 'borrowers'}`;

    const empty = document.getElementById('loans_empty');
    const table = document.getElementById('borrowers_table');

    /* When there are no borrowers hide the table */
    if (rows.length === 0) {
        table.hidden = true;
        empty.hidden = false;
        return;
    }
    /* If borrowers present show the table */
    table.hidden = false;
    empty.hidden = true;

    document.getElementById('borrowers_body').innerHTML = rows.map(r => {
        const remaining = Math.max(r.due - r.paid, 0);
        const status = r.paid <= 0 ? 'UNPAID'
                     : r.paid >= r.due ? 'PAID'
                     : 'PARTIAL';
        return `
            <tr data-borrower="${r.name}" style="cursor:pointer">
                <td><strong>${r.name}</strong></td>
                <td>${r.count}</td>
                <td>${formatCurrency(r.principal, r.currency)}</td>
                <td>${formatCurrency(r.due, r.currency)}</td>
                <td style="color:var(--accent)">${formatCurrency(r.paid, r.currency)}</td>
                <td style="color:var(--red)">${formatCurrency(remaining, r.currency)}</td>
                <td>${badge(status)}</td>
            </tr>
        `;
    }).join('');
};

/* Coloured status badge */
const badge = (status) => {
    const cls = status === 'PAID' ? 'badge--paid'
              : status === 'PARTIAL' ? 'badge--partial'
              : 'badge--unpaid';
    return `<span class="badge ${cls}">${status}</span>`;
};

/* Load the modal */

const initModal = async () => {
    const html = await fetch('/modals/loan').then(r => r.text());
    document.getElementById('modal-root').innerHTML = html;

    document.getElementById('loan_close').addEventListener('click', closeLoanModal);
    document.getElementById('loan_modal').addEventListener('click', e => {
        if (e.target.id === 'loan_modal') closeLoanModal();
    });
    document.getElementById('loan_form').addEventListener('submit', handleLoanSubmit);
};

const openLoanModal = () => {
    document.querySelector('[name="borrowed_at"]').value = new Date().toISOString().slice(0, 10);
    document.getElementById('loan_modal').hidden = false;
};

const closeLoanModal = () => {
    document.getElementById('loan_form').reset();
    document.getElementById('loan_error').hidden = true;
    document.getElementById('loan_modal').hidden = true;
};

const handleLoanSubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    data.principal = parseFloat(data.principal);
    data.interest_rate = parseFloat(data.interest_rate) || 0;

    try {
        await api.createLoan(data);
        closeLoanModal();
        await loadList();
    } catch (err) {
        const errorDiv = document.getElementById('loan_error');
        errorDiv.textContent = err.message;
        errorDiv.hidden = false;
    }
};

/* Connect Add Loan button */

document.querySelectorAll('[data-action="add-loan"]').forEach(btn => {
    btn.addEventListener('click', openLoanModal);
});

document.addEventListener('keydown', (event) => {
    const modal = document.getElementById('loan_modal');
    if (event.key === 'Escape' && modal && !modal.hidden) closeLoanModal();
});

loadList();
initModal();