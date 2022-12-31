from __future__ import annotations
from glob import glob
from os import path
from re import compile

def find_notes() -> list[str]:
    fs = path.sep
    files_with_notes: list[str] = []
    for file in glob(f'decomp{fs}*{fs}**{fs}*.java'):
        with open(file, 'r') as f:
            contents = f.read()
            if '// $FF: ' in contents or '// $QF: ' in contents:
                files_with_notes.append(file)
    return files_with_notes

def find_methods_for_notes(file: str) -> dict[str, list[str]]:
    generous_method_matcher = compile(r'(?P<name>[a-zA-Z$_][a-zA-Z0-9$_]+)(\s|/\*.+?\*/)*\(\)\s*{')
    methods: dict[str, list[str]] = {}
    stray_notes: list[str] = []
    current_method: str = ''
    with open(file, 'r') as f:
        contents = f.readlines()

    for line in contents:
        if '// $FF: ' in line or '// $QF: ' in line:
            note = line.split('// $FF: ')[-1].split('// $QF: ')[-1].strip()
            if current_method:
                methods.get(current_method, list()).append(note)
            else:
                stray_notes.append(note)
        elif generous_method_matcher.search(line):
            method = generous_method_matcher.search(line)['name']
            if len(stray_notes) > 0:
                methods[method] = stray_notes
                stray_notes = []
            else:
                methods[method] = []
            current_method = method

    return methods

def main():
    files_with_notes = find_notes()
    for file in files_with_notes:
        methods = find_methods_for_notes(file)
        for method, notes in methods.items():
            if notes:
                print(f'{file} {method} {notes}')

if __name__ == '__main__':
    main()
