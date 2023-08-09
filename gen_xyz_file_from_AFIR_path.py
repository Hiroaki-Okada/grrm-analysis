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


def generate_xyz_file(log_name, log_file_content):
    xyz_file = open(log_name + '.xyz', 'w')

    isWrite = False
    for line in log_file_content:
        if 'ITR' in line:
            isWrite = True
        if isWrite and 'Item' in line:
            isWrite = False
            xyz_file.write('\n')
        if isWrite:
            xyz_file.write(line)

    xyz_file.close()


def run():
    log_name = get_log_name()
    with open(log_name + '.log', 'r') as log_file:
        log_file_content = log_file.readlines()

    generate_xyz_file(log_name, log_file_content)
    print('\n{}.xyz was generated.\n'.format(log_name))


if __name__ == '__main__':
    run()