#!/usr/bin/env python3
#
# webdriver-util
#
# Automated and optionally headless login
# for web-applications, driven by webdriver
#
# Copyright (c) 2020 Björn Busse <bj.rn@baerlin.eu>
#

import base64
import configargparse
import logging
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import sys
import time


url_releases_geckodriver = "https://github.com/mozilla/geckodriver/releases/"

path_logout = {
    "gitea":     "",
    "grafana5":   "logout",
    "roundcube": "?_task=logout",
    "spotify":   ""
}

msg_error_selector = "No valid selection method supplied. \
Use one of id/name/xpath"


def which(cmd):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(cmd)
    if fpath:
        if is_exe(cmd):
            return cmd
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, cmd)
            if is_exe(exe_file):
                return exe_file

    return None


# Check for a successful login
def web_validate_login(target, validate_url, url):
    logging.info("Validating Login: ", validate_url)
    if target == "grafana5":
        if not validate_url.startswith(url + "?orgId="):
            return False
        return True
    elif target == "spotify":
        url_login_spotify = "https://accounts.spotify.com/en/status"
        if not validate_url.startswith(url_login_spotify):
            logging.info(url)
            return False
        return True
    elif target == "unknown":
        logging.debug("Can not validate login for unknown target")

    return True


# Logout
def web_logout(browser, target, url, path_logout):
    if target == "unknown":
        return False
    else:
        url_logout = url + path_logout[target]
        browser.get(url_logout)

    return True


# Log into web-app
def web_login(browser, browser_options, login, html_login):

    if login['target'] == "grafana5":
        xpath_login_grafana5 = "/html/body/grafana-app/div/div/div/div/div/div[2]/div[1]/form/div[3]/button"
        html_login_selector_user = "name"
        html_login_selector_pw = "id"
        html_login_selector_submit = "xpath"
        html_login_selector_value_user = "username"
        html_login_selector_value_pw = "inputPassword"
        html_login_selector_value_submit = xpath_login_grafana5
    elif login['target'] == "roundcube":
        html_login_selector_user = "id"
        html_login_selector_pw = "id"
        html_login_selector_submit = "id"
        html_login_selector_value_user = "rcmloginuser"
        html_login_selector_value_pw = "rcmloginpwd"
        html_login_selector_value_submit = "rcmloginsubmit"
    elif login['target'] == "spotify":
        html_login_selector_user = "name"
        html_login_selector_pw = "name"
        html_login_selector_submit = "id"
        html_login_selector_value_user = "username"
        html_login_selector_value_pw = "password"
        html_login_selector_value_submit = "login-button"
    else:
        # Selection by: id / name / css-selector / xpath
        html_login_selector_user = html_login['selector_user']
        html_login_selector_pw = html_login['selector_pw']
        html_login_selector_submit = html_login['selector_submit']
        html_login_selector_value_user = html_login['selector_value_user']
        html_login_selector_value_pw = html_login['selector_value_pw']
        html_login_selector_value_submit = html_login['selector_value_submit']

    try:
        if browser_options['fullscreen']:
            browser.fullscreen_window()

        logging.info("Opening " + login['url'] + " with browser")
        browser.get(login['url'])

        # User: Find and fill user input
        if html_login_selector_user == "name":
            e = browser.find_element(By.NAME, html_login_selector_value_user)
        elif html_login_selector_user == "id":
            e = browser.find_element(By.ID, html_login_selector_value_user)
        elif html_login_selector_user == "xpath":
            e = browser.find_element(By.XPATH, html_login_selector_value_user)
        else:
            logging.error(msg_error_selector)
            sys.exit(1)
        e.send_keys(login['user'])

        # Password: Find and fill password input
        if html_login_selector_pw == "name":
            e = browser.find_element(By.NAME, html_login_selector_value_pw)
        elif html_login_selector_pw == "id":
            e = browser.find_element(By.ID, html_login_selector_value_pw)
        elif html_login_selector_pw == "xpath":
            e = browser.find_element(By.XPATH, html_login_selector_value_pw)
        else:
            logging.error(msg_error_selector)
            sys.exit(1)
        e.send_keys(login['pw'])

        # Submit: Find and click submit button
        if html_login_selector_submit == "name":
            e = browser.find_element(By.NAME,
                                     html_login_selector_value_submit)
        elif html_login_selector_submit == "id":
            e = browser.find_element(By.ID,
                                     html_login_selector_value_submit)
        elif html_login_selector_submit == "xpath":
            e = browser.find_element(By.XPATH,
                                     html_login_selector_value_submit)
        else:
            logging.error(msg_error_selector)
            sys.exit(1)
        logging.info("Trying to log into " + login['url'])
        e.click()

    finally:
        if browser is not None:
            return True

    return False


