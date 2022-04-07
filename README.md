# pi_photoframe
Python Script to download photos from Google Photos/Instagram/Facebook (others?) and display

# TODO:
1) Create Global Config file
2) Incorporate the amazing work of https://github.com/jasbur/RaspiWiFi to create a user-friendly Wifi Setup process
   - Project Forked: https://github.com/frobobbo/RaspiWiFi
3) Add ability to change bootscreen animation

# Setup
Follow the follwing instructions for headless wifi config:
1) Create an empty file in the Boot directory called ssh
2) Create a new file called wpa_supplicant.conf with the following code:
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    scan_ssid=1
    ssid="your_real_wifi_ssid"
    psk="your_real_password"
    key_mgmt=WPA-PSK
}
```
3) Configure quiet boot
    - Disable the Splash screen service:
    ```sudo systemctl mask plymouth-start.service```
    - Add the following to the end of cmdline.txt:
    ```console=tty3 logo.nologo vt.global_cursor_default=0 quiet```
    - Add the following to the end of config.txt:
    ```disable_splash=1```

4) Disable the Login Prompt:
```
sudo systemctl disable getty@tty1
```
5) Configure Boot Screen:
    Reference: https://yingtongli.me/blog/2016/12/21/splash.html
    - Create the file /etc/systemd/system/bootscreen.service with the following content
    ``` 
    [Unit]
    Description=Boot Splash Screen
    DefaultDependencies=no
    After=local-fs.target

    [Service]
    ExecStart=/bin/sh -c '/usr/share/bootscreen/bannerd -vD /usr/share/bootscreen/frames/*.bmp'
    StandardInput=tty
    StandardOutput=tty

    [Install]
    WantedBy=local-fs.target
    ```
    - Download bannerd to /usr/share/bootscreen
    ```
    sudo chmod u+x /usr/share/bootscreen/bannerd
    ```
    - unzip frames.zip to /usr/share/bootscreen/frames
    ```unzip frames.zip -d /usr/share/bootscreen/```
    - Execute the following to enable the service:
    ```sudo systemctl enable bootscreen```
    - Animated files can be created from an animated gif using ffmpeg:
    ```ffmpeg -i animated.gif folder\%04d.bmp```
    - or from a video file, limiting FPS using ffmpeg:
    ```ffmpeg -i animated.mp4 -vf "fps=10" folder\%04d.bmp```

6) Install PhotoFrame
 ##TODO create install Script
 - git clone https://github.com/froboboo/pi_photoframe
 - Copy /pi_photoframe/PhotoFrame to ~/PhotoFrame
 - copy lines of crontab to crontab -e
 - copy startup.sh to ~/startup.sh
 - edit /etc/rc.local with contents of rc.local
 - copy /pi_photofram/cronjobs to ~/cronjobs
 - edit startup.sh with appropriate FrameID
 - Run commands in Setup.txt
 
