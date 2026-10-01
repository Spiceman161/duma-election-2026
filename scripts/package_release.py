#!/usr/bin/env python3
"""Verify the supplied snapshot and package CSV/SQLite as ordinary Deflate ZIPs."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

SOURCE_SHA256 = 'e04ec13769fb97de7e40d967c6e027903075a1e7a8bf6c209f512f0f082d7e99'
SOURCE_BYTES = 141718538
STAMP = (2026, 9, 30, 0, 0, 0)
ROOT = Path(__file__).resolve().parents[1]


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def info(name):
    entry = zipfile.ZipInfo(name, STAMP)
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.create_system = 3
    entry.external_attr = 0o100644 << 16
    entry._compresslevel = 6
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Original supplied LZMA ZIP')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    if args.source.stat().st_size != SOURCE_BYTES or digest_file(args.source) != SOURCE_SHA256:
        raise ValueError('Source ZIP size or SHA-256 mismatch')
    args.output.mkdir(parents=True, exist_ok=True)
    assets = []
    with zipfile.ZipFile(args.source) as source:
        members = {Path(i.filename).name: i for i in source.infolist()}
        if len(members) != 20 or len(members) != len(source.infolist()):
            raise ValueError('Unexpected source archive inventory')
        expected = {}
        for line in source.read(members['SHA256SUMS']).decode('utf-8').splitlines():
            sha, name = line.split(maxsplit=1)
            expected[name.lstrip('*').strip()] = sha
        if set(expected) != set(members) - {'SHA256SUMS'}:
            raise ValueError('Source checksum inventory mismatch')
        docs = {
            'README.md': 'docs/SOURCE_README.ru.md',
            'manifest.json': 'docs/manifest.json',
            'schema.json': 'docs/schema.json',
            'validation_summary.json': 'docs/validation_summary.json',
        }
        for kind in ('csv', 'sqlite'):
            filename = f'duma-2026-{kind}-2026-09-30.zip'
            selected = sorted(n for n in members if n.endswith('.csv' if kind == 'csv' else '.sqlite'))
            mapped = {n: n for n in selected}
            mapped.update(docs)
            if kind == 'sqlite':
                mapped['source_ledger.csv'] = 'docs/source_ledger.csv'
            sums = {}
            target = args.output / filename
            with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
                for original, name in sorted(mapped.items(), key=lambda pair: pair[1]):
                    h = hashlib.sha256()
                    with source.open(members[original]) as inp, archive.open(info(name), 'w', force_zip64=True) as out:
                        for block in iter(lambda: inp.read(1024 * 1024), b''):
                            h.update(block)
                            out.write(block)
                    if h.hexdigest() != expected[original]:
                        raise ValueError(f'Source member checksum mismatch: {original}')
                    sums[name] = h.hexdigest()
                    print(f'{kind}: verified {original}', flush=True)
                additions = {'README.md': (ROOT / 'docs/PACKAGE_README.ru.md').read_bytes(),
                             'README.en.md': (ROOT / 'docs/PACKAGE_README.en.md').read_bytes()}
                if kind == 'sqlite':
                    additions['examples/er_by_region.sql'] = (ROOT / 'examples/er_by_region.sql').read_bytes()
                for name, content in sorted(additions.items()):
                    archive.writestr(info(name), content)
                    sums[name] = hashlib.sha256(content).hexdigest()
                archive.writestr(info('SHA256SUMS'), ''.join(f'{sha}  {name}\n' for name, sha in sorted(sums.items())))
            with zipfile.ZipFile(target) as archive:
                if set(archive.namelist()) != set(sums) | {'SHA256SUMS'}:
                    raise ValueError('Output inventory mismatch')
                for entry in archive.infolist():
                    if entry.compress_type != zipfile.ZIP_DEFLATED:
                        raise ValueError('Output is not entirely Deflate')
                    if entry.filename == 'SHA256SUMS':
                        continue
                    h = hashlib.sha256()
                    with archive.open(entry) as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            h.update(block)
                    if h.hexdigest() != sums[entry.filename]:
                        raise ValueError(f'Output member checksum mismatch: {entry.filename}')
            assets.append({'filename': filename, 'bytes': target.stat().st_size,
                           'sha256': digest_file(target), 'format': kind,
                           'data_files': selected, 'compression': 'ZIP Deflate'})
            print(f'Complete: {filename} ({target.stat().st_size} bytes)', flush=True)
    metadata = {'snapshot_date': '2026-09-30', 'source_sha256': SOURCE_SHA256,
                'source_bytes': SOURCE_BYTES, 'assets': assets,
                'note': 'Same snapshot in two representations; original data file bytes are unchanged.'}
    (args.output / 'distribution.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.output / 'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {a['filename']}\n" for a in assets), encoding='utf-8')


if __name__ == '__main__':
    main()
