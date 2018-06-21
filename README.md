# UFiber Nano G - Serial Hack
https://community.ubnt.com/t5/UFiber-GPON/UFiber-Nano-G-GPON-Huawei-HG8245-Configuration



## Dependencies
pip3 install paramiko scp



## Usage
Сhange your serial number on UFiber Nano G via ssh
```sh
./ubi_serial_hack.py -r 192.168.1.1 -p 22 --serial 48:57:54:43:30:30:30:30
```



## Used links
https://blog.onedefence.com/changing-the-gpon-serial-on-the-ubiquiti-ufiber-nano-g-part-two/
https://github.com/palmerc/AESCrypt2
https://github.com/dylangerdaly/UFiber-Nano-G-Playpen
