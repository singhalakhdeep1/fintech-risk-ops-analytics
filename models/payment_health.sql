with base as (
    select *
    from sample_transactions
)

select
    region,
    count(*) as total_transactions,
    sum(case when status = 'succeeded' then 1 else 0 end) as successful_transactions,
    sum(case when status = 'failed' then 1 else 0 end) as failed_transactions,
    sum(case when fraud_flag = 'true' then 1 else 0 end) as fraud_transactions,
    sum(case when chargeback_flag = 'true' then 1 else 0 end) as chargeback_transactions
from base
group by region
