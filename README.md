# ImageCapture
### Description
&nbsp;&nbsp;&nbsp;&nbsp;A program that captures an image and the geolocation data of any user that attempts to login to your compuper x amount of times. The data collected by ImageCapture is then E-mailed to the address you specify. This is a work in progress, so if you find any issues or bugs, please create an issue! I would very much appreciate it!

### [Details]
##### Overview:
<p>&nbsp;&nbsp;&nbsp;&nbsp;ImageCapture allows you to take a picture of the offender after the numbers of attempts of failed logins are reached. The number of attempts can be specified when starting the program. You can also grab the devices location in the form of geolocationdata. Both the picture and or the location data can then be E-mailed to you if you'd like. All you would need to do is pass an E-mail address and password to the program when starting it. E-mail credentials are needed because I am not providing an E-mail service so you have to be able to send the information someway - That way is through your own E-mail account. You should be able to see the outgoing E-mails in your sent box.</p>
   
More to come...

## OPTIONS (Highly configurable)
>Most options are interchangeable, it's just a matter of what you wish to accomplish!

### [Example use cases]
1) Capture an image of the offender only and E-mail that picture to yourself.

   ```sudo python imagecapture.py -c -e 'example@gmail.com' -p 'password' -l '/var/log/messages'```
   
2) Capture an image of the offender, autolog them in, grab the devices location, and E-mail the resulting info to yourself.

   ```sudo python imagecapture.py -ALc -e 'example@gmail.com' -p 'password' -l '/var/log/messages'```

3) Capture an image of the offender, autolog them in, grab the devices location, specify the auth logs location, specify the browser, specify the camera index, print verbose messages to the log, and E-mail resulting info to yourself.

   ```sudo python imagecapture.py -AL -v -B '/opt/google/chrom/chrome' -e 'example@gmail.com' -p 'password' -l '/var/log/messages'```
   
4) Capture an image of the offender, autolog them in, grab the devices location, E-mail the resulting info to yourself, and run the location gathering functionality everytime the computer is booted up.

   ```sudo python imagecapture.py -ALUc -e 'example@gmail.com' -p 'password' -l '/var/log/messages'```

### [Visual of All Options]
```
[anthony@ghost ImageCapture]$ sudo python src/imagecapture.py --help
Usage: imagecapture.py [options]

Options:
  -h, --help            show this help message and exit
  -e EMAIL, --email=EMAIL
                        E-mail address to send notofications to.
  -p PASSWORD, --password=PASSWORD
                        Password used to sign-in to your E-mail account.
  -V VIDEO, --video=VIDEO
                        Specify camera location.
  -v, --verbose         Print the options passed to ImageCapturePy.
  -P PORT, --port=PORT  E-mail port defaults to 587 if not specified.
  -a ATTEMPTS, --attempts=ATTEMPTS
                        Number of failed attempts defaults to 3.
  -L, --location        Enable location capturing.
  -U, --persistent-location
                        Run location capturing routine everytime the computer
                        is powered on.
  -l LOGFILE, --log-file=LOGFILE
                        Log file for program to tail. There is no default and
                        this option is mandatory!
  -c, --enable-cam      Enable cam capture of intruder.
  -A, --auto-login      Auto login user after no of failed attempts.
  -w WEBSITE, --website=WEBSITE
                        Use alternate website to capture location.
  -X, --clear-autologin
                        Remove autologin. Must be root to use this feature.
  -s, --allow-sucessful
                        Run ImageCapture even if login is sucessful.
  -B BROWSER, --browser=BROWSER
                        Select the browser used to grab geolocation data.
  -C CONFIGFILE, --config-file=CONFIGFILE
                        Configuration file path.
```

### [ImageCapture's default values]
      
   * Browser:
   
      ```/opt/google/chrome/chrome```
      
   * Website to grab location data:
   
      ```https://imagecapturepy.herokuapp.com/index.html```

   * Autologin:
   
      ```false```
      
   * Capture image of offender:
   
      ```false```
      
   * Logfile(*):
   
      ```There is NO default value  set for this option.```
      
   * Loation:
    
      ```false```
    
   * E-mail port:
   
      ```587```
      
   * Print options passed(verbose):
   
      ```false```
      
   * Camera index:
   
      ```0```
      
   * Password:
   
      ```password```
      
   * E-mail address:
   
      ```example@gmail.com```
   
   * Attempt count:
   
      ```3```
      

## IMAGECAPTURE INSTALLATION
```
sudo python setup.py sdist 
```
```
sudo python setup.py build
```
```
sudo python setup.py install
```

## IMAGECAPTURE SYSTEM DEPENDENCY CHECK
```
sudo python setup.py check
```

## SYSTEM DEPENDENCIES

### [Debian Based Systems]

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

## Modify version in setup.py via vim/nano before building
**`BEFORE(vim/nano setup.py):`**
```javascript
    setup(
        packages=[],
        name='imagecapture',
        version='0.0.6', # increment version number
```
**`AFTER:`**
```javascript
    setup(
        packages=[],
        name='imagecapture',
        version='0.0.7', # increment version number
```
## Build package for PyPi

**[anthony@ghost ImageCapture]$** `sudo python setup.py sdist`
  
**[anthony@ghost ImageCapture]$** `twine upload dist/*`
  
**NOTE:** If twine does not work with the above command you can try,

`twine upload --repository-url 'https://upload.pypi.org/legacy/' dist/imagecapture-0.0.6.tar.gz`.
   
   
**NOTE:** `dist/imagecapture-0.0.6.tar.gz` will be the name of the file twine just created.

## Contents of ~/.pypirc
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

## Building OpenCV with CMake
```javascript
cmake -DCAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local/opencv-3.4.0 -DWITH_OPENCL=OFF -DWITH_VTK=OFF -DWITH_QT=OFF -DWITH_EIGEN=ON -DWITH_FFMPEG=ON -DWITH_GSTREAMER=ON -DWITH_GTK=OFF -DWITH_JPEG=ON -DWITH_OPENGL=OFF -DWITH_OPENCL=OFF -DWITH_PNG=ON -DWITH_V4L=ON -DWITH_LIBV4L=ON -DWITH_VA=ON -DWITH_GPHOTO2=ON -DINSTALL_PYTHON_EXAMPLES=ON -DBUILD_EXAMPLES=ON -DBUILD_DOCS=ON -DWITH_CUDA=OFF -DWITH_OPENCL_SVM=OFF -DWITH_OPENCLAMDFFT=OFF -DWITH_OPENCLAMDBLAS=OFF -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules ..
```
<p>Steps to obtaining the opencv_contrib package</p>

- git clone git@github.com:opencv/opencv_contrib.git

- git branch -r | more

<p>Example output:</p>

```javascript
anthony@anthony:~/Documents/Source/opencv_contrib$ git branch -r | more
  origin/3.4
  origin/HEAD -> origin/master
  origin/master
anthony@anthony:~/Documents/Source/opencv_contrib$
```

- git checkout 3.4

<p>Now the opencv_contrib package is ready to use and include in your `CMAKE` compilation!</p>
