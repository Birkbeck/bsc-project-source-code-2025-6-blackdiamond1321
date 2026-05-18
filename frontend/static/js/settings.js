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

document.getElementById('password_form').addEventListener('submit', handlePasswordSubmit);

document.getElementById('profile_form').addEventListener('submit', handleProfileSubmit);

loadProfile();