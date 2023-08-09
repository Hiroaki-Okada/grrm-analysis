import pdb

import os
import sys


def get_configuration():
    print('\nEnter log name (like xxx.log)')
    log_name = input().split('.log')[0]
    log_path = log_name + '.log'

    print('\nEnter initial ITR number for extract')
    init_itr = int(input())

    print('\nEnter last ITR number for extract')
    last_itr = int(input())

    if not os.path.exists(log_path):
        print('{} doesn\'t exists...\n'.format(log_path))
        sys.exit(0)

    return log_name, init_itr, last_itr


def generate_cut_path(log_name, init_itr, last_itr):
    with open(log_name + '.log', 'r') as log_file:
        log_file_content = log_file.readlines()

    itr_atom_xyz_l = []

    isWrite = False
    for line in log_file_content:
        if 'ITR' in line or 'NODE' in line:
            cur_itr = int(line.split()[-1])
            if init_itr <= cur_itr <= last_itr:
                isWrite = True
                itr_atom_xyz = []

        if isWrite and 'Item' in line:
            isWrite = False
            itr_atom_xyz_l.append('\n')

        if isWrite:
            itr_atom_xyz_l.append(line)

    with open(log_name + '_cut.log', 'w') as cut_log_file:
        for i in itr_atom_xyz_l:
            cut_log_file.write(i.replace('ITR.', 'NODE'))


def run():
    log_name, init_itr, last_itr = get_configuration()
    generate_cut_path(log_name, init_itr, last_itr)
    print('\n{}_cut.log was generated.\n'.format(log_name))


if __name__ == '__main__':
    run()