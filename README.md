# Trends project

Aim to collect data about technology trends and predict them.

### Installation

All required python libs listed in `requirements.txt`. But before
installing them you should install PostrgreSQL. This project requires at least 9.3 version.

### Initial configuration

If you need to change any settings, better create local.config.json file in the same directory as config.json and add them there.

#### DB creation
- create db user:
 + sudo -u postgres -i
 + psql
  ```
  create role ?user_name? createdb login;
  \q
  ```
 + exit
- create db. You can ignore username parameter if created user is same as your os-user name
  + createdb ?db_name? [-U ?user_name?]
- add your db setting into local.config.json file. Fill fields `db_name`, `db_user`, `db_pass`
- create tables by running
 ```
 psql dbname -U username < project_dir/core/db/create.sql
 ```

#### Sources configuration
- Google trends

 Configure proxies.json file. Add there list of proxies and login information from google account. If you don`t
  need proxies leave proxy field empty:
  ```
  ...
  "proxy":"",
  "user": "name",
  "pass": "password"
  ```
- StackOverflow
 Register in StackExchange and create an api-key. Add it to your local.config.file

#### Making cron entries

You need this step if you want updaters to start automatically. Edit files `add_crontab.sh` and `run_updater.sh`,
 enter there correct paths. Check execution rights for these file. Chmod them if necessary.

 Then just run `run_updater.sh`. Check cron entries by
  ```
  crontab -l
  ```
By default it will start every day. You can edit your crontabs as you wish.

#### Webserver

Create `local.config.json` in `tornadoweb` directory. Add there your db credentials.

Default port is 8888. If you want other port number you can change it in your config file. Remember: you may need give root
privileges to application if you want run it on some ports (for example 80).

Start webserver from `tornadoweb` directory by running (`sudo` is optional.):
```
sudo ./main.py start
```

You can add your own page templates. Just put them into any dir and add `"template_dir"` parameter to your config file.

For different static files location you can create `"staticfiles_dir"`, `"staticfiles_js_dir"`
and `"staticfiles_css_dir"`  parameters.

#### Logging

Updater and webserver store logs in `trends.log` and `websrv.log` files by default. If you want change all logging settings
in configuration files. I recommend read [this](https://docs.python.org/2/library/logging.config.html) at first.


### For developers

If you want to change code always look into module docstrings first. Sometimes there is something useful.
