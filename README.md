# ImageCapturePy
A program that captures an image and the geolocation data of any user that attempts to login to your compuper x amount of times. The data collected by ImageCapturePy is then E-mailed to the E-mail you specify.

## [OPTIONS]
* You can take a picture of the offender after the numbers of attempts are reached, then E-mail that picture to yourself alongside the notification you will receive - No autologin or location options are required.
* 

## [INSTALL]
### run:

```
sudo python setup.py sdist 
```
```
sudo python setup.py build
```
```
sudo python setup.py install
```

## [SYSTEM DEPENDENCIES]

### Debian Based Systems:

* libopencv-dev
* python-opencv
* python-dev
* procmail
* sendmail-base 
* sendmail-bin
* sendmail-cf
* sensible-mda
* syslog-ng
* sqlite3

   You can install these packages by running **sudo apt-get install package_name_above**

## IMPORTANT!
You must enable less secure apps in your gmail settings or the app will not be able to send notifications!
https://support.google.com/accounts/answer/6010255
