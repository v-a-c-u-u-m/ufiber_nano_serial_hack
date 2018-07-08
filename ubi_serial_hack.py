#!/usr/bin/env python3
import sys
from select import select
from argparse import ArgumentParser, RawTextHelpFormatter
from getpass import getpass, getuser
from hashlib import sha256
from struct import pack, unpack
from binascii import hexlify, unhexlify

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient



class log():
    color_table = {
        'default':  '\033[00m',
        'red':      '\033[01;31m',
        'green':    '\033[01;32m',
        'yellow':   '\033[01;33m',
        'cyan':     '\033[01;34m',
        'fuchsia':  '\033[01;35m',
    }

    def pre(symbol, color):
        if sys.platform[0:3] == 'lin':
            symbol = log.color_table[color] + symbol + log.color_table['default']
        return '[' + symbol + ']'

    def success(s):
        pre = log.pre('+', 'green')
        print('{} {}'.format(pre, s))

    def care(s):
        pre = log.pre('!', 'fuchsia')
        print('{} {}'.format(pre, s))

    def note(s):
        pre = log.pre('~', 'yellow')
        print('{} {}'.format(pre, s))

    def info(s):
        pre = log.pre('~', 'cyan')
        print('{} {}'.format(pre, s))

    def error(s):
        pre = log.pre('-', 'red')
        print('{} {}'.format(pre, s))



local_crc32_table = [
    0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA,
    0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,
    0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988,
    0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91,
    0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE,
    0x1ADAD47D, 0x6DDDE4EB, 0xF4D4B551, 0x83D385C7,
    0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC,
    0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5,
    0x3B6E20C8, 0x4C69105E, 0xD56041E4, 0xA2677172,
    0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B,
    0x35B5A8FA, 0x42B2986C, 0xDBBBC9D6, 0xACBCF940,
    0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59,
    0x26D930AC, 0x51DE003A, 0xC8D75180, 0xBFD06116,
    0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F,
    0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924,
    0x2F6F7C87, 0x58684C11, 0xC1611DAB, 0xB6662D3D,
    0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A,
    0x71B18589, 0x06B6B51F, 0x9FBFE4A5, 0xE8B8D433,
    0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818,
    0x7F6A0DBB, 0x086D3D2D, 0x91646C97, 0xE6635C01,
    0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E,
    0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457,
    0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA, 0xFCB9887C,
    0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65,
    0x4DB26158, 0x3AB551CE, 0xA3BC0074, 0xD4BB30E2,
    0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB,
    0x4369E96A, 0x346ED9FC, 0xAD678846, 0xDA60B8D0,
    0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9,
    0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086,
    0x5768B525, 0x206F85B3, 0xB966D409, 0xCE61E49F,
    0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4,
    0x59B33D17, 0x2EB40D81, 0xB7BD5C3B, 0xC0BA6CAD,
    0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A,
    0xEAD54739, 0x9DD277AF, 0x04DB2615, 0x73DC1683,
    0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8,
    0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1,
    0xF00F9344, 0x8708A3D2, 0x1E01F268, 0x6906C2FE,
    0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7,
    0xFED41B76, 0x89D32BE0, 0x10DA7A5A, 0x67DD4ACC,
    0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5,
    0xD6D6A3E8, 0xA1D1937E, 0x38D8C2C4, 0x4FDFF252,
    0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B,
    0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60,
    0xDF60EFC3, 0xA867DF55, 0x316E8EEF, 0x4669BE79,
    0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236,
    0xCC0C7795, 0xBB0B4703, 0x220216B9, 0x5505262F,
    0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04,
    0xC2D7FFA7, 0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D,
    0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A,
    0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713,
    0x95BF4A82, 0xE2B87A14, 0x7BB12BAE, 0x0CB61B38,
    0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21,
    0x86D3D2D4, 0xF1D4E242, 0x68DDB3F8, 0x1FDA836E,
    0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777,
    0x88085AE6, 0xFF0F6A70, 0x66063BCA, 0x11010B5C,
    0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45,
    0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2,
    0xA7672661, 0xD06016F7, 0x4969474D, 0x3E6E77DB,
    0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0,
    0xA9BCAE53, 0xDEBB9EC5, 0x47B2CF7F, 0x30B5FFE9,
    0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6,
    0xBAD03605, 0xCDD70693, 0x54DE5729, 0x23D967BF,
    0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94,
    0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D,
]

def get_crc32(data, crc=0xffffffff):
    for i in data:
        crc = (crc >> 8) ^ local_crc32_table[(crc ^ i) & 0xff]
    return crc & 0xffffffff



def ssh_connection(host, port, username):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(host, port, username, getpass())
    return ssh

