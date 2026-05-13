/* FinTrack UI */

import { api } from './api.js';

/* Modal open, close, and switch */
const modalRoot = document.getElementById('modal-root');

/* Load a code from /modals/{modal_name} and put it into modal-root */
const openModal = async (name) => {
    const response = await fetch(`/modals/${name}`);
    const html = await response.text();
    modalRoot.innerHTML = html;
};

/* Empty modal-root to remove any open modal */
const closeModal = () => {
    modalRoot.innerHTML = '';
};

/* Actions for buttons in the landing page */

document.getElementById('login_btn')?.addEventListener('click', () => openModal('login'));
document.getElementById('register_btn')?.addEventListener('click', () => openModal('register'));
document.getElementById('get_str_btn')?.addEventListener('click', () => openModal('register'));

/* Click actions inside modals */

modalRoot.addEventListener('click', (event) => {
    /* Click on the dark overlay (not its children) → close */
    if (event.target.classList.contains('modal-overlay')) {
        closeModal();
        return;
    }

    /* Click the 'x' button to close */
    if (event.target.closest('.modal-close')) {
        closeModal();
        return;
    }

    /* Go to register modal from login modal */
    if (event.target.id === 'go_to_register') {
        event.preventDefault();
        openModal('register');
        return;
    }

    /* Go to login modal from register modal */
    if (event.target.id === 'go_to_login') {
        event.preventDefault();
        openModal('login');
        return;
    }
});

/* Escape key closes any open modal */

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeModal();
});

/* Form submission */

modalRoot.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.target;

    if (form.id === 'login_form')    await loginUser(form);
    if (form.id === 'register_form') await registerUser(form);
});

/* Show an error message inside */
const showError = (form, message) => {
    const errorDiv = form.querySelector('.modal-error');
    if (!errorDiv) return;
    errorDiv.textContent = message;
    errorDiv.hidden = false;
};

/* Read form fields */
const readForm = (form) => Object.fromEntries(new FormData(form));

const loginUser = async (form) => {
    const data = readForm(form);
    try {
        const result = await api.login(data.email, data.password);
        api.token.set(result.access_token);
        closeModal();
    } catch (err) {
        showError(form, err.message);
    }
};

const registerUser = async (form) => {
    const data = readForm(form);
    try {
        const result = await api.register(data);
        api.token.set(result.access_token);
        closeModal();
    } catch (err) {
        showError(form, err.message);
    }
};

/* Live password requirements — three states: untouched (○), failed (✗), passed (✓) */
modalRoot.addEventListener('input', (event) => {
    if (event.target.name !== 'password') return;

    const rules = event.target.closest('.field')?.querySelector('.password-rules');
    if (!rules) return;

    const value = event.target.value;
    const checks = {
        length:  value.length >= 8,
        symbol:  /[^a-zA-Z0-9]/.test(value),
        capital: /[A-Z]/.test(value),
        digit:   /[0-9]/.test(value),
    };

    for (const [rule, ok] of Object.entries(checks)) {
        const li = rules.querySelector(`[data-rule="${rule}"]`);
        if (!li) continue;

        if (value.length === 0) {
            /* Empty field — reset to neutral state (○) */
            li.classList.remove('valid', 'invalid');
        } else {
            /* User has typed — show pass or fail */
            li.classList.toggle('valid', ok);
            li.classList.toggle('invalid', !ok);
        }
    }
});