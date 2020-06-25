# Winner Winner Cheater Finder

## Finding cheaters on PUBG using Bayesian inference

* __Background__ : There are a lot of cheaters on PUBG, and this problem has been prevalent even though PUBG has implemented multiple cheater prevention systems over the last few years. This has slashted the number of users significantly and also affected the company reputation.

* __Motivation__ : My motivation for my app was to help the general users detect cheaters quickly and effectively so that they can promptly report to the PUBG monitoring team to take action and prevent further spread of cheats.

* __Data acquisition__ : I used a Python code (scrape.py) based on Selenium and BeaufiulSoup to scrape PUBG.OP.GG website to obtain player history. I looked at the most 20 recent match history that each player has. Each record belongs to a match played by a certain user and contains features such as playtime, gametype (squad,duo,etc), number of kills, number of headshots, distances travelled and so on. Total # of records I was able to get was ~56,000, which represents 2,700+ users. The users and matches to look for were randomly selected by using the offical PUBG API.

* __Data storage__ : The scraped data were stored in the Heroku SQL server and accessed by my web app using SQLALECHMY commands.

* __Validation data (cheater)__ : All of my data were not labeled, but for validation I was able to get ~20 cheater data. I got these 'cheater-labeled' data by going over the South Korean PUBG fan website (https://cafe.naver.com/playbattlegrounds). This was the only website where the official PUBG monitoring team responds to general users' complaints about cheating behaviors, and unfortunately their reponses are not alwways guaranteed so I had to go over hundrdes of posts myself.

* __Validation data (pro)__ : The question then can arise if my model would just catch those who happen to be good like pro gamers. So to validate my model behavior, I collected PUBG pro gamers data by manually looking up some of the well known pro gamers data (like chocoTaco) on PUBG.OP.GG.

* __Model__ 
  - __Challenge :__ Because players play on different times, I cannot simply use typical time series analysis. For example, let's assume *user A* played on 1/1/2020 and 1/3/2020 and *user B* played 1/2/2020 only. Also let's assume *user A* had made 0 kills on 1/1/2020 and 2 kills on 1/3/2020. Then, if *user B* made 10 kills on 1/2/2020, the model would say *user B* is suspicious because there is a sudden jump of kills from 0 to 10. However, this is not true because *user B* only has one instance of 10 kills and we are not sure if this user got beginner's luck or whatsoever. Thus we cannot simply merge all the data and try to look for anomalies. 

* __Building the app__ : I used flask to build the web app that is deployed on Heroku server at www.PUBG-CHEATER-FINDER.com . The "application.py" code contains all the lines of the code that were used to build the web app.
  - __Layout of the app__ : 
--
