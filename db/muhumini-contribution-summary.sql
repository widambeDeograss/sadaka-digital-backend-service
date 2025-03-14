-- Create a comprehensive view for individual contributor (muhumini) contributions
CREATE OR REPLACE VIEW muhumini_contributions_view AS
WITH all_contributions AS (
    -- Zaka contributions through card numbers
    SELECT
        cn.mhumini_id,
        z.church_id,
        'Zaka' as contribution_type,
        'Regular Zaka' as contribution_detail,
        z.zaka_amount as amount,
        z.date as transaction_date,
        z.payment_type_id,
        NULL::numeric as pledge_amount,
        NULL::date as due_date
    FROM service_providers_zaka z
    JOIN service_providers_cardsnumber cn ON z.bahasha_id = cn.id
    WHERE cn.bahasha_type = 'zaka'

    UNION ALL

    -- Sadaka contributions through card numbers
    SELECT
        cn.mhumini_id,
        s.church_id,
        'Sadaka' as contribution_type,
        COALESCE(st.name, 'General Sadaka') as contribution_detail,
        s.sadaka_amount as amount,
        s.date as transaction_date,
        s.payment_type_id,
        NULL::numeric as pledge_amount,
        NULL::date as due_date
    FROM service_providers_sadaka s
    JOIN service_providers_cardsnumber cn ON s.bahasha_id = cn.id
    LEFT JOIN service_providers_sadakatypes st ON s.sadaka_type_id = st.id
    WHERE cn.bahasha_type = 'sadaka'

    UNION ALL

    -- Mchango payments
    SELECT
        mp.mhumini_id,
        m.church_id,
        'Mchango' as contribution_type,
        m.mchango_name as contribution_detail,
        mp.amount,
        mp.inserted_at::date as transaction_date,
        mp.payment_type_id,
        m.target_amount as pledge_amount,
        NULL::date as due_date
    FROM service_providers_mchangopayments mp
    JOIN service_providers_mchango m ON mp.mchango_id = m.id
    WHERE m.status = true

    UNION ALL

    -- Mavuno payments
    SELECT
        mp.mhumini_id,
        m.church_id,
        'Mavuno' as contribution_type,
        m.name as contribution_detail,
        mp.amount,
        mp.inserted_at::date as transaction_date,
        mp.payment_type_id,
        m.year_target_amount as pledge_amount,
        NULL::date as due_date
    FROM service_providers_mavunopayments mp
    JOIN service_providers_mavuno m ON mp.mavuno_id = m.id
    WHERE m.status = true

    UNION ALL

    -- Ahadi payments
    SELECT
        ap.mhumini_id,
        a.church_id,
        'Ahadi' as contribution_type,
        COALESCE(m.mchango_name, 'General Pledge') as contribution_detail,
        ap.amount,
        ap.inserted_at::date as transaction_date,
        ap.payment_type_id,
        a.amount as pledge_amount,
        a.due_date
    FROM service_providers_ahadipayments ap
    JOIN service_providers_ahadi a ON ap.ahadi_id = a.id
    LEFT JOIN service_providers_mchango m ON a.mchango_id = m.id
)
SELECT
    ac.*,
    w.first_name,
    w.last_name,
    w.phone_number,
    w.email,
    w.gender,
    j.name as jumuiya_name,
    k.name as kanda_name,
    sp.church_name,
    pt.name as payment_type_name,
    EXTRACT(MONTH FROM ac.transaction_date) as month,
    EXTRACT(YEAR FROM ac.transaction_date) as year,
    TO_CHAR(ac.transaction_date, 'Month') as month_name
FROM all_contributions ac
JOIN service_providers_wahumini w ON ac.mhumini_id = w.id
LEFT JOIN service_providers_jumuiya j ON w.jumuiya_id = j.id
LEFT JOIN service_providers_kanda k ON j.kanda_id = k.id
JOIN service_provider_table sp ON ac.church_id = sp.id
JOIN service_providers_paymenttype pt ON ac.payment_type_id = pt.id;

-- Create a summary view for quick totals
CREATE OR REPLACE VIEW muhumini_contribution_summary_view AS
SELECT
    mhumini_id,
    church_id,
    first_name,
    last_name,
    jumuiya_name,
    kanda_name,
    contribution_type,
    year,
    month_name,
    SUM(amount) as total_amount,
    COUNT(*) as number_of_contributions
FROM muhumini_contributions_view
GROUP BY
    mhumini_id,
    church_id,
    first_name,
    last_name,
    jumuiya_name,
    kanda_name,
    contribution_type,
    year,
    month,
    month_name
ORDER BY
    year,
    month;