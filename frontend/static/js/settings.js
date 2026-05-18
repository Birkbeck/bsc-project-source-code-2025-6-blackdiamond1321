/* FinTrack settings */

import { api } from './api.js';

/* Fill the form with users details */
const loadProfile = async () => {
    const user = await api.me();
    document.querySelector('[name="first_name"]').value = user.first_name;
    document.querySelector('[name="last_name"]').value  = user.last_name;
    document.querySelector('[name="email"]').value      = user.email;
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

document.getElementById('profile_form').addEventListener('submit', handleProfileSubmit);

loadProfile();