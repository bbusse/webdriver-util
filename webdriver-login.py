#!/usr/bin/env python3

import base64
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import sys
import time

url = os.environ.get('URL')
url_payload = os.environ.get('URL_PAYLOAD')
port = os.environ.get('PORT')
target = os.environ.get('TARGET')

browser_headless = False
browser_fullscreen = True
log_path = '/tmp/geckobrowser.log'

if not target:
    target = "unknown"

msg_error_selector = "No valid selection method supplied. Use one of id/name/xpath"

def validate_login(target, validate_url, url):
    print("Validating: ", validate_url)
    if target == "grafana":
        if not url.endswith("/"):
            url += "/"
        if not validate_url.startswith(url + "?orgId="):
            return False
        return True
    elif target == "unknown":
        print("Can not validate login for unknown target")

    return False


if target == "grafana":
    html_login_selector_user = "name"
    html_login_selector_pw = "id"
    html_login_selector_submit = "xpath"
    html_login_selector_value_user = "username"
    html_login_selector_value_pw = "inputPassword"
    html_login_selector_value_submit = "/html/body/grafana-app/div/div/div/div/div/div[2]/div[1]/form/div[3]/button"
elif target == "roundcube":
    html_login_selector_user = "id"
    html_login_selector_pw = "id"
    html_login_selector_submit = "id"
    html_login_selector_value_user = "rcmloginuser"
    html_login_selector_value_pw = "rcmloginpwd"
    html_login_selector_value_submit = "rcmloginsubmit"
else:
    # Selection by: id / name / css-selector / xpath
    html_login_selector_user = os.environ.get('SELECTOR_USER')
    html_login_selector_pw = os.environ.get('SELECTOR_PW')
    html_login_selector_submit = os.environ.get('SELECTOR_SUBMIT')
    html_login_selector_value_user = os.environ.get('SELECTOR_VALUE_USER')
    html_login_selector_value_pw = os.environ.get('SELECTOR_VALUE_PW')
    html_login_selector_value_submit = os.environ.get('SELECTOR_VALUE_SUBMIT')

if not os.environ.get('LOGIN_USER'):
    print("Missing user for login. Please provide a username via LOGIN_USER")
    sys.exit(1)
else:
    login_user = os.environ.get('LOGIN_USER')

if not os.environ.get('LOGIN_PW'):
    print("Missing password for login. Please provide a password via LOGIN_PW")
    sys.exit(1)
else:
    login_pw = base64.b64decode(os.environ.get('LOGIN_PW')).decode("utf-8")

if len(url) < 12:
    print("Not a valid URL")
    sys.exit(1)

options = Options()
if browser_headless:
    options.headless = True
options.log.level = "info"
browser = webdriver.Firefox(options=options,
                            service_log_path=log_path)

try:
    if browser_fullscreen:
        browser.fullscreen_window()

    print("Opening " + url)
    browser.get(url)

    # User: Find and fill user input
    if html_login_selector_user == "name":
        e = browser.find_element(By.NAME, html_login_selector_value_user)
    elif html_login_selector_user == "id":
        e = browser.find_element(By.ID, html_login_selector_value_user)
    elif html_login_selector_user == "xpath":
        e = browser.find_element(By.XPATH, html_login_selector_value_user)
    else:
        print(msg_error_selector)
        sys.exit(1)
    e.send_keys(login_user)

    # Password: Find and fill password input
    if html_login_selector_pw == "name":
        e = browser.find_element(By.NAME, html_login_selector_value_pw)
    elif html_login_selector_pw == "id":
        e = browser.find_element(By.ID, html_login_selector_value_pw)
    elif html_login_selector_pw == "xpath":
        e = browser.find_element(By.XPATH, html_login_selector_value_pw)
    else:
        print(msg_error_selector)
        sys.exit(1)
    e.send_keys(login_pw)

    # Submit: Find and click submit button
    if html_login_selector_submit == "name":
        e = browser.find_element(By.NAME, html_login_selector_value_submit)
    elif html_login_selector_submit == "id":
        e = browser.find_element(By.ID, html_login_selector_value_submit)
    elif html_login_selector_submit == "xpath":
        e = browser.find_element(By.XPATH, html_login_selector_value_submit)
    else:
        print(msg_error_selector)
        sys.exit(1)
    print("Trying to log into " + url)
    e.click()

    # Add some grace time
    time.sleep(3)

    # Validate Login
    if not validate_login(target, browser.current_url, url):
        print("Failed to log into " + target + " on: " + url)
    else:
        print("Successfully logged into " + target + " on: " + url)
        # Open payload
        if not url_payload:
            print("No payload supplied, exiting")
        else:
            print("Opening payload: ", url_payload)
            browser.get(url_payload)
finally:
    if browser is not None:
        browser.close()
