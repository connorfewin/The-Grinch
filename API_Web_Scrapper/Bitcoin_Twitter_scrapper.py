import tweepy
from textblob import TextBlob
import re
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')
import twitterToken


def twitterScrapper(date, search, numOfTwts):
    # Date format ('2021-10-4')
    # Search format should be world in lowercase

    # Create authentication object
    authenticate = tweepy.OAuthHandler(twitterToken.consumerKey, twitterToken.consumerSecret)
    # Set access token and the access token secret
    authenticate.set_access_token(twitterToken.accessToken, twitterToken.accessTokenSecret)
    # Create the API object
    api = tweepy.API(authenticate, wait_on_rate_limit=True)

    # Gather 2000 tweets about Bitcoin and filter out any retweets
    search_term = '#' + search + ' -filter:retweets'
    # search_term = '#bitcoin -filter:retweets'
    # Create a cursor object
    # tweets = tweepy.Cursor(api.search, q=search_term, lang='en', since='2021-10-4', tweet_mode='extended').items(1000)
    #tweets = tweepy.Cursor(api.search, q=search_term, lang='en', since=date, tweet_mode='extended').items(numOfTwts)
    tweets = api.search_tweets(q=search_term, lang='en', result_type="mixed", until=date)
    # Store tweets in a variable and get full text
    for tweet in tweets:
        # Store tweets in a variable and get full text
        all_tweets = [tweet.text]
        all_tweets_timestamp = [tweet.created_at]


    # Create a dataframe to store the tweets with a column called 'Tweets'
    df = pd.DataFrame(all_tweets, columns=['Tweets'])
    df['Timestamp'] = all_tweets_timestamp
    df = makeDataFrame(df)
    #plotSentiment(df)
    #graphSentiment(df)
    jsonFormat = dfToJson(df)
    return jsonFormat


def makeDataFrame(dataFrame):
    # Clean the tweets
    dataFrame['Cleaned_tweets'] = dataFrame['Tweets'].apply(cleanTwt)
    # Create two new columns called 'Subjectivity' & 'Polarity'
    dataFrame['Subjectivity'] = dataFrame['Cleaned_tweets'].apply(getSubjectivity)
    dataFrame['Polarity'] = dataFrame['Cleaned_tweets'].apply(getPolarity)
    # Create a column to store the text sentiment
    dataFrame['Sentiment'] = dataFrame['Polarity'].apply(getSentiment)
    return dataFrame


# Create a func to clean the tweets
def cleanTwt(twt):
    twt = re.sub('#[A-Za-z0-9]+', '', twt)  # Removes any strings with a '#' (Hashtag)
    twt = re.sub('\\n', '', twt)  # Removes the '\n' string
    twt = re.sub('https?:\/\/\S+', '', twt)  # Removes any hyperlinks from string
    return twt


# Create a func to get the subjectivity
def getSubjectivity(twt):
    return TextBlob(twt).sentiment.subjectivity


# Create a func to get polarity
def getPolarity(twt):
    return TextBlob(twt).sentiment.polarity


# Create a func to get the sentiment of the text
def getSentiment(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def plotSentiment(dataframe):
    # Create a scatter plot to show the subjectivity and the polarity
    plt.figure(figsize=(8, 6))
    for i in range(0, dataframe.shape[0]):
        plt.scatter(dataframe['Polarity'][i], dataframe['Subjectivity'][i], color='Purple')
    plt.title('Sentiment Analysis Scatter Plot')
    plt.xlabel('Polarity')
    plt.ylabel('Subjectivity (objective -> subjective)')
    plt.show()


def graphSentiment(dataframe):
    # Create a scatter plot to show the subjectivity and the polarity
    dataframe['Sentiment'].value_counts().plot(kind='bar')
    plt.title('Sentiment Analysis Scatter Plot')
    plt.xlabel('Polarity')
    plt.ylabel('Subjectivity (objective -> subjective)')
    plt.show()

def dfToJson(dataframe):
    # Convert the df to json format for database
    json = dataframe.to_json()
    return json


# Paramerters to be passed in calling this function
# Date format
todaysDate = '2021-10-13'
# Item to search format.  Lowercase full name.
searchThis = 'bitcoin'
# Number of Tweets being pulled
numOfTweets = 1000

# Used to call function passing in date, search item, and number of tweets to pull paramerters
#print(twitterScrapper(todaysDate, searchThis, numOfTweets))
