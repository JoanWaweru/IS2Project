import snscrape.modules.twitter as sntwitter
import pandas as pd

query = "(@Safaricom_Care) until:2022-10-24"
tweets = []
limits = 5000
for tweet in sntwitter.TwitterSearchScraper(query).get_items():
  #print(vars(tweet))
  #break
  if len(tweets) == limits:
    break
  else:
    tweets.append([tweet.date, tweet.user.username,tweet.content])

df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet'])
df.to_csv('safaricomDataset.csv')
