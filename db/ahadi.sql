CREATE OR REPLACE VIEW church_pledges_view AS
SELECT
    a.church_id,
    a.id as ahadi_id,
    a.wahumini_id,
    a.amount as pledged_amount,
    COALESCE(SUM(ap.amount), 0) as total_paid_amount,
    a.amount - COALESCE(SUM(ap.amount), 0) as remaining_amount,
    a.date_pledged,
    a.due_date,
    w.first_name || ' ' || w.last_name as wahumini_name,
    w.phone_number as wahumini_phone,
    COALESCE(m.mchango_name, 'General Pledge') as pledge_purpose,
    sp.church_name,
    j.name as jumuiya_name,
    k.name as kanda_name,
    EXTRACT(MONTH FROM a.date_pledged) as month,
    EXTRACT(YEAR FROM a.date_pledged) as year,
    TO_CHAR(a.date_pledged, 'Month') as month_name,
    CASE
        WHEN a.due_date < CURRENT_DATE AND (a.amount - COALESCE(SUM(ap.amount), 0)) > 0 THEN 'Overdue'
        WHEN a.amount - COALESCE(SUM(ap.amount), 0) = 0 THEN 'Completed'
        ELSE 'Active'
    END as pledge_status,
    CASE
        WHEN a.amount = COALESCE(SUM(ap.amount), 0) THEN 100
        ELSE ROUND((COALESCE(SUM(ap.amount), 0) * 100.0 / NULLIF(a.amount, 0)), 2)
    END as completion_percentage
FROM ahadi a
JOIN wahumini w ON a.wahumini_id = w.id
LEFT JOIN mchango m ON a.mchango_id = m.id
JOIN service_provider_table sp ON a.church_id = sp.id
LEFT JOIN jumuiya j ON w.jumuiya_id = j.id
LEFT JOIN kanda k ON j.kanda_id = k.id
LEFT JOIN ahadi_payments ap ON a.id = ap.ahadi_id
GROUP BY
    a.id,
    a.church_id,
    a.wahumini_id,
    a.amount,
    a.date_pledged,
    a.due_date,
    w.first_name,
    w.last_name,
    w.phone_number,
    m.mchango_name,
    sp.church_name,
    j.name,
    k.name;

-- Create a detailed payments view for each pledge
CREATE OR REPLACE VIEW church_pledge_payments_view AS
SELECT
    ap.ahadi_id,
    ap.amount as payment_amount,
    ap.inserted_at as payment_date,
    pt.name as payment_type,
    ap.inserted_by,
    a.church_id,
    w.first_name || ' ' || w.last_name as wahumini_name,
    COALESCE(m.mchango_name, 'General Pledge') as pledge_purpose,
    j.name as jumuiya_name,
    EXTRACT(MONTH FROM ap.inserted_at) as month,
    EXTRACT(YEAR FROM ap.inserted_at) as year,
    TO_CHAR(ap.inserted_at, 'Month') as month_name
FROM ahadi_payments ap
JOIN ahadi a ON ap.ahadi_id = a.id
JOIN wahumini w ON ap.mhumini_id = w.id
LEFT JOIN mchango m ON a.mchango_id = m.id
LEFT JOIN jumuiya j ON w.jumuiya_id = j.id
JOIN payment_type pt ON ap.payment_type_id = pt.id;