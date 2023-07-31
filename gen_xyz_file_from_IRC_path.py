import pdb
import os
import sys

print('\nEnter log name (like xxx.log)')
log_name = input().split('.log')[0]
log_path = log_name + '.log'

if not os.path.exists(log_path):
    print(log_path, 'doesn\'t exists...\n')
    sys.exit(0)

log_file = open(log_path, 'r')
log_file_content = log_file.readlines()
log_file.close()

isTSRead = False
isIRCRead = False
ts_l = []
irc_l = []

for idx, line in enumerate(log_file_content):
    if 'INITIAL STRUCTURE' in line:
        isTSRead = True
        ts = []

    if isTSRead and 'ENERGY' in line:
        isTSRead = False
        ts.append('\n')
        ts_l.append(ts)

    if ts_l and any((i in line for i in ('# STEP', '# ITR'))):
        isIRCRead = True
        irc = []

    if isIRCRead and any((i in line for i in ('ENERGY', 'Item'))):
        isIRCRead = False
        irc.append('\n')
        irc_l.append(irc)

    if isTSRead:
        ts.append(line)

    if isIRCRead:
        irc.append(line)

    if line == '# STEP 1\n':
        middle_idx = len(irc_l)

irc_path = irc_l[:middle_idx][::-1] + ts_l + irc_l[middle_idx:]

xyz_file = open(log_name + '.xyz', 'w')

for i in irc_path:
    for j in i:
        xyz_file.write(j)

xyz_file.close()