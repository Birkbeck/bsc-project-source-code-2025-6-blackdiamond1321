/* FinTrack settings */

import { api } from './api.js';

/* Fill the form with users details */
const loadProfile = async () => {
    const user = await api.me();
    document.querySelector('[name="first_name"]').value = user.first_name;
    document.querySelector('[name="last_name"]').value = user.last_name;
    document.querySelector('[name="email"]').value = user.email;
    updateTfaUI(user.totp_enabled);
};

/* Change profile details */
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

/* Payment Methods */

/* List payment methods */
const loadPaymentMethods = async () => {
    const sources = await api.getPaymentSources();
    const list = document.getElementById('ps_list');

    if (sources.length === 0) {
        list.innerHTML = '<p style="color:var(--text2); font-size:13px; padding:8px 0">No payment methods yet — add your first one below.</p>';
        return;
    }

    list.innerHTML = sources.map(s => `
        <div class="ps-row" data-id="${s.id}">
            <input class="form-input ps-name" data-id="${s.id}" value="${s.name}">
            <button class="btn btn--secondary btn--small ps-rename" data-id="${s.id}">Rename</button>
            <button class="btn btn--danger btn--small ps-delete" data-id="${s.id}">Delete</button>
        </div>
    `).join('');

    /* Rename buttons */
    list.querySelectorAll('.ps-rename').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const input = list.querySelector(`.ps-name[data-id="${id}"]`);
            try {
                await api.updatePaymentSource(id, { name: input.value.trim() });
                loadPaymentMethods();
            } catch (err) {
                alert('Rename failed: ' + err.message);
            }
        });
    });

    /* Delete buttons */
    list.querySelectorAll('.ps-delete').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Delete this payment method? Existing transactions keep their old method label.')) return;
            try {
                await api.deletePaymentSource(btn.dataset.id);
                loadPaymentMethods();
            } catch (err) {
                alert('Delete failed: ' + err.message);
            }
        });
    });
};

/* Add new */
document.getElementById('ps_form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = document.getElementById('ps_msg');
    const input = document.querySelector('[name="ps_name"]');
    msg.textContent = '';
    msg.className = 'settings-msg';

    try {
        await api.createPaymentSource({ name: input.value.trim() });
        input.value = '';
        loadPaymentMethods();
    } catch (err) {
        msg.textContent = err.message;
        msg.classList.add('settings-msg--error');
    }
});

/* 2FA */

/* Change the status between enabled/disabled */
const updateTfaUI = (enabled) => {
    const status = document.getElementById('tfa_status');
    const enableBtn = document.getElementById('tfa_enable_btn');
    const disableBtn = document.getElementById('tfa_disable_btn');
    if (enabled) {
        status.textContent = 'ENABLED';
        status.className = 'badge badge--paid';
        enableBtn.hidden = true;
        disableBtn.hidden = false;
    } else {
        status.textContent = 'DISABLED';
        status.className = 'badge badge--unpaid';
        enableBtn.hidden = false;
        disableBtn.hidden = true;
    }
};

/* Open the setup modal */
document.getElementById('tfa_enable_btn').addEventListener('click', async () => {
    try {
        if (!root.querySelector('#tfa_setup_modal')) {
            const html = await fetch('/modals/2fa-setup').then(r => r.text());
            root.insertAdjacentHTML('beforeend', html);
            wireTfaSetupModal();
        }
        const { secret, qr_data_url } = await api.setup2FA();
        document.getElementById('tfa_qr').src        = qr_data_url;
        document.getElementById('tfa_secret').value  = secret;
        document.getElementById('tfa_setup_code').value = '';
        document.getElementById('tfa_setup_error').hidden = true;
        document.getElementById('tfa_setup_modal').hidden = false;
    } catch (err) {
        alert('Setup failed: ' + err.message);
    }
});

const wireTfaSetupModal = () => {
    const modal = document.getElementById('tfa_setup_modal');
    modal.querySelectorAll('[data-close-modal]').forEach(el => {
        el.addEventListener('click', () => { modal.hidden = true; });
    });
    modal.addEventListener('click', e => {
        if (e.target === modal) modal.hidden = true;
    });

    document.getElementById('tfa_setup_verify_btn').addEventListener('click', async () => {
        const code = document.getElementById('tfa_setup_code').value.trim().replace(/\s+/g, '');
        const error = document.getElementById('tfa_setup_error');
        error.hidden = true;
        try {
            const { recovery_codes } = await api.enable2FA(code);
            modal.hidden = true;
            await showBackupCodes(recovery_codes);
            updateTfaUI(true);
        } catch (err) {
            error.textContent = err.message;
            error.hidden = false;
        }
    });
};

/* Show the recovery codes */
const showBackupCodes = async (codes) => {
    if (!root.querySelector('#tfa_backup_modal')) {
        const html = await fetch('/modals/2fa-codes').then(r => r.text());
        root.insertAdjacentHTML('beforeend', html);
        document.getElementById('tfa_backup_done_btn').addEventListener('click', () => {
            document.getElementById('tfa_backup_modal').hidden = true;
        });
    }
    document.getElementById('tfa_backup_codes').textContent = codes.join('\n');
    document.getElementById('tfa_backup_modal').hidden = false;
};

/* Open the disable modal */
document.getElementById('tfa_disable_btn').addEventListener('click', async () => {
    if (!root.querySelector('#tfa_disable_modal')) {
        const html = await fetch('/modals/2fa-disable').then(r => r.text());
        root.insertAdjacentHTML('beforeend', html);
        wireTfaDisableModal();
    }
    document.getElementById('tfa_disable_form').reset();
    document.getElementById('tfa_disable_error').hidden = true;
    document.getElementById('tfa_disable_modal').hidden = false;
});

const wireTfaDisableModal = () => {
    const modal = document.getElementById('tfa_disable_modal');
    modal.querySelectorAll('[data-close-modal]').forEach(el => {
        el.addEventListener('click', () => { modal.hidden = true; });
    });
    modal.addEventListener('click', e => {
        if (e.target === modal) modal.hidden = true;
    });

    document.getElementById('tfa_disable_form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const error = document.getElementById('tfa_disable_error');
        error.hidden = true;
        try {
            await api.disable2FA({
                password: document.querySelector('[name="tfa_disable_password"]').value,
                code:     document.querySelector('[name="tfa_disable_code"]').value,
            });
            modal.hidden = true;
            updateTfaUI(false);
        } catch (err) {
            error.textContent = err.message;
            error.hidden = false;
        }
    });
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

loadPaymentMethods();
loadProfile();