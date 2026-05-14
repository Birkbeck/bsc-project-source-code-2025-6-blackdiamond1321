/* FinTrack dashboard */

/* Show current date on dashboard */
const showDate = () => {
    const el = document.getElementById('dashboard_date');
    if (!el) return;
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    el.textContent = new Date().toLocaleDateString('en-GB', options);
};

showDate();
