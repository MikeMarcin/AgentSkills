"""libclang discovery and translation-unit parsing from compile_commands.json.

Discovery order for libclang:
  1. CLANG_SPLIT_LIBCLANG (file path of libclang.{dylib,so,dll})
  2. `llvm-config --libdir` (LLVM_CONFIG names the binary; versioned names are tried)
  3. common Homebrew / apt / Windows install locations, newest first

The Python bindings come from the same LLVM when `import clang.cindex` fails.
"""
import functools
import glob
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys

LIB_NAMES = {'Darwin': 'libclang.dylib', 'Windows': 'libclang.dll'}


class SetupError(RuntimeError):
    pass


def _version_key(path):
    return [int(x) for x in re.findall(r'\d+', path)] or [0]


def _llvm_config_candidates():
    if os.environ.get('LLVM_CONFIG'):
        yield os.environ['LLVM_CONFIG']
    for name in ['llvm-config'] + [f'llvm-config-{v}' for v in range(30, 13, -1)]:
        found = shutil.which(name)
        if found:
            yield found
    for pattern in ('/opt/homebrew/opt/llvm*/bin/llvm-config', '/usr/local/opt/llvm*/bin/llvm-config',
                    '/usr/lib/llvm-*/bin/llvm-config'):
        yield from sorted(glob.glob(pattern), key=_version_key, reverse=True)


def _libdir_from(llvm_config):
    try:
        out = subprocess.run([llvm_config, '--libdir'], capture_output=True, text=True, timeout=20)
    except OSError:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def find_libclang():
    """(library_file, llvm_libdir) or raise SetupError."""
    lib = LIB_NAMES.get(platform.system(), 'libclang.so')
    explicit = os.environ.get('CLANG_SPLIT_LIBCLANG')
    if explicit:
        if not os.path.isfile(explicit):
            raise SetupError(f'CLANG_SPLIT_LIBCLANG={explicit} is not a file')
        return explicit, os.path.dirname(explicit)
    for cfg in _llvm_config_candidates():
        d = _libdir_from(cfg)
        if d:
            hits = sorted(glob.glob(os.path.join(d, lib + '*')), key=len)
            if hits:
                return hits[0], d
    for pattern in (f'/usr/lib/llvm-*/lib/{lib}*', f'/usr/lib/x86_64-linux-gnu/{lib}*',
                    f'/usr/lib/aarch64-linux-gnu/{lib}*', f'C:/Program Files/LLVM/bin/{lib}'):
        hits = sorted(glob.glob(pattern), key=_version_key, reverse=True)
        if hits:
            return hits[0], os.path.dirname(hits[0])
    raise SetupError('libclang not found: set CLANG_SPLIT_LIBCLANG or LLVM_CONFIG')


@functools.lru_cache(maxsize=None)
def load():
    """Import clang.cindex bound to the discovered libclang; returns (cindex, libdir)."""
    library, libdir = find_libclang()
    try:
        import clang.cindex as cindex  # noqa: F401
    except ImportError:
        for site in sorted(glob.glob(os.path.join(libdir, 'python3*', 'site-packages')), key=_version_key, reverse=True):
            if os.path.isdir(os.path.join(site, 'clang')):
                sys.path.insert(0, site)
                break
        try:
            import clang.cindex as cindex
        except ImportError as exc:
            raise SetupError(f'clang Python bindings not found beside {libdir}; pip install libclang') from exc
    if not cindex.Config.loaded:
        cindex.Config.set_library_file(library)
    return cindex, libdir


@functools.lru_cache(maxsize=None)
def resource_dir():
    _, libdir = load()
    hits = sorted(glob.glob(os.path.join(libdir, 'clang', '*')), key=_version_key, reverse=True)
    return hits[0] if hits else None


@functools.lru_cache(maxsize=None)
def macos_sdk():
    """macOS SDK path from xcrun; None elsewhere or when Xcode tools are absent."""
    if platform.system() != 'Darwin':
        return None
    try:
        out = subprocess.run(['xcrun', '--show-sdk-path'], capture_output=True, text=True, timeout=20)
    except OSError:
        return None
    path = out.stdout.strip()
    return path if out.returncode == 0 and os.path.isdir(path) else None


