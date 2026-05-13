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
    if (form.id === 'forgot_step1_form')  await forgotStep1(form);
    if (form.id === 'forgot_step2_form')  await forgotStep2(form);
});

/* Show an error message */
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

/* Forgot password */
/* Step 1 */
const forgotStep1 = async (form) => {
    const data = readForm(form);
    try {
        const result = await api.forgotQuestion(data.email);

        /* Show question, hide step 1 form, reveal step 2 form */
        document.getElementById('forgot_question').textContent = result.question;
        document.getElementById('forgot_step1_form').hidden = true;

        const step2 = document.getElementById('forgot_step2_form');
        step2.hidden = false;
        step2.dataset.email = data.email;
    } catch (err) {
        showError(form, err.message);
    }
};

/* Step 2 */
const forgotStep2 = async (form) => {
    const data = readForm(form);
    const email = form.dataset.email;
    try {
        await api.resetPassword(email, data.answer, data.new_password);
        openModal('login');
    } catch (err) {
        showError(form, err.message);
    }
};

/* Password requirements */
modalRoot.addEventListener('input', (event) => {
    if (event.target.name !== 'password' && event.target.name !== 'new_password') return;

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
            /* Empty field */
            li.classList.remove('valid', 'invalid');
        } else {
            /* User has followed rules */
            li.classList.toggle('valid', ok);
            li.classList.toggle('invalid', !ok);
        }
    }
});

modalRoot.addEventListener('click', (event) => {

    /* Go to forgot password from login */
    if (event.target.id === 'go_to_forgot') {
        event.preventDefault();
        openModal('forgot');
        return;
    }

    /* Go to login from forgot password */
    if (event.target.id === 'go_to_login_from_forgot') {
        event.preventDefault();
        openModal('login');
        return;
    }
});