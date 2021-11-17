from psaw import PushshiftAPI
import datetime
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

api = PushshiftAPI()


# Date format (2021, 9, 26)
def wsbReddit(yearDate, monthDate, dayDate, searchTerm, subreddit):
    # Date format is (year, month, day)
    if subreddit == 'memeStock':
        subName = 'wallstreetbets'
    elif subreddit == 'crypto':
        subName = 'CryptoCurrency'
    else:
        subName = 'StockMarket'
    start_time = int(datetime.datetime(yearDate, monthDate, dayDate).timestamp())
    
    submissions = api.search_submissions(after=start_time,
                                         subreddit=subName,
                                         filter=['url', 'author', 'title', 'subreddit', 'created_utc'])

    title = []
    timeStamp = []

    # Loops through each submission in the list of submissions
    for submission in submissions:
        words = submission.title.split()
        # Filter is set to be lower() aka lowercase so the search should be too
        cashtags = list(set(filter(lambda word: word.lower().startswith('$' + searchTerm), words)))

        if cashtags:
            title.append(submission.title)
            timeStamp.append(submission.created_utc)
    df = makeDataFrame(title)
    df['Timestamp'] = timeStamp
    # plotSentiment(df)
    data = df.to_json()
    return data


# Create a func to get the subjectivity
def getSubjectivity(sub):
    return TextBlob(sub).sentiment.subjectivity


# Create a func to get polarity
def getPolarity(sub):
    return TextBlob(sub).sentiment.polarity


# Create a func to get the sentiment of the text
def getSentiment(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

    # Create a column to store the text Sentiment

    # Convert the df to json format for database


def makeDataFrame(title):
    df = pd.DataFrame(title, columns=['Title'])
    df['Subjectivity'] = df['Title'].apply(getSubjectivity)
    df['Polarity'] = df['Title'].apply(getPolarity)
    df['Sentiment'] = df['Polarity'].apply(getSentiment)
    return df
    # Create a scatter plot to show the subjectivity and the polarity


def plotSentiment(df):
    plt.figure(figsize=(8, 6))
    for i in range(0, df.shape[0]):
        plt.scatter(df['Polarity'][i], df['Subjectivity'][i], color='Purple')
    plt.title('Sentiment Analysis Scatter Plot')
    plt.xlabel('Polarity')
    plt.ylabel('Subjectivity (objective -> subjective)')
    plt.show()


# Parameters to be passed in calling this function
yearToday = 2021
monthToday = 10
dayToday = 21
searchThis = 'btc'

# Used to call function passing in 3 date parameters and a search parameter
# print(wsbReddit(yearToday, monthToday, dayToday, searchThis))
