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
3) Configure quiet boot
    - Disable the Splash screen service:
    ```sudo systemctl mask plymouth-start.service```
    - Add the following to the end of cmdline.txt:
    ```logo.nologo vt.global_cursor_default=0 quiet```
    - Add the following to the end of config.txt:
    ```disable_splash=1```

4) Disable the Login Prompt:
```
systemctl disable getty@tty1
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
    - unzip frames.zip to /usr/share/bootscreen/frames
    - Execute the following to enable the service:
    ```systemctl enable bootscreen```
    - Animated files can be created from an animated gif using ffmpeg:
    ```ffmpeg -i animated.gif folder\%04d.bmp```
