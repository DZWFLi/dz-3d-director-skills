import argparse
import shutil
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender')
    parser.add_argument('--script', required=True)
    parser.add_argument('--blend')
    args = parser.parse_args()
    exe = args.blender or shutil.which('blender')
    if not exe:
        parser.error('Pass --blender or put Blender on PATH.')
    script = Path(args.script).resolve(strict=True)
    cmd = [exe, '--background']
    if args.blend:
        cmd.append(str(Path(args.blend).resolve(strict=True)))
    else:
        cmd.append('--factory-startup')
    cmd.extend(['--python-exit-code', '1', '--python', str(script)])
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    main()
