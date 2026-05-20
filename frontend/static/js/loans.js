/* FinTrack loans */

import { api } from './api.js';
import { formatCurrency, formatDate } from './format.js';
import { RING_COLOURS } from './palette.js';

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
                <td>${formatCurrency(r.principal, r.currency)}</td>
                <td>${formatCurrency(r.due, r.currency)}</td>
                <td style="color:var(--accent)">${formatCurrency(r.paid, r.currency)}</td>
                <td style="color:var(--red)">${formatCurrency(remaining, r.currency)}</td>
                <td>${badge(status)}</td>
            </tr>
        `;
    }).join('');

    displayRings(rows);
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
    document.getElementById('add_payment_btn').addEventListener('click', openPaymentModal);
    document.getElementById('delete_loan_btn').addEventListener('click', handleDeleteLoan);
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

    displayBar(loans);

    /* Action buttons need a selected loan */
    document.getElementById('add_payment_btn').disabled = !selectedLoanId;
    document.getElementById('delete_loan_btn').disabled = !selectedLoanId;

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
    const [loanHtml, paymentHtml] = await Promise.all([
        fetch('/modals/loan').then(r => r.text()),
        fetch('/modals/payment').then(r => r.text()),
    ]);

    document.getElementById('modal-root').innerHTML = loanHtml + paymentHtml;

    /* Loan modal */
    document.getElementById('loan_close').addEventListener('click', closeLoanModal);
    document.getElementById('loan_modal').addEventListener('click', e => {
        if (e.target.id === 'loan_modal') closeLoanModal();
    });

    document.getElementById('loan_form').addEventListener('submit', handleLoanSubmit);

    /* Payment modal */
    document.getElementById('payment_close').addEventListener('click', closePaymentModal);
    document.getElementById('payment_modal').addEventListener('click', e => {
        if (e.target.id === 'payment_modal') closePaymentModal();
    });

    document.getElementById('payment_form').addEventListener('submit', handlePaymentSubmit);
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

/* Payment modal */

const openPaymentModal = () => {
    if (!selectedLoanId) return;
    const loan = cachedLoans.find(l => l.id === selectedLoanId);

    document.getElementById('payment_subtitle').textContent =
        `Against loan to ${loan.borrower}`;
    document.querySelector('#payment_form [name="currency"]').value = loan.currency;
    document.querySelector('#payment_form [name="paid_at"]').value = new Date().toISOString().slice(0, 10);
    document.getElementById('payment_modal').hidden = false;
};

const closePaymentModal = () => {
    document.getElementById('payment_form').reset();
    document.getElementById('payment_error').hidden = true;
    document.getElementById('payment_modal').hidden = true;
};

const handlePaymentSubmit = async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    data.amount = parseFloat(data.amount);
    data.exchange_rate = parseFloat(data.exchange_rate) || 1.0;

    try {
        await api.createPayment(selectedLoanId, data);
        closePaymentModal();
        await loadDetail();
    } catch (err) {
        const errorDiv = document.getElementById('payment_error');
        errorDiv.textContent = err.message;
        errorDiv.hidden = false;
    }
};

/* Delete loan */

const handleDeleteLoan = async () => {
    if (!selectedLoanId) return;
    const loan = cachedLoans.find(l => l.id === selectedLoanId);
    const ok = confirm(`Delete the loan to ${loan.borrower}? This will also delete all its payments.`);
    if (!ok) return;

    await api.deleteLoan(selectedLoanId);
    selectedLoanId = null;

    /* If this was the borrower's last loan, go back to the list */
    const remaining = (await api.getLoans()).filter(l => l.borrower === currentBorrower);
    if (remaining.length === 0) {
        await showList();
    } else {
        await loadDetail();
    }
};

/* Display 1 ring per borrower */
const displayRings = (rows) => {
    const card = document.getElementById('ring_card');
    if (rows.length === 0) {
        card.hidden = true;
        return;
    }
    card.hidden = false;

    /* Sum due and paid per borrower */
    const byName = {};
    for (const r of rows) {
        if (!byName[r.name]) byName[r.name] = { due: 0, paid: 0, currency: r.currency };
        byName[r.name].due  += r.due;
        byName[r.name].paid += r.paid;
    }

    document.getElementById('ring_grid').innerHTML = Object.entries(byName).map(([name, d], i) => {
        const pct = d.due > 0 ? Math.min(d.paid / d.due * 100, 100) : 0;
        const colour = RING_COLOURS[i % RING_COLOURS.length];
        return `
            <div class="ring-cell">
                <div class="ring" style="--pct:${pct}; --colour:${colour}">
                    <div class="ring-pct" style="color:${colour}">${Math.round(pct)}%</div>
                </div>
                <div class="ring-name">${name}</div>
                <div class="ring-amounts">${formatCurrency(d.paid, d.currency)} / ${formatCurrency(d.due, d.currency)}</div>
            </div>
        `;
    }).join('');
};

/* Display a horizontal bar per loan in the detail view */
const displayBar = (loans) => {
    const card = document.getElementById('bars_card');
    if (loans.length === 0) {
        card.hidden = true;
        return;
    }
    card.hidden = false;

    document.getElementById('bars').innerHTML = loans.map(l => {
        const due = l.principal * (1 + l.interest_rate / 100);
        const pct = due > 0 ? Math.min(l.amount_paid / due * 100, 100) : 0;
        const remaining = Math.max(due - l.amount_paid, 0);
        /* Colour shifts based on progress */
        const colour = pct >= 100 ? 'var(--accent)'
                     : pct >=  50 ? 'var(--cyan)'
                     : pct >=  25 ? '#f97316'
                     : 'var(--red)';
        return `
            <div class="loan-bar">
                <div class="loan-bar-head">${formatCurrency(l.amount_paid, l.currency)} / ${formatCurrency(due, l.currency)}</div>
                <div class="loan-bar-track">
                    <div class="loan-bar-fill" style="width:${pct}%; background:${colour}"></div>
                    <span class="loan-bar-pct">${pct.toFixed(0)}%</span>
                </div>
                <div class="loan-bar-caption">
                    ${pct >= 100 ? '✓ Fully paid' : 'Remaining: ' + formatCurrency(remaining, l.currency)}
                </div>
            </div>
        `;
    }).join('');
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
    if (event.key !== 'Escape') return;
    const lm = document.getElementById('loan_modal');
    const pm = document.getElementById('payment_modal');
    if (lm && !lm.hidden) closeLoanModal();
    if (pm && !pm.hidden) closePaymentModal();
});

(async () => {
    await loadViews();
    await initModal();
    await showList();
})();