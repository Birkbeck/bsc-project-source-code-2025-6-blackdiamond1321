/* FinTrack loans */

import { api } from './api.js';
import { formatCurrency, formatDate } from './format.js';

/* Keep recent loans list in memory for editing */
let cachedLoans = [];
let currentBorrower = '';
let selectedLoanId = null;

/* Keep views in memory */
let listHtml = '';
let detailHtml = '';

const loadViews = async () => {
    listHtml = await fetch('/views/loans-list').then(r => r.text());
    detailHtml = await fetch('/views/loans-detail').then(r => r.text());
};

/* Show the list view */
const showList = async () => {
    currentBorrower = '';
    selectedLoanId = null;
    document.getElementById('view-root').innerHTML = listHtml;

    /* Connect Add Loan button */
    document.querySelectorAll('[data-action="add-loan"]').forEach(btn => {
        btn.addEventListener('click', openLoanModal);
    });

    await loadList();
};

/* List view */
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
            <tr data-borrower="${r.name}" class="loan-row">
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

/* Detail view */

const showDetail = async (name) => {
    currentBorrower = name;
    selectedLoanId = null;
    document.getElementById('view-root').innerHTML = detailHtml;
    document.getElementById('detail_name').textContent = name;
    document.getElementById('back_btn').addEventListener('click', showList);
    await loadDetail();
};

const loadDetail = async () => {
    cachedLoans = await api.getLoans();
    const loans = cachedLoans.filter(l => l.borrower === currentBorrower);

    document.getElementById('detail_body').innerHTML = loans.map(l => {
        const due = l.principal * (1 + l.interest_rate / 100);
        const remaining = Math.max(due - l.amount_paid, 0);
        const status = l.is_paid ? 'PAID' : l.amount_paid > 0 ? 'PARTIAL' : 'UNPAID';
        const selected = selectedLoanId === l.id;
        return `
            <tr data-loan-id="${l.id}" class="loan-row ${selected ? 'loan-row--selected' : ''}">
                <td><input type="radio" name="loan-select" ${selected ? 'checked' : ''} style="pointer-events:none"></td>
                <td><strong>${formatCurrency(l.principal, l.currency)}</strong></td>
                <td>${l.interest_rate}%</td>
                <td>${l.currency}</td>
                <td><strong>${formatCurrency(due, l.currency)}</strong></td>
                <td style="color:var(--accent)">${formatCurrency(l.amount_paid, l.currency)}</td>
                <td style="color:var(--red)">${formatCurrency(remaining, l.currency)}</td>
                <td style="font-size:13px">${formatDate(l.borrowed_at)}</td>
                <td>${badge(status)}</td>
            </tr>
        `;
    }).join('');

    /* Payment history for selected loan */
    const paymentsBody  = document.getElementById('payments_body');
    const paymentsEmpty = document.getElementById('payments_empty');

    if (!selectedLoanId) {
        paymentsBody.innerHTML = '';
        paymentsEmpty.hidden = false;
        return;
    }

    const payments = await api.getPayments(selectedLoanId);
    if (payments.length === 0) {
        paymentsBody.innerHTML = '';
        paymentsEmpty.hidden = false;
        return;
    }

    paymentsEmpty.hidden = true;
    paymentsBody.innerHTML = payments.map(p => {
        const cross = p.currency !== p.loan_currency;
        const converted = p.amount * p.exchange_rate;
        return `
            <tr>
                <td><strong>${formatCurrency(p.amount, p.currency)}</strong></td>
                <td>${p.currency}</td>
                <td>${cross ? p.exchange_rate.toFixed(4) : '—'}</td>
                <td>${cross ? formatCurrency(converted, p.loan_currency) : '—'}</td>
                <td>${formatDate(p.paid_at)}</td>
            </tr>
        `;
    }).join('');
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

/* Row clicks */
document.getElementById('view-root').addEventListener('click', (event) => {
    const borrowerRow = event.target.closest('[data-borrower]');
    if (borrowerRow) {
        showDetail(borrowerRow.dataset.borrower);
        return;
    }
    const loanRow = event.target.closest('[data-loan-id]');
    if (loanRow) {
        selectedLoanId = parseInt(loanRow.dataset.loanId);
        loadDetail();
        return;
    }
});

document.addEventListener('keydown', (event) => {
    const modal = document.getElementById('loan_modal');
    if (event.key === 'Escape' && modal && !modal.hidden) closeLoanModal();
});

(async () => {
    await loadViews();
    await initModal();
    await showList();
})();