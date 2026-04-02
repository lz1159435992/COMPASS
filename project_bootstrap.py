import os
import sys
import importlib

ARIPARTI_BASE = os.environ.get('ARIPARTI_HOME', '/home/<USER>/PycharmProjects/AriParti')


def _append_sys_path(p: str) -> None:
    if p and os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)


def _prepend_env_path(p: str) -> None:
    if not p or not os.path.isdir(p):
        return
    path_env = os.environ.get('PATH', '')
    paths = path_env.split(os.pathsep) if path_env else []
    if p not in paths:
        os.environ['PATH'] = p + (os.pathsep + path_env if path_env else '')


def setup_ariparti_paths(base: str = ARIPARTI_BASE) -> None:
    src_dir = os.path.join(base, 'src')
    scripts_dir = os.path.join(base, 'scripts')
    bin_dir = os.path.join(base, 'bin', 'linux-prebuilt')
    part_scripts_dir = os.path.join(base, 'src', 'partitioner', 'scripts')

    _append_sys_path(src_dir)
    _append_sys_path(scripts_dir)
    _append_sys_path(part_scripts_dir)
    _prepend_env_path(bin_dir)


setup_ariparti_paths()


def smoke_test() -> dict:
    mods = [
        'AriParti',
        'batch_process',
        'partitioner.scripts.mk_util',
    ]
    results = {}
    for m in mods:
        try:
            importlib.import_module(m)
            results[m] = True
        except Exception:
            results[m] = False
    # fallback: try plain mk_util if nested import fails
    if not results.get('partitioner.scripts.mk_util', False):
        try:
            importlib.import_module('mk_util')
            results['mk_util'] = True
        except Exception:
            results['mk_util'] = False
    results['PATH_has_linux_prebuilt'] = any(
        'linux-prebuilt' in p for p in os.environ.get('PATH', '').split(os.pathsep)
    )
    return results


if __name__ == '__main__':
    import json
    print(json.dumps(smoke_test(), ensure_ascii=False, indent=2))
