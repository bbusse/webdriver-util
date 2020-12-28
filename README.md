# webdriver-login
Webdriver Python Code to log into web applications

## Environment Variables
- TARGET - The application to log into
- URL - The target URL
- URL_PAYLOAD - The URL to open after successful login
- LOGIN_USER - The user to use for logging in
- LOGIN_PW - The pw to use for logging in

With a target given, only the above environment variables are needed
TARGET can be one of
- gitea
- grafana
- roundcube

In cases where the target is not supported, the user/password/submit
element selection methods and their values must be supplied additionally:
One of: id / name / xpath
"id" is ideal but does not always exist
- SELECTOR_USER - The method to select the user input element
- SELECTOR_PW - The method to select the user input element
- SELECTOR_SUBMIT - The method to select the submit button element

- SELECTOR_VALUE_USER - The value for the above selected element
- SELECTOR_VALUE_PW - The value for the above selected element
- SELECTOR_VALUE_SUBMIT - The value for the above selected element


## Usage
```
$ TARGET="grafana" LOGIN_USER="foo" LOGIN_PW="bar" URL="https://grafana.example.com" ./webdriver-login.py
```