def ssh_exec(ssh, cmd):
    (ssh_stdin, ssh_stdout, ssh_stderr) = ssh.exec_command(cmd)
    while not ssh_stdout.channel.exit_status_ready():
        if ssh_stdout.channel.recv_ready():
            rl, wl, xl = select([ssh_stdout.channel], [], [], 0.0)
            if len(rl) > 0:
                print(ssh_stdout.channel.recv(1024).decode())
    while not ssh_stderr.channel.exit_status_ready():
        if ssh_stderr.channel.recv_ready():
            rl, wl, xl = select([ssh_stderr.channel], [], [], 0.0)
            if len(rl) > 0:
                print(ssh_stderr.channel.recv(1024).decode())


def hex_format(data):
    b = b''
    for i in range(len(data)//2):
        if i != 0:
            b += b':'
        b += data[2*i:2*(i+1)]
    return b

def get_mac(data):
    data = hexlify(data)
    return hex_format(data)

def get_serial(sn_vendor_id, sn_serial_id):
    data = hexlify(sn_vendor_id) + sn_serial_id
    return hex_format(data)

def check_vendor_id(data):
    for i in data:
        if not (65 <= i <= 90):
            return False
    return True
        


def nvram_info(mtdblock3):
    nvram_block = mtdblock3[1408:1408+1024]
    nvram_version                = nvram_block[0:4]
    boot_line                    = nvram_block[4:260]
    board_id                     = nvram_block[260:276]
    main_thread                  = nvram_block[276:280]
    psi_size                     = nvram_block[280:284]
    num_mac_addr                 = nvram_block[284:288]
    base_mac_addr                = nvram_block[288:294]
    reserved                     = nvram_block[294:296]
    old_check_sum                = nvram_block[296:300]
    gpon_sn_vendor_id            = nvram_block[300:304]
    gpon_sn_serial_id            = nvram_block[304:313]
    gpon_password                = nvram_block[313:324]
    wps_dev_pin                  = nvram_block[324:332]
    wlan_params                  = nvram_block[332:588]
    syslog_size                  = nvram_block[588:592]
    nand_part_ofs_kb             = nvram_block[592:612]
    nand_part_size_kb            = nvram_block[612:632]
    voice_board_id               = nvram_block[632:648]
    afe_id                       = nvram_block[648:656]
    unused                       = nvram_block[656:1020]
    checksum                     = nvram_block[1020:1024]
    log.info('nvram_version:    {}'.format(  unpack('!I', nvram_version)[0]  ))
    log.info('boot_line:        "{}"'.format(  boot_line.decode()  ))
    log.info('board_id:         "{}"'.format(  board_id.decode()  ))
    log.info('main_thread:      {}'.format(  unpack('!I', main_thread)[0]  ))
    log.info('psi_size:         {}'.format(  unpack('!I', psi_size)[0]  ))
    log.info('num_mac_addr:     {}'.format(  unpack('!I', num_mac_addr)[0]  ))
    log.info('base_mac_addr:    {}'.format(  get_mac(base_mac_addr).decode()  ))
    log.info('old_check_sum:    {}'.format(  hex(int.from_bytes(old_check_sum, byteorder='big'))  ))
    log.info('vendor_id:        "{}"'.format(  gpon_sn_vendor_id.decode()  ))
    log.info('serial_id:        "{}"'.format(  gpon_sn_serial_id.decode()  ))
    log.note('serial_formatted: "{}"'.format(  get_serial(gpon_sn_vendor_id, gpon_sn_serial_id).decode()  ))
    log.info('gpon_password:    "{}"'.format(  gpon_password.decode()  ))
    log.info('checksum:         {}'.format(  hex(int.from_bytes(checksum, byteorder='big'))  ))
    return board_id.decode()

def nvram_upgrade(mtdblock3, s, mac_addr):
    nvram_block = mtdblock3[1408:1408+1024]
    gpon_serial_number_vendor_id = nvram_block[300:304] # 4 bytes
    gpon_serial_number_serial_id = nvram_block[304:313] # 8 bytes + b'\x00'
    s = s.replace('-','').replace(':','').replace('\\x','').replace('x','').upper()
    length = len(s)
    if length != 16:
        log.error('Invalid serial number length')
        sys.exit(0)
    serial = unhexlify(s)
    gpon_sn_vendor_id = serial[0:4]
    gpon_sn_serial_id = s[8:16].encode() + b'\x00'
    if not check_vendor_id(gpon_sn_vendor_id):
        log.error('Invalid vendor_id')
        sys.exit(0)
    nulls = b'\x00\x00\x00\x00'
    if mac_addr:
        mac_addr = mac_addr.replace('-','').replace(':','').replace('\\x','').replace('x','').upper()
        mac_length = len(mac_addr)
        if mac_length != 12:
            log.error('Invalid mac address length')
            sys.exit(0)
        mac_addr = unhexlify(mac_addr)
        nvram_block_new = nvram_block[:288] + mac_addr + nvram_block[294:300] + gpon_sn_vendor_id + gpon_sn_serial_id + nvram_block[313:-4] + nulls
    else:
        nvram_block_new = nvram_block[:300] + gpon_sn_vendor_id + gpon_sn_serial_id + nvram_block[313:-4] + nulls
    checksum = get_crc32(nvram_block_new).to_bytes(4, byteorder='big')
    nvram_block_new = nvram_block_new[:-4] + checksum
    mtdblock3_new = mtdblock3[:1408] + nvram_block_new + mtdblock3[1408+1024:]
    return mtdblock3_new





def hack(host, port, username, serial, mac_addr):
    ssh = ssh_connection(host, port, username)
    ssh_exec(ssh, 'dd if=/dev/mtdblock3 of=/tmp/mtdblock3.BIN')

    with SCPClient(ssh.get_transport()) as scp:
        scp.get('/tmp/mtdblock3.BIN', 'mtdblock3.BIN')
    log.success('Downloaded mtdblock3.BIN')

    with open('mtdblock3.BIN', 'rb') as f:
        mtdblock3 = f.read()
    hashsum = sha256()
    hashsum.update(mtdblock3)
    log.care('Hashsum of mtdblock3.BIN (sha256): {}'.format(hashsum.hexdigest()))
    board_id = nvram_info(mtdblock3)
    if board_id != 'UBNT_SFU\x00\x00\x00\x00\x00\x00\x00\x00':
        log.error('Abnormal termination')
        sys.exit(0)

    mtdblock3_new = nvram_upgrade(mtdblock3, serial, mac_addr)
    hashsum = sha256()
    hashsum.update(mtdblock3_new)
    log.success('Built mtdblock3_new.BIN')
    log.care('Hashsum of mtdblock3_new.BIN (sha256): {}'.format(hashsum.hexdigest()))
    board_id_new = nvram_info(mtdblock3_new)
    if board_id_new != 'UBNT_SFU\x00\x00\x00\x00\x00\x00\x00\x00':
        log.error('Abnormal termination (debug)')
        sys.exit(0)

    with open('mtdblock3_new.BIN', 'wb') as f:
        f.write(mtdblock3_new)

    with SCPClient(ssh.get_transport()) as scp:
        scp.put('mtdblock3_new.BIN', '/tmp/mtdblock3_new.BIN')

    ssh_exec(ssh, 'dd if=/tmp/mtdblock3_new.BIN of=/dev/mtdblock3')
    log.success('Uploaded mtdblock3_new.BIN')

    #ssh_exec(ssh, 'reboot')
    #log.success('Now the device is rebooting')

    ssh.close()



if __name__ == '__main__':
    version = '0.4'

    colors = ['','']
    if sys.platform[0:3] == 'lin':
        colors = ['\033[1;m\033[10;31m', '\033[1;m']

    banner = '''{}
                (                            )                
          )     )\ )                 (    ( /(             )  
    (  ( /((   (()/(   (  (  (     ) )\   )\())   )     ( /(  
    )\ )\())\   /(_)) ))\ )( )\ ( /(((_) ((_)\ ( /(  (  )\()) 
 _ ((_|(_)((_) (_))  /((_|()((_))(_))_    _((_))(_)) )\((_)\  
| | | | |(_|_) / __|(_))  ((_|_|(_)_| |  | || ((_)_ ((_) |(_) 
| |_| | '_ \ | \__ \/ -_)| '_| / _` | |  | __ / _` / _|| / /  
 \___/|_.__/_| |___/\___||_| |_\__,_|_|  |_||_\__,_\__||_\_\  
                                                              

                      Author: m0rph0

                        version {}
{}'''.format(colors[0], version, colors[1])
    usage  = '''./ubi_serial_hack.py -r 192.168.1.1 -p 22 --serial 48:57:54:43:30:30:30:30
./ubi_serial_hack.py -r 192.168.1.1 -p 22 --serial 48:57:54:43:30:30:30:30 --mac 11:22:33:44:55:66'''

    parser = ArgumentParser(description=banner,
                            formatter_class=RawTextHelpFormatter,
                            epilog=usage)

    parser.add_argument("-r","-R",'--host', dest='host', type=str, default=None, help="host [127.0.0.1]")
    parser.add_argument("-u","-U",'--username', dest='username', type=str, default='ubnt', help="username")
    parser.add_argument("-s","-S",'--sn','--serial', dest='serial', type=str, default=None, help="serial")
    parser.add_argument("-m","-M",'--mac','--mac', dest='mac', type=str, default=None, help="Base MAC Addr")
    parser.add_argument("-p","-P",'--port', dest='port', type=int, default=22, help="port [22]")
    parser.add_argument("-v","-V",'--version', dest='version', action='store_true', help="version flag")

    args = parser.parse_args()


    if args.version:
        print('ubi_serial_hack version {}'.format(version))
        sys.exit(0)
    elif args.host and args.serial:
        hack(args.host, args.port, args.username, args.serial, args.mac)
    else:
        print('usage:\n{}'.format(usage))
        sys.exit(0)
