from __future__ import annotations
from typing import Optional
from dataclasses import dataclass
import re

"""
This script is used to clean decompilation results in order to reduce diff size.
If using the decompilation for reasons other than diffing, you can skip this step.
"""

@dataclass
class StacktraceLine:
    class_plus_package: str
    method: str
    file: Optional[str]
    line: Optional[int]
    is_native: bool

    def __str__(self) -> str:
        if self.is_native or self.file is None:
            file_part = 'Native Method'
        elif self.line is None:
            file_part = self.file
        else:
            file_part = f'{self.file}:{self.line}'
        return f'  at {self.class_plus_package}.{self.method}({file_part})'

def as_stacktrace_line(line: str) -> Optional[StacktraceLine]:
    """
    Returns a StacktraceLine object if the line is a stacktrace line, otherwise None.
    """
    regex = r'^at\s+(?P<class_plus_package>[\w\.$]+)\.(?P<method>([\w$]+|<(cl)?init>))\(((?P<file>[\w\.$]+):(?P<line>\d+)?|(?P<native>Native Method))\)$'
    line = line.strip()
    match = re.match(regex, line)
    if match:
        return StacktraceLine(
            class_plus_package=match['class_plus_package'],
            method=match['method'],
            file=match['file'],
            line=match['line'],
            is_native=match['native'] is not None
        )
    return None

def clean_decomp(decomp: str) -> str:
    """
    Cleans the decompilation by removing various changing components.
    This includes:
    - Line numbers in comments' stacktrace lines
    - `// $FF` becoming `// $QF` in more recent versions of Quiltflower
    """
    output = []
    for line in decomp.splitlines():
        if ('// $FF:' in line):
            line = line.replace('// $FF:', '// $QF:')

        if re.compile(r'^\s*//\s*(.+)').match(line):
            split_point = line.find('//') + 2
            stacktrace_line = as_stacktrace_line(line[split_point:].strip())
            if not stacktrace_line:
                output.append(line)
            else:
                stacktrace_line.line = None

                p1 = line[:split_point]
                p2 = str(stacktrace_line)
                output.append(p1 + p2)
        else:
            output.append(line)
    return '\n'.join(output)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        # Assuming clean everything in `decomp` and place in `cleaned` folder
        import os
        from glob import glob
        fs = os.path.sep
        os.makedirs(f'cleaned{fs}', exist_ok=True)
        for path in glob(f'decomp{fs}**{fs}*.java', recursive=True):
            with open(path, 'r') as f:
                decomp = f.read()
            cleaned = clean_decomp(decomp)
            parent = os.path.dirname(path)
            os.makedirs(parent.replace('decomp', 'cleaned'), exist_ok=True)
            with open(path.replace('decomp', 'cleaned'), 'w') as f:
                f.write(cleaned)
    else:
        path = sys.argv[1]
        with open(path, 'r') as f:
            decomp = f.read()
        cleaned = clean_decomp(decomp)
        print(cleaned)
