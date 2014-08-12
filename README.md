# Trends project

Aim to collect data about technology trends and predict them

### Requirements

* Tesseract OCR. Quite tricky configuration to keep it works. Will be removed in the future (i hope).
* My google-api-plugin port for python3.

_____

### Initial configuration

#### DB creation
- install postgresql
- create user:
 + sudo -u postgres -i
 + psql
  + create role ?user_name? createdb login;
  + \q
 + exit
- create db. You can ignore username parameter if created user is same as your os-user name
  + createdb ?db_name? [-U ?user_name?]
- add your db setting into config.json file

#### Sources configuration
- Google trends

 Configure proxies.json file. Add there list of proxies and login information from google account. If you don`t
  need proxies leave proxy field empty
  ```
  ...
  "proxy":"",
  "user": "name",
  "pass": "password"
  ```