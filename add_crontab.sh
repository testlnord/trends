crontab -l > x3
echo  "20 16 * * * /home/user/Dropbox/trends/run_updater.sh" >> x3
crontab < x3
rm x3