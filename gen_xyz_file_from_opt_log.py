import pdb

import os
import sys


def get_log_name():
    print('\nEnter log name (like xxx.log)')
    log_name = input().split('.log')[0]
    log_path = log_name + '.log'
    com_path = log_name + '.com'

    if not os.path.exists(log_path):
        print('\n{} doesn\'t exists...\n'.format(log_path))
        sys.exit(0)
    if not os.path.exists(com_path):
        print('\n{} doesn\'t exists...\n'.format(com_path))
        sys.exit(0)

    return log_name


def read_com_file(com_file_content):
    isRead = False
    frozen_atoms = []
    for line in com_file_content:
        if 'options' in line.lower():
            isRead = False

        if isRead:
            frozen_atoms.append(line)

        if 'frozenatoms' in line.lower():
            isRead = True

    return frozen_atoms


def generate_xyz_file(log_name, log_file_content, frozen_atoms):
    xyz_file = open(log_name + '.xyz', 'w')

    isWrite = False
    for line in log_file_content:
        if 'ITR' in line:
            isWrite = True

        if isWrite and 'Item' in line:
            isWrite = False
            if frozen_atoms != []:
                for i in frozen_atoms:
                    xyz_file.write(i)
            xyz_file.write('\n')

        if isWrite:
            xyz_file.write(line)

    xyz_file.close()


def run():
    log_name = get_log_name()
    with open(log_name + '.log', 'r') as log_file:
        log_file_content = log_file.readlines()

    with open(log_name + '.com', 'r') as com_file:
        com_file_content = com_file.readlines()

    frozen_atoms = read_com_file(com_file_content)
    generate_xyz_file(log_name, log_file_content, frozen_atoms)

    print('\n{}.xyz was generated.\n'.format(log_name))


if __name__ == '__main__':
    run()