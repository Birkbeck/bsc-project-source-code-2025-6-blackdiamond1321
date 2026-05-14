/* FinTrack dashboard */

/* Show current date on dashboard */
import {formatDateLong} from "./format.js";

const showDate = () => {
    const el = document.getElementById('dashboard_date');
    if (!el) return;
    el.textContent = formatDateLong(new Date());
};

showDate();
