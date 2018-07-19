# ImageCapturePy
A program to capture a picture and geolocation data upon 3 incorrect attempts at login screen. This data is then e-mailed to you.

## [INSTALL]
### run:

```javascript
sudo python setup.py sdist 
```
```javascript
sudo python setup.py build
```
```javascript
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
