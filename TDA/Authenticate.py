from tda import auth, client
import json
import Config
import datetime

try:
    c = auth.client_from_token_file(Config.token_path, Config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(Config.executable_path) as driver:
        c = auth.client_from_login_flow(
            driver, Config.api_key, Config.redirect_uri, Config.token_path)
