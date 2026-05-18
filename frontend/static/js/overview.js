/* FinTrack overview */

import { api } from './api.js';
import { formatCurrency } from './format.js';
import { displayMonthlyBars, displayCumulative } from './chart.js';

/* Load transactions + loans, then display the stat cards */
const load = async () => {
    const [transactions, loans] = await Promise.all([
        api.getTransactions(),
        api.getLoans(),
    ]);

    /* Date */
    const now = new Date();
    document.getElementById('dashboard_date').textContent =
        now.toLocaleDateString('en-GB', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });

    displayMonthlyBars(
        document.getElementById('monthly_bars'),
        buildMonthlyData(transactions),
    );
    
    displayCumulative(
        document.getElementById('cumulative_line'),
        buildCumulativeData(buildMonthlyData(transactions)),
    );

    displayStats(transactions, loans);
};

/* Incomes vs Expanses */
const buildMonthlyData = (transactions) => {
    const now = new Date();
    const months = [];

    /* sort from oldest to newest */
    for (let i = 5; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const ym = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        const label = d.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' });
        months.push({ ym, label, income: 0, expense: 0 });
    }

    for (const t of transactions) {
        const month = months.find(m => t.date.startsWith(m.ym));
        if (!month) continue;
        if (t.type === 'income') month.income  += t.amount;
        else month.expense += t.amount;
    }

    return months;
};

/* Cumulative savings */
const buildCumulativeData = (monthlyData) => {
    let total = 0;
    return monthlyData.map(m => {
        total += m.income - m.expense;
        return { label: m.label, value: total };
    });
};

/* Build the stat cards on the top row */
const displayStats = (transactions, loans) => {
    const now = new Date();
    /* Filter this month's transactions */
    const ym = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

    /* Sum this month's income and expenses */
    let monthIncome = 0, monthExpense = 0;
    for (const t of transactions) {
        if (!t.date.startsWith(ym)) continue;
        if (t.type === 'income') monthIncome += t.amount;
        else monthExpense += t.amount;
    }
    const monthSavings = monthIncome - monthExpense;

    /* Loans outstanding */
    const outstanding = loans.reduce(
        (sum, l) => sum + (l.principal - l.amount_paid), 0
    );

    document.getElementById('stat_cards').innerHTML = `
        <div class="stat-card">
            <div class="stat-card-label">Monthly Income</div>
            <div class="stat-card-value stat-card-value--income">${formatCurrency(monthIncome)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Monthly Expenses</div>
            <div class="stat-card-value stat-card-value--expense">${formatCurrency(monthExpense)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">This Month Savings</div>
            <div class="stat-card-value stat-card-value--net">${formatCurrency(monthSavings)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-label">Loans Outstanding</div>
            <div class="stat-card-value stat-card-value--expense">${formatCurrency(outstanding)}</div>
        </div>
    `;
};

load();