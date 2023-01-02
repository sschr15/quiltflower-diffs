from glob import glob
from requests import get
from xml.etree import ElementTree
import os
import sys
import subprocess
import time

try:
    from natsort import natsorted as sort
except ImportError:
    sort = sorted

def get_releases() -> list[str]:
    releases: list[str] = []
    xml = get('https://maven.quiltmc.org/repository/release/org/quiltmc/quiltflower/maven-metadata.xml').text
    root = ElementTree.fromstring(xml)
    versions = root.findall('versioning/versions/version')
    for version in versions:
        releases.append(version.text)
    return sort(releases)

def get_latest_snapshot() -> str:
    xml = get('https://maven.quiltmc.org/repository/snapshot/org/quiltmc/quiltflower/maven-metadata.xml').text
    root = ElementTree.fromstring(xml)
    return root.find('versioning/latest').text

def download_version(version: str):
    if os.path.exists(f'jars/quiltflower-{version}.jar'):
        return

    os.makedirs('jars', exist_ok=True)

    if version.endswith('-SNAPSHOT'):
        repo = 'snapshot'
    else:
        repo = 'release'
    url = f'https://maven.quiltmc.org/repository/{repo}/org/quiltmc/quiltflower/{version}/'
    if repo == 'snapshot':
        print(f"WARN: Snapshot versions are always re-downloaded, even if they already exist locally. Re-downloading {version}")
        # get metadata to get the latest build
        xml = get(url + 'maven-metadata.xml').text
        root = ElementTree.fromstring(xml)
        version = root.find('versioning/snapshotVersions/snapshotVersion/value').text
    
    url += f'quiltflower-{version}.jar'
    print(f'Downloading {url}')
    with get(url, stream=True) as r:
        r.raise_for_status()
        with open(f'jars/quiltflower-{version}.jar', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def main(flags: list[str]):
    os.makedirs('jars', exist_ok=True)
    os.makedirs('decomp', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    fs = os.path.sep

    versions = get_releases()
    versions.append(get_latest_snapshot())

    for version in versions:
        download_version(version)
    
    failures = {}

    for file in glob('jars/quiltflower-*.jar'):
        version = file.split("quiltflower-")[1].split(".jar")[0]
        command = f'java -Xmx4G -jar {file} ' + \
                  ' '.join(flags) + \
                  f' test-cases.jar decomp{fs}{version}'

        print(f'Running {command!r}')
        with open(f'logs{fs}{version}.log', 'w') as log:
            with subprocess.Popen(command, stdout=log, stderr=log) as proc:
                start_time = time.time()
                while proc.poll() is None:
                    time.sleep(1)
                    if time.time() - start_time > 60:
                        print(f'Timed out decompiling {version}')
                        proc.kill()
                        failures[version] = 'timeout'
                        no_continue = False  # pain
                        break
                else:
                    no_continue = True
                    exit_code = proc.returncode
                
        if not no_continue:
            continue

        if exit_code != 0:
            print(f'Failed to decompile using QF {version} with exit code {exit_code}')
            failures[version] = exit_code

    if len(failures) > 0:
        print(f'Failed to decompile {len(failures)} versions:')
        for version, exit_code in failures.items():
            print(f'{version} with exit code {exit_code}')

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        try:
            from qf_prefs import IFernflowerPreferences
        except ImportError:
            print('qf_prefs.py not found, trying to generate via GenQfPreferences.java')
            # Ensure a QF jar is downloaded
            version = get_releases()[-1]
            download_version(version)
            os.system('javac GenQfPreferences.java')
            os.system(f'java GenQfPreferences {version}.jar')
            try:
                from qf_prefs import IFernflowerPreferences
            except ImportError:
                print('Failed to generate qf_prefs.py, please run GenQfPreferences.java manually')
                exit(1)

        default_preferences: dict[str, bool | str | int] = {
            IFernflowerPreferences.INCLUDE_ENTIRE_CLASSPATH: True,
            IFernflowerPreferences.DECOMPILE_GENERIC_SIGNATURES: True,
            IFernflowerPreferences.REMOVE_SYNTHETIC: False,
            IFernflowerPreferences.LOG_LEVEL: 'WARN',
        }

        prefs = [f'-{k}={v if not isinstance(v, bool) else ("1" if v else "0")}' for k, v in default_preferences.items()]

        main(prefs)
    else:
        main(sys.argv[1:])
