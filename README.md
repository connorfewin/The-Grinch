**The-Grinch**
Open Source Github Repository to start Algorithmic Trading 
Installation:
  Requirements: (pip install ~each of the following items~)
  
    - numpy
    - selenium
    - tda-api
    - pymongo 3.12.x (check version after first install and update if needed)
    - cbpro
    - ta
    - bokeh
    - pandas
    - backtesting
    - matplotlib
    - plotly
    - psaw
    - textblob
    - tweepy
    - fastquant
    
   **TDA**
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
        

  **Coinbase Pro**
      Create an account on Coinbase Pro. This project uses their test server, which means it does not accept real bank account information. The price data is accurate to the real market. [Coinbase Pro Sandbox](https://public.sandbox.pro.coinbase.com/)
      
  **Mongo DB**
    Download a current version of MongoDB Community Server and start the service on your localhost to use the database features.
    [Community Edition Link](https://www.mongodb.com/try/download/community)
    After starting the server, if you have authentication for a Coinbase account and TD Ameritrade account you will be able to pull live price history to populate the database.
    Use 
