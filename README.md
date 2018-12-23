# pi_photoframe
Python Script to download photos from Instagram/Google Photos and display

# TODO:
1) Create Global Config file

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
3) Add the following to the end of cmdline.txt:
```
quiet logo.nologo vt.global_cursor_default=0 consoleblank=0 loglevel=1 disable_splash=1 console=tty3
```
4) Disable the Login Prompt:
```
systemctl disable getty@tty1
```
5) Configure Boot Screen:
    Reference: https://yingtongli.me/blog/2016/12/21/splash.html
    - Create the file /etc/systemd/system/splashscreen.service with the following content
    ``` 
    [Unit]
    Description=Splash screen
    DefaultDependencies=no
    After=local-fs.target

    [Service]
    ExecStart=/usr/bin/fbi -d /dev/fb0 --noverbose -a /opt/splash.png
    StandardInput=tty
    StandardOutput=tty

    [Install]
    WantedBy=sysinit.target
    ```
    
    
    :ffmpeg -i animated.gif folder\%04d.bmp
