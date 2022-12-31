from __future__ import annotations
from glob import glob
from difflib import unified_diff
from collections import namedtuple
import os

try:
    from natsort import natsorted
except ImportError:
    natsorted = None  # guarantee the existence of the variable
    print('natsort not found, will attempt to manually parse the latest version')

SemVer = namedtuple('SemVer', ['major', 'minor', 'patch'])

def main():
    fs = os.path.sep

    if os.path.exists('cleaned'):
        work_dir = 'cleaned'
    else:
        work_dir = 'decomp'
    
    if not os.path.exists(work_dir):
        print('No decompilation found, please run main.py first, then run clean_decomp.py for a cleaner diff')
        return
    
    if natsorted:
        dirs = natsorted(glob(f'{work_dir}{fs}*'))
        latest = dirs[-1].split(fs)[-1]
    else:
        dirs = glob(f'{work_dir}{fs}*')
        semvers: dict[SemVer, str] = {}
        for d in dirs:
            try:
                semvers[SemVer(*[int(i) for i in d.split(fs)[-1].split('.')])] = d.split(fs)[-1]
            except ValueError:
                if len(d.split(fs)[-1]) > 10:
                    # Likely a snapshot, cut off after first dash
                    semvers[SemVer(*[int(i) for i in d.split(fs)[-1].split('-')[0].split('.')])] = d.split(fs)[-1]
                else:
                    raise ValueError(f'Unable to parse version {d.split(fs)[-1]}')

        latest = semvers[max(semvers.keys())]

    os.makedirs('diffs', exist_ok=True)

    for d in dirs:
        if d.split(fs)[-1] == latest:
            continue
        print(f'Comparing {d.split(fs)[-1]} to {latest}')
        entire_output = []
        for file in glob(f'{d}{fs}**{fs}*.java'):
            with open(file, 'r') as f:
                old_contents = f.readlines()
            with open(file.replace(d, f'{work_dir}{fs}{latest}'), 'r') as f:
                new_contents = f.readlines()
            
            v1 = d.split(fs)[-1]
            v2 = latest

            diff = unified_diff(old_contents, new_contents, fromfile=v1, tofile=v2)
            diff = list(diff)
            if len(diff) > 0:
                pretty_file = file.replace('\\', '/').replace(f'{work_dir}/{v1}/', '')
                pretty_line = f'gen_diffs.py {pretty_file} {v1} {v2}\n'  # modeled after the output of the `diff` command
                entire_output.append(pretty_line)
                entire_output.extend(diff)
                if diff[-1][-1] != '\n':
                    entire_output.append('\n\\ No newline at end of file\n')

        if len(entire_output) > 0:
            with open(f'diffs{fs}{d.split(fs)[-1]}-{latest}.diff', 'w') as f:
                f.write(''.join(entire_output))

if __name__ == '__main__':
    main()
