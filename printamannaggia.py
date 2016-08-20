#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import socket
import subprocess

HOST = ''
PORT = 1001
MANNAGGIA_CMD = './mannaggia_nocloud.py -r -c 1 -b %(dbname)s'
MANNAGGIA_DB_DIR = './db'

MANNAGGIA_DB_MAPPING = {
    'btn_1A': 'santi_e_beati.txt',
    'btn_1B': 'prcd_cri.txt',
    'btn_1C': 'prcd_dio.txt',
    'btn_1A1B': 'prcd_ges.txt',
    'btn_1B1C': 'prcd_mad.txt',
    'btn_1A1C': 'prcd_pap.txt',
    'btn_2A': 'prcd_mtc.txt',
    'btn_2C': 'prcd_vsf.txt'
}

re_buttons = re.compile(r'\(A\d\d\)\(B\d\d\)\(C\d\d\)')

def extract_btn(s):
    a = int(s[2:4])
    b = int(s[7:9])
    c = int(s[12:14])
    return {'A': a, 'B': b, 'C': c}


def mannaggia(buttons):
    btn_key = 'btn_'
    for btn in ('A', 'B', 'C'):
        btn_val = buttons.get(btn, 0)
        if not btn_val:
            continue
        btn_key += '%d%s' % (btn_val, btn)
    print 'Db key:', btn_key
    db = MANNAGGIA_DB_MAPPING.get(btn_key, 'santi_e_beati.txt')
    cmd = MANNAGGIA_CMD % {'dbname': os.path.join(MANNAGGIA_DB_DIR, db)}
    print 'Running command: %s' % cmd
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print 'Command failed: stdout: %s; stderr: %s' % (p.stdout, p.stderr)
        return ''
    return stdout.strip()


def scan():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    print 'Connection from', addr
    buf = ''
    while True:
        buf += conn.recv(6)
        matches = re_buttons.findall(buf)
        if not matches:
            if '(' not in buf and ')' not in buf:
                buf = ''
                continue
        else:
            for match in matches:
                try:
                    buttons = extract_btn(match)
                    print 'Clicked: ', buttons
                    improperio = mannaggia(buttons)
                    if improperio:
                        try:
                            improperio = improperio.decode('utf8').encode('iso-8859-1')
                            print 'Printing: ', improperio
                        except:
                            pass
                        conn.sendall(improperio + '\n\n\n\n')
                except Exception, e:
                    print 'Unknown buttons %s: %s' % (match, e)
                    continue
            buf = buf[buf.rfind(matches[-1])+15:]
        sys.stdout.flush()


if __name__ == '__main__':
    while True:
        try:
            scan()
        except Exception, e:
            print 'OH NO:', e
            time.sleep(2)

