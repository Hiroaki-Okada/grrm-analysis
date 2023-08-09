import pdb

import os
import sys


def get_log_name():
    print('\nEnter log name (like xxx.log)')
    log_name = input().split('.log')[0]
    log_path = log_name + '.log'

    if not os.path.exists(log_path):
        print('\n{} doesn\'t exists...\n'.format(log_path))
        sys.exit(0)

    return log_name


def extract_irc_and_ts(log_file_content):
    isTSRead = False
    isIRCRead = False
    ts_l = []
    irc_l = []
    middle_idx = 0

    for line in log_file_content:
        # Start TS extraction
        if 'INITIAL STRUCTURE' in line:
            isTSRead = True
            ts = []

        # Finish TS extraction
        if isTSRead and 'ENERGY' in line:
            isTSRead = False
            ts.append('\n')
            ts_l.append(ts)

        # Start IRC extraction
        if ts_l and any((i in line for i in ('# STEP', '# ITR'))):
            isIRCRead = True
            irc = []

        # Finish IRC extraction
        if isIRCRead and any((i in line for i in ('ENERGY', 'Item'))):
            isIRCRead = False
            irc.append('\n')
            irc_l.append(irc)

        # Extract TS
        if isTSRead:
            ts.append(line)

        # Extraxt IRC
        if isIRCRead:
            irc.append(line)

        # Index of turning point for IRC path
        if line == '# STEP 1\n':
            middle_idx = len(irc_l)

    irc_path = irc_l[:middle_idx][::-1] + ts_l + irc_l[middle_idx:]

    return irc_path, middle_idx


def generate_xyz_file(log_name, irc_path, middle_idx):
    xyz_file = open(log_name + '.xyz', 'w')
    
    for i_idx, i in enumerate(irc_path):
        for j_idx, j in enumerate(i):
            if j_idx == 0:
                if i_idx < middle_idx:
                    xyz_file.write('{} ({})\n'.format(j.rstrip('\n'), 'forward'))
                elif i_idx > middle_idx:
                    xyz_file.write('{} ({})\n'.format(j.rstrip('\n'), 'backward'))
                else:
                    xyz_file.write('TS structure\n')
            else:
                xyz_file.write(j)

    xyz_file.close()


def run():
    log_name = get_log_name()
    with open(log_name + '.log', 'r') as log_file:
        log_file_content = log_file.readlines()

    irc_path, middle_idx = extract_irc_and_ts(log_file_content)
    generate_xyz_file(log_name, irc_path, middle_idx)
    print('\n{}.xyz was generated.\n'.format(log_name))


if __name__ == '__main__':
    run()