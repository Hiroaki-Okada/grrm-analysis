import pdb

print('\nEnter log name (like xxx.log)')
log_name = input().split('.log')[0]

log_file = open(log_name + '.log', 'r')
log_file_content = log_file.readlines()
log_file.close()

xyz_file = open(log_name + '.xyz', 'w')

isWrite = False
for line in log_file_content:
    if 'ITR' in line:
        isWrite = True
    if 'Item' in line:
        isWrite = False
        xyz_file.write('\n')
    if isWrite:
        xyz_file.write(line)

xyz_file.close()
