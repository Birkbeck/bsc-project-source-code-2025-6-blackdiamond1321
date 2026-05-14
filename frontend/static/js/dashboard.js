/* FinTrack dashboard */

import { api } from './api.js';

/* If not logged in (no valid token), send back to the landing page. */
const checkAuth = async () => {
    /* No token redirect to landing */
    if (!api.token.get()) {
        window.location.href = '/';
        return;
    }

    /* If token exists. Check it is still valid */
    try {
        await api.me();
    } catch {
        /* If token rejected, clear token and redirect landing */
        api.token.clear();
        window.location.href = '/';
    }
};

checkAuth();