# ImageCapturePy
### Description
A program that captures an image and the geolocation data of any user that attempts to login to your compuper x amount of times. The data collected by ImageCapturePy is then E-mailed to the address you specify.

### Details
   ImageCapturePy allows you to take a picture of the offender after the numbers of attempts are reached. The number of attempts can be specified when starting the program. You can also grab the devices location in the form of geolocationdata. Both the picture and or the location data can then be E-mailed to you if you'd like. All you would need to do is pass an E-mail address and password to the program when starting it. E-mail credentials are needed because I am not providing an E-mail service so you have to be able to send the information someway - That way is through your own E-mail account. You should be able to see the outgoing E-mails in your sent box.
   
More to come...

### ImageCapturePy's default values

   * Number of attempts:

      ```3```
      
   * Browser:
   
      ```/opt/google/chrome/chrome```
      
   * Website to grab location data:
   
      ```https://imagecapturepy.herokuapp.com/index.html```

   * Autologin:
   
      ```false```
      
   * Capture image of offender:
   
      ```false```
      
   * Logfile:
   
      ```/var/log/auth.log```
      
   * Loation:
    
      ```false```
     
   * Number of attempts:

      ```3```
    
   * E-mail port:
   
      ```587```
      
   * Print options passed(verbose):
   
      ```false```
      
   * Camera index:
   
      ```0```
      
   * 

## [OPTIONS] (Highly configurable)
>Most options are interchangeable, it's just a matter of what you wish to accomplish!

### Example use cases
1) Capture an image of the offender only and E-mail that picture to yourself.

   ```sudo python imagecapture.py -c -e 'example@gmail.com' -p 'password'```
   
2) Capture an image of the offender, autolog them in, grab the devices location, and E-mail the resulting info to yourself.

   ```sudo python imagecapture.py -ALc -e 'example@gmail.com' -p 'password'```

3) Capture an image of the offender, autolog them in, grab the devices location, specify the auth logs location, specify the browser, specify the camera index, and E-mail resulting info to yourself.

   ```sudo python imagecapture.py -AL -v 1 -l '/var/log/messages' -B '/opt/google/chrom/chrome' -e 'example@gmail.com' -p 'password'```

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

## [IMAGECAPTUREPY INSTALLATION]
```
sudo python setup.py sdist 
```
```
sudo python setup.py build
```
```
sudo python setup.py install
```

## [IMAGECAPTUREPY SYSTEM DEPENDENCY CHECK]
```
sudo python setup.py check
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

`twine upload --repository-url 'https://upload.pypi.org/legacy/' dist/imagecapturepy-0.0.6.tar.gz`.
   
   
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
