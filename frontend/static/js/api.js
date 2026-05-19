/* FinTrack API client */

const API_BASE = '/api';

/* Token storage */
class TokenStore {
    #key = 'fintrack_token';

    get(){ return localStorage.getItem(this.#key); }
    set(token){ localStorage.setItem(this.#key, token); }
    clear(){ localStorage.removeItem(this.#key); }
}

const token = new TokenStore();

/* Request error */
export class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
    }
}

/* Headers builder */
const buildHeaders = (extra = {}) => {
    const headers = { ...extra };
    const t = token.get();
    if (t) headers.Authorization = `Bearer ${t}`;
    return headers;
};

/* Response parser */
const parseResponse = async (response) => {
    const data = await response.json().catch(() => null);

    if (!response.ok) {
        let detail = data?.detail;
        /* FastAPI validation errors */
        if (Array.isArray(detail)) {
            detail = detail.map(e => e.msg || JSON.stringify(e)).join('; ');
        }
        throw new ApiError(
            detail ?? `Request failed (${response.status})`,
            response.status
        );
    }
    return data;
};

/* JSON request */
const apiJson = async (path, { method = 'GET', body } = {}) => {
    const response = await fetch(API_BASE + path, {
        method,
        headers: buildHeaders({
            'Content-Type': 'application/json'
        }),
        body: body ? JSON.stringify(body) : null
    });
    return parseResponse(response);
};

/* Form-encoded request */
const apiForm = async (path, fields) => {
    const response = await fetch(API_BASE + path, {
        method: 'POST',
        headers: buildHeaders(),
        body: new URLSearchParams(fields)
    });
    return parseResponse(response);
};

/* Public API */
export const api = {
    /* Auth */
    register: (data) => apiJson('/users/register', {
        method: 'POST',
        body: data
    }),
    login: (email, password) => apiForm('/users/login', {
        username: email, password
    }),
    me: () => apiJson('/users/me'),
        updateProfile: (data) => apiJson('/users/me', {
        method: 'PUT',
        body: data,
    }),
    changePassword: (data) => apiJson('/users/me/password', {
        method: 'POST',
        body: data,
    }),
    deleteAccount: (data) => apiJson('/users/me', {
        method: 'DELETE',
        body: data,
    }),

    /* Password reset */
    forgotQuestion: (email) => apiJson('/users/forgot-question', {
        method: 'POST',
        body: { email }
    }),
    resetPassword: (email, answer, new_password) => apiJson('/users/reset-password', {
        method: 'POST',
        body: { email, answer, new_password }
    }),
    /* Transactions */
    getTransactions: () => apiJson('/transactions'),
    createTransaction: (data) => apiJson('/transactions', {
        method: 'POST',
        body: data
    }),
    updateTransaction: (id, data) => apiJson(`/transactions/${id}`, {
        method: 'PUT',
        body: data
    }),
    deleteTransaction: (id) => apiJson(`/transactions/${id}`, {
        method: 'DELETE'
    }),

    /* Payment sources */
    getPaymentSources: () => apiJson('/payment-sources'),
    createPaymentSource: (data) => apiJson('/payment-sources', {
        method: 'POST',
        body: data,
    }),
    updatePaymentSource: (id, data) => apiJson(`/payment-sources/${id}`, {
        method: 'PUT',
        body: data,
    }),
    deletePaymentSource: (id) => apiJson(`/payment-sources/${id}`, {
    method: 'DELETE'
    }),

    /* Budgets */
    getBudgets: () => apiJson('/budgets'),
    createBudget: (data) => apiJson('/budgets', { method: 'POST',
        body: data
    }),
    deleteBudget: (category) => apiJson(`/budgets/${encodeURIComponent(category)}`, {
        method: 'DELETE'
    }),
    /* Loans */
    getLoans: ()=> apiJson('/loans'),
    createLoan: (data) => apiJson('/loans', {
        method: 'POST',
        body: data
    }),
    /* Payments in loan */
    getPayments: (loanId) => apiJson(`/loans/${loanId}/payments`),
    createPayment: (loanId, data)  => apiJson(`/loans/${loanId}/payments`, {
        method: 'POST',
        body: data
    }),
    deleteLoan: (id) => apiJson(`/loans/${id}`, { method: 'DELETE' }),
    /* Download the summary PDF*/
    /* Download the summary PDF as a Blob (caller turns it into a save) */
    async downloadSummaryPdf(from, to) {
        const params = new URLSearchParams();
        if (from) params.set('date_from', from);
        if (to)   params.set('date_to', to);

        const r = await fetch(`${API_BASE}/summary/pdf?${params}`, {
            headers: buildHeaders(),
        });
        if (!r.ok) throw new ApiError(`PDF download failed (${r.status})`, r.status);
        return r.blob();
    },
    token
};