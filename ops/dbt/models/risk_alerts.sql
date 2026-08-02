-- dbt model for risk alerts in fintech-risk-ops-analytics

with risk_thresholds as (
    select
        transaction_type,
        percentile_cont(0.95) within group (order by risk_score) as p95_risk_score
    from {{ source('raw', 'risk_transactions') }}
    group by transaction_type
),

high_risk_transactions as (
    select
        rt.transaction_id,
        rt.user_id,
        rt.amount,
        rt.transaction_type,
        rt.risk_score,
        rt.timestamp,
        rt.p95_risk_score
    from {{ source('raw', 'risk_transactions') }} rt
    join risk_thresholds rt_t
        on rt.transaction_type = rt_t.transaction_type
    where rt.risk_score > rt_t.p95_risk_score
)

select
    transaction_id,
    user_id,
    amount,
    transaction_type,
    risk_score,
    p95_risk_score,
    timestamp,
    'HIGH_RISK' as alert_type,
    'Risk score exceeds 95th percentile' as alert_message
from high_risk_transactions
order by risk_score desc
