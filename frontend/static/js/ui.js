/* FinTrack UI */
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