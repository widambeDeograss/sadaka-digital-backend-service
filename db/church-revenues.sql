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
    FROM service_providers_revenue

    UNION ALL

    -- Sadaka records with specific types
    SELECT
        s.church_id,
        s.sadaka_amount as amount,
        'Sadaka' as revenue_type,
        CASE
            WHEN st.name IS NOT NULL THEN st.name
            ELSE 'general_sadaka'
        END as revenue_type_record,
        s.date as transaction_date,
        s.payment_type_id
    FROM service_providers_sadaka s
    LEFT JOIN service_providers_sadakatypes st ON s.sadaka_type_id = st.id

    UNION ALL

    -- Zaka records
    SELECT
        church_id,
        zaka_amount as amount,
        'Zaka' as revenue_type,
        'Zaka' as revenue_type_record,
        date as transaction_date,
        payment_type_id
    FROM service_providers_zaka

    UNION ALL

    -- Mchango payments with specific mchango records
    SELECT
        m.church_id,
        mp.amount,
        'Michango' as revenue_type,
        CASE
            WHEN m.mchango_name IS NOT NULL THEN m.mchango_name
            ELSE 'general_mchango'
        END as revenue_type_record,
        mp.inserted_at::date as transaction_date,
        mp.payment_type_id
    FROM service_providers_mchangopayments mp
    JOIN service_providers_mchango m ON mp.mchango_id = m.id
    WHERE m.status = true

    UNION ALL

    -- Mavuno payments with specific mavuno records
    SELECT
        m.church_id,
        mp.amount,
        'Mavuno' as revenue_type,
        CASE
            WHEN m.name IS NOT NULL THEN m.name
            ELSE 'general_mavuno'
        END as revenue_type_record,
        mp.inserted_at::date as transaction_date,
        mp.payment_type_id
    FROM service_providers_mavunopayments mp
    JOIN service_providers_mavuno m ON mp.mavuno_id = m.id
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
JOIN service_providers_paymenttype pt ON ar.payment_type_id = pt.id;