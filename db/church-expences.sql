-- Expense View
CREATE OR REPLACE VIEW church_expense_view AS
SELECT
    e.church_id,
    e.amount,
    e.date as transaction_date,
    e.spent_by,
    ec.category_name,
    ec.budget as category_budget,
    sp.church_name,
    EXTRACT(MONTH FROM e.date) as month,
    EXTRACT(YEAR FROM e.date) as year,
    TO_CHAR(e.date, 'Month') as month_name
FROM service_providers_expense e
JOIN service_providers_expensecategory ec ON e.expense_category_id = ec.id
JOIN service_provider_table sp ON e.church_id = sp.id;
