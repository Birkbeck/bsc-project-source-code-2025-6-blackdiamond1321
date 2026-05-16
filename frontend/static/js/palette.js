/* Colour palette */

/* Categories */
export const CATEGORY_COLOURS = {
    /* Expense */
    'groceries': '#10b981',
    'food & dining': '#f97316',
    'transport': '#06b6d4',
    'bills': '#ef4444',
    'leisure': '#8b5cf6',
    'shopping': '#ec4899',
    'health': '#facc15',
    'subscriptions': '#3b82f6',
    /* Income */
    'salary': '#10b981',
    'freelance': '#06b6d4',
    'investment': '#8b5cf6',
    /* Income or Expense */
    'bank transfer': '#facc15',
    /* Other */
    'other': '#93c5fd',
    'total spending':  '#10b981',
};

export const EXPENSE_CATEGORIES = [
    'Groceries',
    'Food & Dining',
    'Transport',
    'Bills',
    'Leisure',
    'Shopping',
    'Health',
    'Subscriptions',
    'Bank Transfer',
    'Other',
];

export const INCOME_CATEGORIES = [
    'Salary',
    'Freelance',
    'Investment',
    'Bank Transfer',
    'Other',
];

export const getCategoryColour = (category) =>
    CATEGORY_COLOURS[category.toLowerCase()] ?? 'var(--muted)';