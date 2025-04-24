select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select close
from USER_DB_BEETLE.analytics.stock_metrics
where close is null



      
    ) dbt_internal_test