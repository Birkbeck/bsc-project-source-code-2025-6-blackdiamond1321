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
        const user = await api.me();
        showUser(user);
    } catch {
        /* If token rejected, clear token and redirect landing */
        api.token.clear();
        window.location.href = '/';
    }
};

/* Show user name on dashboard in nav */
const showUser = (user) => {
    const el = document.getElementById('user_name');
    if (el) el.textContent = `Hi, ${user.first_name}`;
};

checkAuth();