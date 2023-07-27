import pdb

print('\nEnter log name (like xxx.log)')
log_name = input().split('.log')[0]

print('\nEnter initial ITR number for extract')
init_itr = int(input())

print('\nEnter last ITR number for extract')
last_itr = int(input())

log_file = open(log_name + '.log', 'r')
log_content = log_file.readlines()
log_file.close()

itr_atom_xyz_l = []

isRead = False
for line in log_content:
    if 'ITR' in line:
        cur_itr = int(line.split()[-1])
        if init_itr <= cur_itr <= last_itr:
            isRead = True
            itr_atom_xyz = []

    if isRead and 'Item' in line:
        isRead = False
        itr_atom_xyz_l.append('\n')

    if isRead:
        itr_atom_xyz_l.append(line)

cut_log_file = open(log_name + '_cut.log', 'w')

for i in itr_atom_xyz_l:
    cut_log_file.write(i.replace('ITR.', 'NODE'))

cut_log_file.close()