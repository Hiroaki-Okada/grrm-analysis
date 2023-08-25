import pdb

import os
import re
import sys
import glob

# from scipy.spatial import distance


# # # # # PARAMETER # # # # #
# atom_pairs = [[1, 2], [1, 3], [2, 3]]
atom_pairs = [[1, 2]]
# # # # # # # # # # # # # # #


def get_configuration():
    print('\nEnter program mode (work/home)')
    mode = input()

    if mode not in ['work', 'home']:
        print('Invalid mode was specified.')
        sys.exit(0)

    print('\nEnter wildcards in filenames. If there are multiple candidates, enter one per line.')
    match_str_l = []
    while True:
        match_str = input()
        if match_str == '':
            break

        match_str_l.append(match_str)

    return mode, match_str_l


def get_pop_dirs():
    path = os.getcwd()
    files = os.listdir(path)
    dirs = [f for f in files if os.path.isdir(os.path.join(path, f))]

    return dirs


def convert_atom_xyz(atom_xyz):
    converted_atom_xyz = []
    for i in atom_xyz:
        tmp_atom_xyz = i.rstrip('\n')
        tmp_atom_xyz = re.split(r'\s+', tmp_atom_xyz)
        new_atom_xyz = [tmp_atom_xyz[0]] + [float(j) for j in tmp_atom_xyz[1:]]
        converted_atom_xyz.append(new_atom_xyz)

    return converted_atom_xyz


def get_last_itr_atom_xyz(log_path):
    with open(log_path, 'r') as log_file:
        log_file_content = log_file.readlines()

    itr = 0
    isRead = False
    for line in log_file_content:
        if isRead and 'Item' in line:
            isRead = False

        if isRead:
            atom_xyz.append(line)

        if 'ITR' in line:
            atom_xyz = []
            isRead = True

            # SADDLE+IRCでIRC計算の結果まで読まないようにする
            curr_itr = int(line.rstrip('\n').split()[-1])
            if curr_itr < itr:
                print('Detect results of IRC calculations. Exit the log file.')
                break
            else:
                itr = curr_itr

    return atom_xyz


def get_bond_distances(atom_xyz, atom_pairs):
    bond_lens = []
    converted_atom_xyz = convert_atom_xyz(atom_xyz)
    for each_atom_pair in atom_pairs:
        atom_i_num = int(each_atom_pair[0]) - 1
        atom_j_num = int(each_atom_pair[1]) - 1

        atom_i_xyz = converted_atom_xyz[atom_i_num][1:]
        atom_j_xyz = converted_atom_xyz[atom_j_num][1:]

        # bond_len = distance.euclidean(atom_i_xyz, atom_j_xyz)
        bond_len = sum([(i - j) ** 2 for i, j in zip(atom_i_xyz, atom_j_xyz)]) ** 0.5
        bond_lens.append(bond_len)

    return bond_lens


def output_results(log_path, atom_pairs, bond_distances):
    if atom_pairs == []:
        return

    print('\n' + log_path)
    for atom_ij, distance in zip(atom_pairs, bond_distances):
        atom_i = atom_ij[0]
        atom_j = atom_ij[1]
        distance_s = round(distance, 3)
        print('{}-{} distance = {}'.format(atom_i, atom_j, distance_s))


def run():
    mode, match_str_l = get_configuration()

    if mode == 'work':
        log_paths = [glob.glob(os.path.join(os.getcwd(), '*', i)) for i in match_str_l]
    elif mode == 'home':
        log_paths = [glob.glob(i) for i in match_str_l]
    else:
        raise ValueError('Imvalid mode was specified...')

    log_paths = sorted(sum(log_paths, []))

    atom_xyz = open('Last_itr_str.xyz', 'w')
    for log_path in log_paths:
        last_itr_atom_xyz = get_last_itr_atom_xyz(log_path)
        bond_distances = get_bond_distances(last_itr_atom_xyz, atom_pairs)
        output_results(log_path, atom_pairs, bond_distances)

        atom_xyz.write(log_path + '\n')
        for i in last_itr_atom_xyz:
            atom_xyz.write(i)

        atom_xyz.write('\n')

    atom_xyz.close()

    print('\nLast_itr_str.xyz was generated.\n')


if __name__ == '__main__':
    run()