class Browser:

    def __init__(self, args, log_level, path_login, url_releases_geckodriver):
        self.login = {}
        self.browser = self.browser_init(args,
                                         log_level,
                                         path_login)

        self.url_releases_geckodriver = "https://github.com/mozilla/geckodriver/releases/"

    def gecko_browser_setup(self):
        options = Options()
        service = Service(log_path=os.devnull)

        service.log_path = os.devnull
        options.log.level = self.browser_options['log_level']

        if not self.browser_options['headless']:
            options.headless = False

        if self.browser_options["drm"]:
            options.firefox_profile.set_preference("media.gmp-manager.updateEnabled",
                                                   True)
            options.firefox_profile.set_preference("media.eme.enabled",
                                                   True)

        browser = webdriver.Firefox(options=options,
                                    service=service)

        return browser

    def browser_init(self, args, log_level, path_logout):

        self.browser_options = {
            "gecko_logfile":          args.gecko_logfile,
            "log_level":              log_level,
            "headless":               args.browser_headless,
            "fullscreen":             args.browser_fullscreen,
            "gracetime_headless":     3,
            "gracetime_non_headless": 30,
            "drm":                    args.browser_drm,
            "close":                  args.browser_close,
        }

        self.target = args.target
        self.url = args.url[0]
        self.perform_login = True

        login_pw = args.login_pw
        login_pw_base64 = False
        if login_pw and login_pw_base64:
            login_pw = base64.b64decode(login_pw).decode("utf-8")

        self.login["target"] = self.target
        self.login["url"] = self.url
        self.login["url_payload"] = args.url_payload
        self.login["user"] = args.login_user
        self.login["pw"] = login_pw
        self.login["path_logout_target"] = path_logout

        if not self.login["user"]:
            self.perform_login = False

        html_login = {
            "selector_user":          args.selector_user,
            "selector_pw":            args.selector_pw,
            "selector_submit":        args.selector_submit,
            "selector_value_user":    args.selector_value_user,
            "selector_value_pw":      args.selector_value_pw,
            "selector_value_submit":  args.selector_value_submit
        }

        if self.target == "":
            self.target = "unknown"
            path_logout = "unknown"
        else:
            logging.info("Browser target: " + self.target)
            path_logout_target = path_logout[self.target]

        if len(self.url) < 12:
            logging.error('Not a valid URL: ', len(self.url))
            sys.exit(1)

        # Add trailing slash if it does not exist
        if not self.url.endswith("/"):
            self.url += "/"

        browser = self.gecko_browser_setup()

        if self.perform_login:
            logging.info("Performing Login")
            web_login(browser, self.browser_options, self.login, html_login)
        else:
            browser.get(self.url)
            logging.debug("Requesting " + self.url)

        # Add some grace time
        # We need less time when running headless
        if not self.browser_options['headless']:
            time.sleep(self.browser_options['gracetime_non_headless'])
        else:
            time.sleep(self.browser_options['gracetime_headless'])

        if self.perform_login:
            # Validate Login
            if not web_validate_login(self.login['target'],
                                      browser.current_url,
                                      self.login['url']):

                logging.error("Failed to log into "
                              + self.login['target'] + " on: " + self.login['url'])
            else:
                logging.info("Successfully logged into "
                             + self.login['target'] + " on: " + self.login['url'])

            # Open payload
            if not self.login['url_payload']:
                logging.info("No payload supplied")
            else:
                logging("Opening payload: ", self.login['url_payload'])
                browser.get(self.login['url_payload'])

            if self.browser_options['close']:
                logging.info("Logging out of " + self.login['url'])
                web_logout(browser,
                           self.login['target'],
                           self.login['url'],
                           self.login['path_logout'])
                browser.close()

        return browser

    def screenshot(self, img_path, t_wait_s):
        t0 = int(round(time.time() * 1000))
        n = 0

        Path(img_path).mkdir(parents=True, exist_ok=True)
        self.browser.get(self.url)

        while True:
            filename = img_path + '/image_' + str(n).zfill(4) + '.png'
            self.browser.save_screenshot(filename)
            t1 = int(round(time.time() * 1000))
            logging.info(self.url + " saved to: " + filename + " in " + str(t1 - t0) + " ms")
            t0 = t1

            time.sleep(t_wait_s)
            if 10 == n:
                n = 0
            else:
                n += 1


