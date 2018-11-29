# pi_photoframe
Python Script to download photos from Instagram/Google Photos and display

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
quiet logo.nologo vt.global_cursor_default=0
```
~~4) Configure Plymouth Boot Screen~~
Plymouth does not work well with rPI0
```
#Ensure Plymouth is installed and up to date
#Install Plymouth Themes and Pix Theme
sudo apt-get install plymouth plymouth-themes pix-plym-splash

#Set the Default Theme
sudo plymouth-set-default-theme pix --rebuild-initrd
```
4) Configure Boot Screen:
https://yingtongli.me/blog/2016/12/21/splash.html
