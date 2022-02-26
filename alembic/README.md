Generic single-database configuration.

## migration test commands
- `select count(*) from price_actions where price_date='2022-02-25';`
- `delete from price_actions  where price_date='2022-02-25';`
- `select count(*) from shortlisted_stocks where conditions_met_on='2022-02-25';`
- `delete from shortlisted_stocks where conditions_met_on='2022-02-25';`
- `select count(*) from stock_names where created_at > '2022-02-25 00:00:00.000000';`
- `delete from stock_names where created_at > '2022-02-25 00:00:00.000000';`

