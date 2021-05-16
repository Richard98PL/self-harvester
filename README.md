#HOW DO I WORK
I check weekly fluctuation of selected cryptocurrency via coinmarketcapAPI and then I compare it with the fluctuation threshold set.
basically automated buy low, sell high, that's it

self-harvester

HOSTED ON HEROKU

using binance API

using coinamrketcap API

Configure which cryptocurrency you want to focus on

Configure your weekly fluctuation threshold

logs/api_keys stored in MySQL

scheduled for daily execution with Advanced Scheduler (heroku)

db: clearDB MySQL (heroku)


logs query - SELECT Id,Log FROM Logs ORDER BY Id DESC
