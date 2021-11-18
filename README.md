# The-Grinch
Open Source Github Repository to start Algorithmic Trading 
Installation:
  Requirements: (pip install ~each of the following items~)
    tda-api
    plotly
    matplotlib
    pandas
    numpy
    fastquant
    selenium
    psaw
    textblob
    tweepy
    
   TDA: 
    - After installing the tda-api we need to configure the TDA api (Reference Config.py in the TDA folder, these are the things we need to fill out)
      + you will need to go to https://developer.tdameritrade.com/apis
        - signup or login and create an application
        - This is where you will find you API_key
      + Then go to your regular TDA account and find your account number
        - This is the account number you need in the Config file
    - If you are having trouble setting it up, reference this youtube video: https://www.youtube.com/watch?v=P5YanfJFlNs
    - Also, here is the link to the tda-api documentation: https://tda-api.readthedocs.io/en/latest/
      + This has all the information on how to use the api, it can be a little hard to turn it into code, so reference our code while going
        through the documentation, should clear a lot of things up. It is not too difficult once you get the hang of it.
      
    Sentiment:
    - After installing tweepy a twitter api will need to be set-up through https://developer.twitter.com/en/portal/petition/essential/basic-info. The keys you recieve will be added in to twitter token under the API_Web_Scraper Directory. 
