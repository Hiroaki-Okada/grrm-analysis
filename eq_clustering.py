import pdb

import re
import os

import numpy as np
from scipy.spatial.distance import pdist, squareform


class Clustering:
    def __init__(self, dir_name, input_name,
                 bond_check_atom, inequality_sign,
                 threshold_bond_len, threshold_energy,
                 lim_delta_energy, lim_max_error, lim_rms_error, lim_extract_num):

        self.dir_name           = dir_name
        self.input_name         = input_name
        self.bond_check_atom    = bond_check_atom
        self.inequality_sign    = inequality_sign
        self.threshold_bond_len = threshold_bond_len
        self.threshold_energy   = threshold_energy
        self.lim_delta_energy   = lim_delta_energy
        self.lim_max_error      = lim_max_error
        self.lim_rms_error      = lim_rms_error
        self.lim_extract_num    = lim_extract_num

        self.dir_path = os.path.join(os.getcwd(), '..', self.dir_name)
        self.input_path = os.path.join(self.dir_path, self.input_name)

    def run(self):
        eq_list = self.read_eq_list()
        self.d_clustering(eq_list)

    def read_eq_list(self):
        eq_list = open(self.input_path + '_EQ_list.log', 'r')
        eq_list_content = eq_list.readlines() + ['\n']
        eq_list.close()

        return eq_list_content

    def write_eq(self, eq_num, cluster_num, eq_list, eq_xyz, eq_energy, all_eq_list, all_eq_xyz, energy_list, min_energy):
        eq_list.write('# Geometry of EQ {}, SYMMETRY = C1  \n'.format(eq_num))

        for i in all_eq_list[eq_num]:
            eq_list.write(i)
        eq_list.write('\n')

        eq_xyz.write('Cluster {}, EQ {}\n'.format(cluster_num, eq_num))
        for i in all_eq_xyz[eq_num]:
            eq_xyz.write(i)
        eq_xyz.write('\n')

        relative_energy = (energy_list[eq_num] - min_energy) * 2625.5
        eq_energy.write('Cluster {:>4}---- EQ {:>4} ---- Relative energy value = {:>8} (kJ/mol)\n'.format(cluster_num, eq_num, round(relative_energy, 3)))

    def analyze_eq_list(self, eq_list_content):
        dist_matrix = []
        bond_check_list = []
        energy_list = []
        all_eq_list = []
        all_eq_xyz = []

        isReadXyz = False
        isReadList = False
        for line in eq_list_content:
            if isReadXyz and 'Energy' in line:
                isReadXyz = False

                judge = True
                check_idx = 0
                for atom_i, atom_j in self.bond_check_atom:
                    atom_i_xyz = np.array(xyz_list[atom_i - 1])
                    atom_j_xyz = np.array(xyz_list[atom_j - 1])
                    bond_len = np.linalg.norm(atom_i_xyz - atom_j_xyz)

                    if self.inequality_sign[check_idx] == '<=':
                        if bond_len > self.threshold_bond_len[check_idx]:
                            judge = False
                            break
                    elif self.inequality_sign[check_idx] == '>=':
                        if bond_len < self.threshold_bond_len[check_idx]:
                            judge = False
                            break
                    else:
                        raise ValueError('Inappropriate inequality sign')

                    check_idx += 1

                bond_check_list.append(judge)
                dist_matrix.append(squareform(pdist(xyz_list)))
                all_eq_xyz.append(eq_xyz)

            if isReadList and line == '\n':
                isReadList = False
                all_eq_list.append(eq_list)

            if isReadXyz:
                eq_xyz.append(line)
                atom_xyz = line.rstrip('\n').split()
                xyz = [float(i) for i in atom_xyz[1:]]
                xyz_list.append(xyz)

            if isReadList:
                eq_list.append(line)

            if 'Energy' in line:
                if re.search(r'\(\s*-?\d+\.\d+', line):
                    temp_energy = re.search(r'\(\s*-?\d+\.\d+', line).group()
                else:
                    temp_energy = re.search(r'Energy\s+=\s+-?\d+\.\d+', line).group()

                energy = re.search(r'-?\d+\.\d+', temp_energy).group()
                energy = float(energy)
                energy_list.append(energy)

            if 'EQ' in line:
                isReadXyz = True
                isReadList = True

                xyz_list = []
                eq_xyz = []
                eq_list = []

        return dist_matrix, bond_check_list, energy_list, all_eq_list, all_eq_xyz

    def d_clustering(self, eq_list_content):
        dist_matrix, bond_check_list, energy_list, all_eq_list, all_eq_xyz = self.analyze_eq_list(eq_list_content)

        min_energy = min(energy_list)
        energy_order = np.argsort(energy_list)

        cluster_eq_list = [[] for i in range(len(energy_list))]
        bond_reject_eq = []
        energy_reject_eq = []

        cluster_num = 0
        for i in range(len(energy_order) - 1):
            eq_num_i = energy_order[i]
            eq_energy_i = energy_list[eq_num_i]
            eq_bond_check_i = bond_check_list[eq_num_i]

            if (eq_energy_i - min_energy) * 2625.5 > self.threshold_energy:
                energy_reject_eq.append(eq_num_i)
                continue

            elif eq_bond_check_i == False:
                bond_reject_eq.append(eq_num_i)
                continue

            elif eq_num_i in sum(cluster_eq_list, []):
                continue

            cluster_eq_list[cluster_num].append(eq_num_i)

            for j in range(i + 1, len(energy_order)):
                eq_num_j = energy_order[j]
                eq_energy_j = energy_list[eq_num_j]
                eq_bond_check_j = bond_check_list[eq_num_j]

                if (eq_energy_j - min_energy) * 2625.5 > self.threshold_energy:
                    continue

                if eq_bond_check_j == False:
                    continue

                delta_energy = (eq_energy_j - eq_energy_i) * 2625.5
                delta_distance = np.absolute(dist_matrix[energy_order[j]] - dist_matrix[energy_order[i]])

                max_error = 0
                sum_error = 0
                element_num = 0
                for k in delta_distance:
                    max_error = max(max_error, max(k))
                    sum_error += sum(k)
                    element_num += len(k)

                rms_error = sum_error / element_num

                if delta_energy <= self.lim_delta_energy and max_error <= self.lim_max_error and rms_error <= self.lim_rms_error:
                    cluster_eq_list[cluster_num].append(eq_num_j)

            cluster_num += 1

        clustered_eq_list       = open(self.input_path + '_clustered_EQ_list.log','w')
        clustered_eq_xyz        = open(self.input_path + '_clustered_EQ_list.xyz','w')
        clustered_eq_rel_energy = open(self.input_path + '_clustered_EQ_relative_energy.log','w')

        rep_clustered_eq_list       = open(self.input_path + '_rep_clustered_EQ_list.log','w')
        rep_clustered_eq_xyz        = open(self.input_path + '_rep_clustered_EQ_list.xyz','w')
        rep_clustered_eq_rel_energy = open(self.input_path + '_rep_clustered_EQ_relative_energy.log','w')

        clustered_eq_list.write('List of Equilibrium Structures\n\n')
        rep_clustered_eq_list.write('List of Equilibrium Structures\n\n')

        cluster_num = 0
        new_eq_num = 0
        rep_new_eq_num = 0
        for cluster in cluster_eq_list:
            extract_num = 0
            for eq_num in cluster:
                self.write_eq(eq_num, cluster_num, clustered_eq_list, clustered_eq_xyz, clustered_eq_rel_energy, all_eq_list, all_eq_xyz, energy_list, min_energy)

                if extract_num < self.lim_extract_num:
                    self.write_eq(eq_num, cluster_num, rep_clustered_eq_list, rep_clustered_eq_xyz, rep_clustered_eq_rel_energy, all_eq_list, all_eq_xyz, energy_list, min_energy)
                    rep_new_eq_num += 1

                extract_num += 1
                new_eq_num += 1

            cluster_num += 1

        clustered_eq_list.close()
        clustered_eq_xyz.close()
        clustered_eq_rel_energy.close()
        rep_clustered_eq_list.close()
        rep_clustered_eq_xyz.close()
        rep_clustered_eq_rel_energy.close()

        cnt = 0
        new_cluster_eq_list = []
        for i in cluster_eq_list:
            if i:
                cnt += 1
                new_cluster_eq_list.append(i)

        print('EQ has been classified into {} clasters.'.format(cnt))
        print(new_cluster_eq_list)
        print('\nThe following {} EQs have been rejected due to bond condition.'.format(len(bond_reject_eq)))
        print(sorted(bond_reject_eq))
        print('\nThe following {} EQs have been rejected due to electron energy instability'.format(len(energy_reject_eq)))
        print(sorted(energy_reject_eq))
        print('')


# dir_name と同じ階層に適当な名前の(例えば program)ディレクトリがあり, その中に本プログラムが入っている状況を想定していることに注意
# dir_name と input_name を適切に設定した上で, 状況に応じてその他のパラメータも調整する
def run(dir_name,
        input_name,
        bond_check_atom=[], # List of list of atom-pair (1-indexed)
        inequality_sign=[], # List of "<=" of ">=
        threshold_bond_len=[], # List of float
        threshold_energy=30.0,
        lim_delta_energy=30.0,
        lim_max_error=2.00,
        lim_rms_error=0.20,
        lim_extract_num=1):

    clustering = Clustering(dir_name, input_name,
                            bond_check_atom, inequality_sign,
                            threshold_bond_len, threshold_energy,
                            lim_delta_energy, lim_max_error, lim_rms_error, lim_extract_num)
    clustering.run()


if __name__ == '__main__':
    run()