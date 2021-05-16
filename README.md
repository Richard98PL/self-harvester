#HOW DO I WORK

I check weekly fluctuation of selected cryptocurrency once a day via coinmarketcapAPI and then I compare it with the fluctuation threshold set.
basically automated buy low, sell high, that's it

self-harvester https://github.com/Richard98PL/self-harvester

HOSTED ON HEROKU https://dashboard.heroku.com/

using binance API https://www.binance.com/en

using coinamrketcap API https://coinmarketcap.com/

scheduled for daily execution with Advanced Scheduler (heroku) https://app.advancedscheduler.io/

db: clearDB MySQL (heroku) https://www.cleardb.com/
___________________________________

Configure which cryptocurrency you want to focus on

Configure your weekly fluctuation threshold

logs/api_keys stored in MySQL

logs query - SELECT Id,Log FROM Logs ORDER BY Id DESC
___________________________________
PROJECT STARTED 16.05.2021

Starting asset: €34.54