def git_root(path):
    start = path if os.path.isdir(path) else os.path.dirname(path)
    out = subprocess.run(['git', '-C', start, 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    if out.returncode:
        raise SetupError(f'{path} is not inside a git checkout')
    return os.path.realpath(out.stdout.strip())


def _entry_args(entry):
    if 'arguments' in entry:
        return list(entry['arguments'])
    return shlex.split(entry['command'], posix=os.name != 'nt')


def compile_entry(build_dir, source):
    path = os.path.join(build_dir, 'compile_commands.json')
    if not os.path.isfile(path):
        raise SetupError(f'{path} missing: configure with -DCMAKE_EXPORT_COMPILE_COMMANDS=ON')
    real = os.path.realpath(source)
    for e in json.load(open(path)):
        if os.path.realpath(os.path.join(e['directory'], e['file'])) == real:
            return e
    raise SetupError(f'{source} has no entry in {path}')


def parse_args_for(build_dir, source):
    """Compiler flags (without output/dependency/warning flags) plus discovered sysroot."""
    e = compile_entry(build_dir, source)
    args = _entry_args(e)[1:]
    out, skip = [], False
    real = os.path.realpath(source)
    for a in args:
        if skip:
            skip = False
            continue
        if a in ('-o', '-MF', '-MT', '-MQ'):
            skip = True
            continue
        if a in ('-c', '--'):
            continue
        if os.path.realpath(os.path.join(e['directory'], a)) == real:
            continue
        if a.startswith(('-W', '-fcolor', '-fdiagnostics-color')) or a in ('-MD', '-MMD'):
            continue
        out.append(a)
    sdk = macos_sdk()
    if sdk and '-isysroot' not in out:
        out += ['-isysroot', sdk]
        libcxx = os.path.join(sdk, 'usr', 'include', 'c++', 'v1')
        if os.path.isdir(libcxx):
            out += ['-isystem', libcxx]
    rd = resource_dir()
    if rd:
        out += ['-resource-dir', rd]
    out.append('-Wno-everything')
    SYSTEM_DIRS.update(system_dirs(out))
    return out, e['directory']


def include_dirs(args):
    dirs = []
    for i, a in enumerate(args):
        if a in ('-I', '-isystem', '-iquote', '-idirafter') and i + 1 < len(args):
            dirs.append(args[i + 1])
        elif a.startswith('-I') and len(a) > 2:
            dirs.append(a[2:])
        elif a.startswith('-isystem') and len(a) > 8:
            dirs.append(a[8:])
    return dirs


def system_dirs(args):
    dirs = [os.path.realpath(a[8:] if len(a) > 8 else args[i + 1])
            for i, a in enumerate(args) if a.startswith('-isystem') and (len(a) > 8 or i + 1 < len(args))]
    for flag in ('-isysroot', '-resource-dir', '--sysroot'):
        if flag in args:
            dirs.append(os.path.realpath(args[args.index(flag) + 1]))
    return dirs + ['/usr/include', '/usr/local/include', '/Library/Developer']


def defined_macros(args):
    """Macro names set on the command line (-DNAME or -D NAME=...)."""
    names = set()
    for i, a in enumerate(args):
        v = a[2:] if a.startswith('-D') and len(a) > 2 else (args[i + 1] if a == '-D' and i + 1 < len(args) else None)
        if v:
            names.add(v.split('=', 1)[0])
    return names


def parse(build_dir, source, detailed=False):
    ci, _ = load()
    args, directory = parse_args_for(build_dir, source)
    os.chdir(directory)
    opts = ci.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD if detailed else 0
    tu = ci.Index.create().parse(os.path.realpath(source), args=args, options=opts)
    errs = [d for d in tu.diagnostics if d.severity >= 3]
    return tu, errs


def in_file(c, path):
    return c.location.file is not None and os.path.realpath(c.location.file.name) == os.path.realpath(path)


class _Lazy:
    """`ci` attribute access that loads libclang on first use."""

    def __getattr__(self, name):
        return getattr(load()[0], name)


ci = _Lazy()


SYSTEM_DIRS = set()


def is_system(path):
    """True for files of the toolchain, SDK or system include roots seen while parsing."""
    real = os.path.realpath(path)
    return is_stdlib(real) or any(real.startswith(d.rstrip('/') + '/') for d in SYSTEM_DIRS)


def is_stdlib(path):
    p = path.replace('\\', '/')
    return '/c++/v1/' in p or re.search(r'/include/c\+\+/\d', p) is not None or '/MSVC/' in p
