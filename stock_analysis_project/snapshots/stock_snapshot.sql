{% snapshot stock_snapshot %}
{{
    config(
      target_schema='snapshots',
      unique_key='symbol || date',
      strategy='check',
      check_cols=['close']
    )
}}

select * from {{ ref('raw_stock_data') }}

{% endsnapshot %}
