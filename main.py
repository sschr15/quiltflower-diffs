from glob import glob
from requests import get
import os
import sys

VERSIONS = [
    '1.4.0',
    '1.5.0',
    '1.6.1',
    '1.7.0',
    '1.8.0',
    '1.8.1',
    '1.9.0',
    '1.10.0-SNAPSHOT',
]

def download_version(version: str):
    if os.path.exists(f'jars/quiltflower-{version}.jar'):
        return
    if version.endswith('-SNAPSHOT'):
        repo = 'snapshot'
    else:
        repo = 'release'
    url = f'https://maven.quiltmc.org/repository/{repo}/org/quiltmc/quiltflower/{version}/'
    if repo == 'snapshot':
        print(f"WARN: Snapshot versions are always re-downloaded, even if they already exist locally. Re-downloading {version}")
        # get metadata to get the latest build
        metadata = get(url + 'maven-metadata.xml').text
        snapshot_version = metadata.split('<snapshotVersion>')[1].split('</snapshotVersion>')[0]
        version = snapshot_version.split('<value>')[1].split('</value>')[0]
    
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

    fs = os.path.sep

    for version in VERSIONS:
        download_version(version)

    for file in glob('jars/quiltflower-*.jar'):
        version = file.split("quiltflower-")[1].split(".jar")[0]
        command = f'java -Xmx4G -jar {file} ' + \
                  ' '.join(flags) + \
                  f' test-cases.jar decomp{fs}{version}'

        print(f'Running "{command}"')
        os.system(command)

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        main([])
    else:
        main(sys.argv[1:])
