/* Format currency and date for all pages */

/* Format a number as GBP  */
export const formatCurrency = (amount, currency = 'GBP') => {
    return new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency,
        currencyDisplay: 'narrowSymbol'
    }).format(amount);
};

/* Format a date as to UK format instead of ISO. Short form e.g. 14/05/2026 */
export const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-GB');
};

/* Format a date as UK long form e.g. Thursday, 14 May 2026 */
export const formatDateLong = (date) => {
    return new Date(date).toLocaleDateString('en-GB', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    });
};