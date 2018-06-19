#!/bin/bash

user=`users | awk '{print $1}'`;
config_dir="/home/$user/.imagecapture";
config="$config_dir/credentials.cfg";

if [[ $EUID != 0 ]]; then
  echo -e "Must be root to run this script!";
  exit;
fi

usage() {
  echo -e "USAGE: sudo bash Build/Debian/build.sh <email> <password>";
  exit;
};

if [[ $# != 2 ]]; then
  usage;
elif [[ $# > 2 ]]; then
  echo -e "Password cannot contains spaces or Wrong number of args.";
  exit;
fi

usage() {
  echo -e "USAGE: sudo bash Build/Debian/build.sh <email> <password>";
  exit;
};

if [[ ! -e $config_dir ]]; then
  echo -e "Creating dir $config_dir.";
  mkdir -p $config_dir;
  echo -e "Changing permissions of $config_dir.";
  sudo chmod 775 $config_dir;
  echo -e "Changing ownership of $config_dir.";
  sudo chmod $user:$user $config_dir;
  echo -e "creating file credentials.cfg.";
  touch $config; 
  echo -e "Changing permissions of $config.";
  sudo chmod 775 $config;
  echo -e "Changing ownership of $config.";
  sudo chown $user:$user $config;
else
  echo -e "Config already exists.";
fi

write_to_config() {
  echo -e "Write credentials(E-mail: $1 - Password: $2) to file? ";
  read -p "Is this correct [yes|YES]? " answer
  if(( answer == 'yes' || answer == 'YES' )); then
    echo -e "writing credentials to file.";
    echo "$1:$2" > $config;
  else
    echo -e "Exiting now.";
    exit;
  fi
};

copy_scripts_to_path() {
  if [[ -e $1/$2 ]]; then
    echo -e "File $2 already exists. Backing up before copy to directory.";
    sudo cp $1/$2 $1/$2.backup;
    sudo find ../../* -type f -name $2 -exec cp {} $1/ \;
  else
    echo -e "File $1/$2 does not exist. Copying script to the $1/ dir now.";
    sudo find ../../* -type f -name $2 -exec cp {} $1/ \;
  fi
};

install_dep() {
  case "$1" in
    'bash')
      if [[ `sudo dpkg -s $2 | awk '/^Status.*installed$/{print}'` ]]; then
        echo -e "System package $2 is already installed.";
      else
        echo -e "Installing OpenCV system packages now.";
        sudo apt-get --force-yes --yes install $2;
      fi
    ;;
    'pip')
      if [[ `pip list 2> /dev/null | egrep -o $2` ]]; then
        echo -e "PIP package $2 already installed.";
      else
        echo -e "PIP package $2 not installed. Installing PIP package now.";
        sudo pip install $2;
      fi
    ;;
  esac
};

if [[ `echo $1 | egrep --color -io "[a-z0-9]*\@[a-z]{3,8}\.[a-z]{2,6}"` && $# == 2 ]]; then
  echo -e "Using $1 as your E-mail.";
  write_to_config $1 $2;
  email=$1;
  password=$2;
else
  echo -e "E-mail($1) is not a proper format.";
  exit;
fi

for i in mdm.conf common-auth; do 
  copy_scripts_to_path '/etc/pam.d' $i;
done

for i in libopencv-dev python-opencv python-dev procmail sendmail-base sendmail-bin sendmail-cf sensible-mda syslog-ng sqlite3; do
  install_dep 'bash' $i;
done

if [[ ! `opencv_version 2> /dev/null | egrep -o "^3\.[0-9]\.[0-9]"` ]]; then
  echo -e "Please install OpenCV 3.X.X from source before continuing.";
  return;
else
  if [[ -e /usr/local/lib/python2.7/dist-packages/cv2 && `pip list 2> /dev/null | egrep --color -i opencv-python` ]]; then
    echo -e "Checking the /home/* path for OpenCV source.";
    echo -e "Copying source compiled cv2 shared object into /usr/local/lib/python2.7/dist-packages/";
    sudo find /home/* -type f -name "cv2.so" \( ! -wholename '/usr/local/lib/python2.7/dist-packages/*' \) -exec cp -i {} /usr/local/lib/python2.7/dist-packages/cv2/ \;
  else
    echo -e "Failed to copy the source compiled cv2 shared object\nto /usr/local/lib/python2.7/dist-packages/cv2/. Exiting now!";
    exit;
  fi
fi

for i in ImageCapture.py is_imagecapture_running.sh; do 
  copy_scripts_to_path '/usr/local/bin' $i;
  echo -e "Changing permissions of /usr/local/bin/$i";
  sudo chmod 775 /usr/local/bin/$i;
  echo -e "Changing ownership of $i";
  sudo chown $user:$user /usr/local/bin/$i;
done

sudo cp -R modules /usr/local/bin/;

if [[ `egrep -io "-e 'username' -p 'password' &" /usr/local/bin/is_imagecapture_running.sh` ]]; then
  echo -e "Modifying daemon script and adding username and password.";
  sed -i -re "s/(^.*.py.*-e ')(.*)(' -p ')(.*)(' \&)/\1$email\3$password\5/g" /usr/local/bin/is_imagecapture_running.sh;
else
  echo -e "Deamon script has already been modified."
fi

if [[ `egrep -io "username" /etc/pam.d/mdm.conf` ]]; then
  sed -i -re "s/username/$user/g" /etc/pam.d/mdm.conf
fi

if [[ `egrep -io 'xhost \+local:' /home/$user/.bashrc` ]]; then
  echo -e "Display for user is already exported.";
else
  echo -e "Exporting user display now.";
  echo 'xhost +local:' >> /home/$user/.bashrc;
  echo -e "Sourcing /home/$user/.bashrc now.";
  source /home/$user/.bashrc;
fi

if [[ `egrep -io 'xhost \+local:' /root/.bashrc` ]]; then
  echo -e "Display for root is already exported.";
else
  echo -e "Exporting root display now.";
  echo 'xhost +local:' >> /root/.bashrc;
  echo -e "Sourcing /root/.bashrc now.";
  source /root/.bashrc;
fi

if [[ `sudo crontab -l -u root | egrep -io '* * * * * env DISPLAY=:0.0 /bin/bash /usr/local/bin/is_imagecapture_running.sh'` ]]; then
  echo -e "Not creating crontab for root user since it already exists.";
else
  echo -e "Creating crontab for root user.";
  echo -e "* * * * * env DISPLAY=:0.0 /bin/bash /usr/local/bin/is_imagecapture_running.sh" >> /var/spool/cron/crontabs/root;
fi

# --
#/bin/bash /usr/local/bin/is_imagecapture_running.sh

# This needs to be run before its actually used. 
sudo /opt/google/chrome/chrome --user-data-dir=/home/$user/.imagecapture --no-sandbox https://justdrive-app.com/imagecapture/index.html?Email=$email 2> /dev/null