if __name__ == '__main__':

    parser = configargparse.ArgParser(description="")
    parser.add_argument('--browser-headless',
                        dest='browser_headless',
                        env_var='BROWSER_HEADLESS',
                        help="Run the browser in headless mode",
                        type=bool,
                        default=False)
    parser.add_argument('--browser-fullscreen',
                        dest='browser_fullscreen',
                        env_var='BROWSER_FULLSCREEN',
                        help="Run browser in fullscreen mode",
                        type=bool,
                        default=False)
    parser.add_argument('--browser-enable-drm',
                        dest='browser_drm',
                        env_var='BROWSER_DRM',
                        help="Download and enable DRM binaries",
                        type=bool,
                        default=False)
    parser.add_argument('--browser-close',
                        dest='browser_close',
                        env_var='BROWSER_CLOSE',
                        help="Close browser after successful run",
                        type=bool)
    parser.add_argument('--target',
                        dest='target',
                        env_var='TARGET',
                        help="The application to log into",
                        type=str,
                        default="")
    parser.add_argument('--url', dest='url',
                        env_var='URL',
                        action='append',
                        help="URL to open in browser startup",
                        type=str,
                        required=True)
    parser.add_argument('--url-payload',
                        dest='url_payload',
                        env_var='URL_PAYLOAD',
                        help="URL to open after successful login",
                        type=str,
                        default="")
    parser.add_argument('--login-user',
                        dest='login_user',
                        env_var='LOGIN_USER',
                        help="Username to use for web-app login",
                        type=str,
                        required=False)
    parser.add_argument('--login-pw',
                        dest='login_pw',
                        env_var='LOGIN_PW',
                        help="Password to user for web-app login",
                        type=str,
                        required=False)
    parser.add_argument('--selector-user',
                        dest='selector_user',
                        env_var='SELECTOR_USER',
                        help="The method to select the user input element",
                        type=str)
    parser.add_argument('--selector-pw',
                        dest='selector_pw',
                        env_var='SELECTOR_PW',
                        help="The method to select the user input element",
                        type=str)
    parser.add_argument('--selector-submit',
                        dest='selector_submit',
                        env_var='SELECTOR_SUBMIT',
                        help="The method to select the submit button element",
                        type=str)
    parser.add_argument('--selector-value-user',
                        dest='selector_value_user',
                        env_var='SELECTOR_VALUE_USER',
                        help="The value for the user element selection",
                        type=str)
    parser.add_argument('--selector-value-pw',
                        dest='selector_value_pw',
                        env_var='SELECTOR_VALUE_PW',
                        help="The value for the pw element selection",
                        type=str)
    parser.add_argument('--selector-value-submit',
                        dest='selector_value_submit',
                        env_var='SELECTOR_VALUE_SUBMIT',
                        help="The value for the submit element selection",
                        type=str)
    parser.add_argument('--screenshots',
                        dest='screenshots',
                        env_var='SCREENSHOTS',
                        help="Take browser screenshots",
                        type=bool,
                        default=False
                        )
    parser.add_argument('--screenshots-img-path',
                        dest='screenshots_img_path',
                        env_var='SCREENSHOTS_IMG_PATH',
                        help="Path to save screenshots to",
                        type=str,
                        default="/tmp/screenshots/"
                        )
    parser.add_argument('--screenshots-pause',
                        dest='screenshots_pause',
                        env_var='SCREENSHOTS_PAUSE',
                        help="Time between two screenshots in seconds",
                        type=int,
                        default=3
                        )
    parser.add_argument('--logfile',
                        dest='logfile',
                        env_var='LOGFILE',
                        help="The file to log to",
                        type=str)
    parser.add_argument('--geckodriver-logfile',
                        dest='gecko_logfile',
                        env_var='LOGFILE_GECKO',
                        help="The file to log geckodriver messages to",
                        type=str,
                        default="/tmp/geckodriver.log")
    parser.add_argument('--loglevel',
                        dest='log_level',
                        env_var='LOGLEVEL',
                        help="Loglevel, default: INFO",
                        type=str,
                        default='INFO')
    args = parser.parse_args()

    logfile = args.logfile
    log_level = args.log_level
    screenshots = args.screenshots
    screenshots_img_path = args.screenshots_img_path
    t_screenshots_interval_s = args.screenshots_pause

    log_format = '[%(asctime)s] \
    {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'

    # Optional File Logging
    if logfile:
        tlog = logfile.rsplit('/', 1)
        logpath = tlog[0]
        logfile = tlog[1]
        if not os.access(logpath, os.W_OK):
            # Our logger is not set up yet, so we use print here
            print("Logging: Can not write to directory. \
            Skippking file logging handler")
        else:
            fn = logpath + '/' + logfile
            file_handler = logging.FileHandler(filename=fn)
            # Our logger is not set up yet, so we use print here
            print("Logging: Logging to " + fn)

    stdout_handler = logging.StreamHandler(sys.stdout)

    if 'file_handler' in locals():
        handlers = [file_handler, stdout_handler]
    else:
        handlers = [stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )

    logger = logging.getLogger(__name__)
    level = logging.getLevelName(log_level)
    logger.setLevel(level)

    if which('geckodriver') is None:
        logging.error('Could not find geckodriver.\n\
                      You can download it from: '
                      + url_releases_geckodriver)
        sys.exit(1)

    if which('firefox') is None:
        logging.error('Could not find firefox. Aborting..')
        sys.exit(1)

    b = Browser(args, log_level, path_logout, url_releases_geckodriver)

    if screenshots:
        b.screenshot(screenshots_img_path, t_screenshots_interval_s)
    else:
        while True:
            time.sleep(1)
