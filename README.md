# Winner Winner Cheater Finder

## Finding cheaters on PUBG using Bayesian inference

* __Background__ : There are a lot of cheaters on PUBG, and this problem has been prevalent even though PUBG has implemented multiple cheater prevention systems over the last few years. This has slashted the number of users significantly and also affected the company reputation.

* __Motivation__ : My motivation for my app was to help the general users detect cheaters quickly and effectively so that they can promptly report to the PUBG monitoring team to take action and prevent further spread of cheats.

* __Data acquisition__ : I used a Python code (scrape.py) based on Selenium and BeaufiulSoup to scrape PUBG.OP.GG website to obtain player history. I looked at the most 20 recent match history that each player has. Each record belongs to a match played by a certain user and contains features such as playtime, gametype (squad,duo,etc), number of kills, number of headshots, distances travelled and so on. Total # of records I was able to get was ~56,000, which represents 2,700+ users.
