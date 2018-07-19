# ImageCapturePy
A program that captures an image and the geolocation data of any user that attempts to login to your compuper x amount of times. The data collected by ImageCapturePy is then E-mailed to the address you specify.

## [OPTIONS] (Highly configurable)
>Most options are interchangeable, it's just a matter of what you wish to accomplish!
1) You can take a picture of the offender after the numbers of attempts are reached, then E-mail that picture to yourself alongside the notification you will receive - No autologin or location options are required.
2) You can take a picture of the offender after the numbers of attempts are reached, then E-mail that picture to yourself alongside the notification you will receive as well as geolocation data in the form of latitude/longitude coordinates.
3) You can automatically log the offender in whether they get the password wrong or right in conjunction with any options stated above.
4) You can specify the location of the cam, logs to monitor(Where auth attempts ocur), the browser used to grab your location(The autologin option is **required** in order for this to work), as well as quite a few other configurable options.

### Visual of All Options:
```
[anthony@ghost ImageCapturePy]$ sudo python src/imagecapture.py --help
Usage: imagecapture.py [options]

Options:
  -h, --help            show this help message and exit
  -e EMAIL, --email=EMAIL
  -p PASSWORD, --password=PASSWORD
  -V VIDEO, --video=VIDEO
                        Specify camera location.
  -v, --verbose         Print the options passed to ImageCapturePy.
  -P PORT, --port=PORT  E-mail port defaults to 587 if not specified.
  -a ATTEMPTS, --attempts=ATTEMPTS
                        Number of failed attempts defaults to 3.
  -L, --location        Enable location capturing.
  -l LOGFILE, --log-file=LOGFILE
                        Tail log defaults to /var/log/auth.log.
  -c, --enable-cam      Enable cam capture of intruder.
  -A, --auto-login      Auto login user after no of failed attempts.
  -w WEBSITE, --website=WEBSITE
                        Use alternate website to capture location.
  -C, --clear-autologin
                        Remove autologin. Must be root to use this feature.
  -s, --allow-sucessful
                        Run ImageCapture even if login is sucessful.
  -B BROWSER, --browser=BROWSER
                        Select the browser used to grab geolocation data.
```

## [INSTALLING]
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

# Building a release for PyPi

## Modify version in setup.py via vim/nano before building:
**`BEFORE(vim/nano setup.py):`**
```javascript
    setup(
        packages=[],
        name='imagecapturepy',
        version='0.0.6', # increment version number
```
**`AFTER:`**
```javascript
    setup(
        packages=[],
        name='imagecapturepy',
        version='0.0.7', # increment version number
```
## Build package for PyPi:

  **[anthony@ghost ImageCapturePy]$** `sudo python setup.py sdist`
  
  **[anthony@ghost ImageCapturePy]$** `twine upload dist/*`
  
**NOTE:** If twine does not work with the above command you can try,

   `twine upload --repository-url 'https://upload.pypi.org/legacy/' dist/imagecapturepy-0.0.6.tar.gz`
   
   **NOTE:** `dist/imagecapturepy-0.0.6.tar.gz` will be the name of the file twine just created.
   
## Contents of ~/.pypirc:
```javascript
[distutils]
index-servers =
  pypi
  pypitest
[pypi]
repository=https://pypi.python.org/pypi
username=username
password='password'
[pypitest]
repository=https://testpypi.python.org/pypi
username=username
password='password'
```
