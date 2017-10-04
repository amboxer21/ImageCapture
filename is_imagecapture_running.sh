#!/bin/bash

if [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/imagecapture.py" | /usr/bin/wc -l` < 1 ]]; then
  logger -i -t imagecapture "Imagecapture is not running, starting imagecapture."
  /usr/bin/python /usr/local/bin/ImageCapture.py -C;
  /usr/bin/python /usr/local/bin/ImageCapture.py -L -A -c -e 'username' -p 'password' &
fi

if [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/imagecapture.py" | /usr/bin/wc -l` > 1 ]]; then
  logger -i -t imagecapture "Restarting imagecapture."
  /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/imagecapture.py" | /usr/bin/awk '{print $2}'`;
  /usr/bin/python /usr/local/bin/ImageCapture.py -C;
  /usr/bin/python /usr/local/bin/ImageCapture.py -L -A -c -e 'username' -p 'password' &
fi
