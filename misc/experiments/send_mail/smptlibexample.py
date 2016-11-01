import smtplib

to = 'arkady.kalakutsky@jetbrains.com'
mail_user = 'trend.research@yandex.ru'
mail_pwd = '741852963'
print("connecting...")
smtp_server = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
print("connected")
# smtp_server.ehlo()
# smtp_server.starttls()
# smtp_server.ehlo()
smtp_server.login(mail_user, mail_pwd)
header = 'To:' + to + '\n' + 'From: ' + mail_user + '\n' + 'Subject:testing \n'
print(header)
msg = header + '\n this is test msg from mkyong.com \n\n'
smtp_server.sendmail(mail_user, to, msg)
print('done!')
smtp_server.close()
