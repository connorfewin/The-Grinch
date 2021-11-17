"""
The token means you don't have to log in every time, it will create a token when you log in and use that if its
available and hasn't expired.
"""
token_path = 'token'

"""
You need to create a TDA Developers account, and create and application, your API key will be on your application's 
page on the TDA Developers website.
"""
api_key = 'API_KEY123@AMER.OAUTHAP'


#This means that chrome will be pulled up on your local machine
redirect_uri = 'http://localhost/'

#This chromedriver will automatically pull up a TDA login page through chrome
executable_path='./TDA/chromedriver'

#This is on you regular TDA account, it is the account number associated with your account
account_id = 123456789