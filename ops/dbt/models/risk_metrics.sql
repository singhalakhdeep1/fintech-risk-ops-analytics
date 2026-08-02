-- dbt model for risk metrics in fintech-risk-ops-analytics

with risk_transactions as (
    select
        transaction_id,
        user_id,
        amount,
        transaction_type,
        risk_score,
        timestamp
    from {{ source('raw', 'risk_transactions') }}
),

risk_aggregates as (
    select
        date_trunc('day', timestamp) as risk_date,
        transaction_type,
        count(*) as transaction_count,
        sum(amount) as total_amount,
        avg(risk_score) as avg_risk_score,
        max(risk_score) as max_risk_score,
        count(case when risk_score > 0.8 then 1 end) as high_risk_count
    from risk_transactions
    group by
        date_trunc('day', timestamp),
        transaction_type
)

select
    risk_date,
    transaction_type,
    transaction_count,
    total_amount,
    avg_risk_score,
    max_risk_score,
    high_risk_count,
    (high_risk_count::float / transaction_count) * 100 as high_risk_percentage
from risk_aggregates
order by risk_date desc, transaction_type
