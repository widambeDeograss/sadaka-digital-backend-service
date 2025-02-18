CREATE OR REPLACE VIEW church_revenue_view AS
WITH all_revenues AS (
    -- Regular Revenue records
    SELECT
        church_id,
        amount,
        revenue_type,
        revenue_type_record,
        date_received as transaction_date,
        payment_type_id
    FROM revenue

    UNION ALL

    -- Sadaka records with specific types
    SELECT
        s.church_id,
        s.sadaka_amount as amount,
        'sadaka' as revenue_type,
        CASE
            WHEN st.name IS NOT NULL THEN st.name
            ELSE 'general_sadaka'
        END as revenue_type_record,
        s.date as transaction_date,
        s.payment_type_id
    FROM sadaka s
    LEFT JOIN sadaka_types st ON s.sadaka_type_id = st.id

    UNION ALL

    -- Zaka records
    SELECT
        church_id,
        zaka_amount as amount,
        'zaka' as revenue_type,
        'zaka_payment' as revenue_type_record,
        date as transaction_date,
        payment_type_id
    FROM zaka

    UNION ALL

    -- Mchango payments with specific mchango records
    SELECT
        m.church_id,
        mp.amount,
        'mchango' as revenue_type,
        CASE
            WHEN m.mchango_name IS NOT NULL THEN m.mchango_name
            ELSE 'general_mchango'
        END as revenue_type_record,
        mp.inserted_at::date as transaction_date,
        mp.payment_type_id
    FROM mchango_payments mp
    JOIN mchango m ON mp.mchango_id = m.id
    WHERE m.status = true

    UNION ALL

    -- Mavuno payments with specific mavuno records
    SELECT
        m.church_id,
        mp.amount,
        'mavuno' as revenue_type,
        CASE
            WHEN m.name IS NOT NULL THEN m.name
            ELSE 'general_mavuno'
        END as revenue_type_record,
        mp.inserted_at::date as transaction_date,
        mp.payment_type_id
    FROM mavuno_payments mp
    JOIN mavuno m ON mp.mavuno_id = m.id
    WHERE m.status = true
)
SELECT
    ar.church_id,
    ar.amount,
    ar.revenue_type,
    ar.revenue_type_record,
    ar.transaction_date,
    ar.payment_type_id,
    sp.church_name,
    pt.name as payment_type_name,
    EXTRACT(MONTH FROM ar.transaction_date) as month,
    EXTRACT(YEAR FROM ar.transaction_date) as year,
    TO_CHAR(ar.transaction_date, 'Month') as month_name
FROM all_revenues ar
JOIN service_provider_table sp ON ar.church_id = sp.id
JOIN payment_type pt ON ar.payment_type_id = pt.id;