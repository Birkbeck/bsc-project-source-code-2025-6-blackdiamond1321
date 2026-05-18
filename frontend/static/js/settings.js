/* FinTrack settings */

import { api } from './api.js';

/* Fill the form with users details */
const loadProfile = async () => {
    const user = await api.me();
    document.querySelector('[name="first_name"]').value = user.first_name;
    document.querySelector('[name="last_name"]').value = user.last_name;
    document.querySelector('[name="email"]').value = user.email;
};

/* Submit handler */
const handleProfileSubmit = async (e) => {
    e.preventDefault();
    const msg = document.getElementById('profile_msg');
    msg.textContent = '';
    msg.className = 'settings-msg';

    try {
        await api.updateProfile({
            first_name: document.querySelector('[name="first_name"]').value,
            last_name:  document.querySelector('[name="last_name"]').value,
            email:      document.querySelector('[name="email"]').value,
        });
        msg.textContent = 'Profile updated successfully';
        msg.classList.add('settings-msg--success');
    } catch (err) {
        msg.textContent = err.message;
        msg.classList.add('settings-msg--error');
    }
};
/* Password change */
const validateRules = (password) => {
    const checks = {
        len:    password.length >= 8,
        upper:  /[A-Z]/.test(password),
        digit:  /\d/.test(password),
        symbol: /[^A-Za-z0-9]/.test(password),
    };
    document.querySelectorAll('.password-rules li[data-rule]').forEach(li => {
        const rule = li.dataset.rule;
        li.classList.toggle('valid',   checks[rule]);
        li.classList.toggle('invalid', !checks[rule] && password.length > 0);
    });
};

document.querySelector('[name="new_password"]')
    .addEventListener('input', e => validateRules(e.target.value));

/* Submit handler */
const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    const msg = document.getElementById('password_msg');
    msg.textContent = '';
    msg.className = 'settings-msg';

    const current = document.querySelector('[name="current_password"]').value;
    const newPw   = document.querySelector('[name="new_password"]').value;
    const confirm = document.querySelector('[name="confirm_password"]').value;

    /* Check if password match */
    if (newPw !== confirm) {
        msg.textContent = 'New passwords do not match';
        msg.classList.add('settings-msg--error');
        return;
    }

    try {
        await api.changePassword({
            current_password: current,
            new_password: newPw,
        });
        msg.textContent = 'Password changed successfully';
        msg.classList.add('settings-msg--success');
        document.getElementById('password_form').reset();
        validateRules('');   // reset the rules indicators
    } catch (err) {
        msg.textContent = err.message;
        msg.classList.add('settings-msg--error');
    }
};

/* Delete account */

const root = document.getElementById('modal-root');

/* Open modal */
document.getElementById('delete_account_btn').addEventListener('click', async () => {
    if (!root.querySelector('#delete_modal')) {
        const html = await fetch('/modals/delete-account').then(r => r.text());
        root.insertAdjacentHTML('beforeend', html);
        wireDeleteModal();
    }
    document.getElementById('delete_modal').hidden = false;
});

const wireDeleteModal = () => {
    const modal = document.getElementById('delete_modal');

    modal.querySelectorAll('[data-close-modal]').forEach(el => {
        el.addEventListener('click', () => { modal.hidden = true; });
    });
    modal.addEventListener('click', e => {
        if (e.target === modal) modal.hidden = true;
    });

    document.getElementById('delete_form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const err = document.getElementById('delete_error');
        err.hidden = true;

        try {
            await api.deleteAccount({
                email: document.querySelector('[name="delete_email"]').value,
                password: document.querySelector('[name="delete_password"]').value,
            });
            api.token.clear();
            window.location.href = '/';
        } catch (e) {
            err.textContent = e.message;
            err.hidden = false;
        }
    });
};

document.getElementById('password_form').addEventListener('submit', handlePasswordSubmit);

document.getElementById('profile_form').addEventListener('submit', handleProfileSubmit);

loadProfile();