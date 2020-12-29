# webdriver-login
Webdriver Python code to log into web applications  
and optionally load some payload URL

## Usage
```
# For a supported target like Grafana
$ TARGET="grafana" \
  URL="https://grafana.example.com" \
  LOGIN_USER="foo" \
  LOGIN_PW="c3VwZXJTZWNyZXRQYXNzd3JvZAo=" \
  ./webdriver-login.py

# For an unsupported target
$ URL="http://example.com" \
  SELECTOR_USER="id" \
  SELECTOR_VALUE_USER="userName" \
  SELECTOR_PW="name" \
  SELECTOR_VALUE_PW="inputPassword" \
  SELECTOR_SUBMIT="xpath" \
  SELECTOR_VALUE_SUBMIT="/html/body/app/div/div[1]/form/div[3]/button" \
  LOGIN_USER="foo" \
  LOGIN_PW="c3VwZXJTZWNyZXRQYXNzd3JvZAo=" \
  ./webdriver-login.py
```

## Environment Variables
- TARGET - The application to log into (optional)
- URL - The target URL
- URL_PAYLOAD - The URL to open after successful login (optional)
- LOGIN_USER - The user to use for logging in
- LOGIN_PW - The base64 encoded password to use for logging in

With a target given, only the above environment variables are needed.
TARGET can be one of
- gitea
- grafana
- roundcube

In cases where the target is not supported, the user/password/submit
element selection methods and their values must be supplied additionally.  
The currently supported methods are one of: __"id"__, __"name"__ or __"xpath"__.  
"id" is ideal but does not always exist.
- SELECTOR_USER - The method to select the user input element
- SELECTOR_PW - The method to select the user input element
- SELECTOR_SUBMIT - The method to select the submit button element

- SELECTOR_VALUE_USER - The value for the above selected element
- SELECTOR_VALUE_PW - The value for the above selected element
- SELECTOR_VALUE_SUBMIT - The value for the above selected element

### Other optional Environment Variables
- BROWSER_HEADLESS - Whether to run headless or not (defaults to False)
- BROWSER_FULLSCREEN - Whether to run fullscreen or not (defaults to True)
- BROWSER_CLOSE - Whether to close the browser after the script run (defaults to True

## Resources
[W3C WebDriver Specification](https://w3c.github.io/webdriver/)  
[Selenium/WebDriver Documentation](ww.selenium.dev/documentation/en/getting_started_with_webdriver)  
[Mozilla geckodriver](https://github.com/mozilla/geckodriver)
