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
        throw new ApiError(
            data?.detail ?? `Request failed (${response.status})`,
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

    /* Payment sources */
    getPaymentSources: () => apiJson('/payment-sources'),
    token
};