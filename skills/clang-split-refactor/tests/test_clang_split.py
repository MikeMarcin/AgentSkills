"""Self-tests for clang-split against the bundled corpus; no external project needed.

Pure-Python tests always run. Corpus tests need libclang, CMake, a C++20
compiler and git, and skip with the reason when one is missing.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / 'scripts'
CORPUS = HERE / 'corpus'
sys.path.insert(0, str(SCRIPTS))

from clang_split import register, segments  # noqa: E402
from clang_split.extract import condition_frames, wrap  # noqa: E402


def _toolchain_problem():
    for tool in ('cmake', 'git'):
        if shutil.which(tool) is None:
            return f'{tool} not on PATH'
    try:
        from clang_split import cx
        cx.load()
    except Exception as exc:  # SetupError or a broken binding
        return f'libclang unavailable: {exc}'
    return None


def _run(cmd, cwd, check=True):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and res.returncode:
        raise AssertionError(f'{cmd} failed ({res.returncode}):\n{res.stdout}\n{res.stderr}')
    return res


def _cli(args, cwd):
    env = dict(os.environ, PYTHONPATH=str(SCRIPTS), PYTHONDONTWRITEBYTECODE='1')
    res = subprocess.run([sys.executable, '-B', '-m', 'clang_split'] + args, cwd=cwd, env=env, capture_output=True, text=True)
    if res.returncode:
        raise AssertionError(f'clang-split {args} failed:\n{res.stdout}\n{res.stderr}')
    return json.loads(res.stdout)


class PurePythonTests(unittest.TestCase):
    def test_condition_frames_cover_if_elif_else(self):
        lines = [b'#if A', b'a', b'#elif B', b'b', b'#else', b'c', b'#endif', b'd']
        frames = condition_frames(lines)
        self.assertEqual(frames[2], ('#if A',))
        self.assertEqual(frames[4], ('#if !(A) && (B)',))
        self.assertEqual(frames[6], ('#if !(A) && !(B)',))
        self.assertEqual(frames[8], ())

    def test_ifdef_else_becomes_negated_defined(self):
        frames = condition_frames([b'#ifdef X', b'x', b'#else', b'y', b'#endif'])
        self.assertEqual(frames[2], ('#if defined(X)',))
        self.assertEqual(frames[4], ('#if !defined(X)',))

    def test_wrap_merges_adjacent_frames(self):
        text = wrap([(('#if A',), 'one'), (('#if A',), 'two'), ((), 'three')])
        self.assertEqual(text.count('#if A'), 1)
        self.assertTrue(text.endswith('three'))

    def test_segment_respects_budget_and_keeps_callers_together(self):
        g = {
            'a': {'line': 1, 'end': 10, 'helper': False, 'kind': 'CXX_METHOD', 'refs': ['b']},
            'b': {'line': 11, 'end': 20, 'helper': False, 'kind': 'CXX_METHOD', 'refs': ['a']},
            'c': {'line': 21, 'end': 30, 'helper': False, 'kind': 'CXX_METHOD', 'refs': ['d']},
            'd': {'line': 31, 'end': 40, 'helper': False, 'kind': 'CXX_METHOD', 'refs': ['c']},
        }
        segs = segments.segment(g, max_lines=20, penalty=0.1)
        self.assertEqual([s['entities'] for s in segs], [['a', 'b'], ['c', 'd']])

    def test_plan_places_private_and_shared_helpers_and_moves_overloads_together(self):
        m = 'CXX_METHOD'
        g = {
            'h': {'line': 1, 'end': 2, 'helper': True, 'kind': 'FUNCTION_DECL', 'refs': []},
            'f': {'line': 3, 'end': 4, 'helper': True, 'kind': 'FUNCTION_DECL', 'refs': []},
            'f@5': {'line': 5, 'end': 6, 'helper': True, 'kind': 'FUNCTION_DECL', 'refs': []},
            'x': {'line': 10, 'end': 20, 'helper': False, 'kind': m, 'refs': ['h', 'f']},
            'y': {'line': 21, 'end': 30, 'helper': False, 'kind': m, 'refs': ['f@5']},
        }
        plan, _ = segments.plan(g, [['x'], ['y']], {'0': 'one', '1': 'two'}, 'support', {'source': 's.cpp'})
        groups = {grp['stem']: grp for grp in plan['groups']}
        self.assertEqual(groups['one']['private'], ['h'])
        self.assertEqual(sorted(groups['support']['entities']), ['f', 'f@5'])
        self.assertEqual(plan['source'], 's.cpp')

    def test_register_inserts_after_anchor_idempotently(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, 'src'))
            for n in ('part_a.cpp', 'part_a.hpp', 'part_b.cpp'):
                open(os.path.join(d, 'src', n), 'w').close()
            Path(os.path.join(d, 'CMakeLists.txt')).write_text('add_library(x\n\tsrc/main.cpp\n\tsrc/other.cpp\n)\n')
            spec = {'dir': 'src', 'prefix': 'part_',
                    'lists': [{'file': 'CMakeLists.txt', 'anchor': 'src/main.cpp', 'entry': 'src/{name}', 'kinds': ['.cpp']}]}
            register.run(d, spec)
            register.run(d, spec)
            text = Path(d, 'CMakeLists.txt').read_text()
            self.assertEqual(text, 'add_library(x\n\tsrc/main.cpp\n\tsrc/part_a.cpp\n\tsrc/part_b.cpp\n\tsrc/other.cpp\n)\n')

    def test_register_requires_a_unique_anchor(self):
        with tempfile.TemporaryDirectory() as d:
            Path(os.path.join(d, 'CMakeLists.txt')).write_text('nothing\n')
            spec = {'dir': '.', 'prefix': 'zz', 'lists': [{'file': 'CMakeLists.txt', 'anchor': 'src/main.cpp', 'entry': '{name}'}]}
            with self.assertRaises(SystemExit):
                register.run(d, spec)


PLAN = {
    'source': 'src/widget.cpp',
    'build': 'build-on',
    'alt_builds': ['build-off'],
    'guard_prefix': 'DEMO_',
    'groups': [{
        'stem': 'shapes', 'doc': 'Shapes the demo reports on.',
        'entities': ['report_count', 'platform_text', 'sum_of', 'square', 'Shape', 'Widget'],
        'private': ['describe', 'describe@23', 'twice'],
    }, {
        'stem': 'shapes_counter', 'header': False, 'entities': [], 'source_only': ['next'],
    }],
    'register': {'dir': 'src', 'prefix': 'shapes',
                 'lists': [{'file': 'CMakeLists.txt', 'anchor': 'src/widget.cpp', 'entry': 'src/{name}', 'kinds': ['.cpp']}]},
}


@unittest.skipIf(_toolchain_problem(), _toolchain_problem() or '')
class CorpusTests(unittest.TestCase):
    """One split of the corpus, checked by text and by building both configurations."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = cls.root = Path(cls.tmp.name) / 'corpus'
        shutil.copytree(CORPUS, root)
        _run(['git', 'init', '-q'], root)
        _run(['git', 'add', '-A'], root)
        _run(['git', '-c', 'user.email=t@example.invalid', '-c', 'user.name=t', 'commit', '-qm', 'base'], root)
        for build, flag in (('build-on', 'ON'), ('build-off', 'OFF')):
            _run(['cmake', '-S', '.', '-B', build, f'-DDEMO_FEATURE={flag}', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'], root)
        cls.baseline = {b: cls.build_and_run(b) for b in ('build-on', 'build-off')}
        cls.graph = _cli(['analyze', 'src/widget.cpp', '--build', 'build-on', '--alt-build', 'build-off'], root)
        (root / 'plan.json').write_text(json.dumps(PLAN))
        cls.report = _cli(['extract', 'plan.json', '--write'], root)
        cls.header = (root / 'src/shapes.hpp').read_text()
        cls.source = (root / 'src/shapes.cpp').read_text()
        cls.prune = _cli(['prune-includes', 'plan.json', '--write'], root)
        cls.rest = (root / 'src/widget.cpp').read_text()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def build_and_run(cls, build):
        # A failed build must fail here; never run a stale binary.
        _run(['cmake', '--build', build], cls.root)
        return _run([str(cls.root / build / 'demo')], cls.root).stdout

    def test_behavior_is_preserved_in_both_configurations(self):
        for build in ('build-on', 'build-off'):
            _run(['cmake', '-S', '.', '-B', build], self.root)
            self.assertEqual(self.build_and_run(build), self.baseline[build], build)
        self.assertIn('feature', self.baseline['build-on'])
        self.assertIn('plain', self.baseline['build-off'])

    def test_generic_lambda_helper_found_by_text(self):
        self.assertIn('twice', self.graph['Widget']['refs'])
        self.assertIn('describe@23', self.graph['Widget']['refs'])

    def test_header_keeps_declarations_only(self):
        self.assertNotIn('return "widget:"', self.header)
        self.assertIn('explicit Widget(std::string label, int scale = 1);', self.header)
        self.assertIn('std::string name() const override;', self.header)
        self.assertIn('[[nodiscard]] virtual int area() const;', self.header)
        self.assertIn('virtual ~Shape() = default;', self.header)
        self.assertIn('int scaled(int value) const;', self.header)
        self.assertIn('#ifndef DEMO_SHAPES_HPP', self.header)

    def test_default_args_with_shift_tokens_stay_in_header_only(self):
        self.assertIn('rows = std::vector<std::vector<int>>{{1, 2}, {3}}, int bias = square(2));', self.header)
        self.assertIn('int Widget::fold(std::vector<std::vector<int>> rows, int bias) {', self.source)

    def test_definitions_drop_specifiers_and_qualify_nested_types(self):
        self.assertIn('Widget::Widget(std::string label, int scale)\n\t\t: label_(std::move(label))', self.source)
        self.assertIn('std::string Widget::name() const {', self.source)
        self.assertIn('int Shape::area() const {', self.source)
        self.assertIn('int Widget::Options::scaled(int value) const {', self.source)
        for word in ('override', 'virtual', 'nodiscard', 'explicit'):
            self.assertNotIn(word, self.source)

    def test_deduced_return_and_constexpr_stay_in_header(self):
        self.assertIn('inline auto sum_of(const std::vector<int>& values) {', self.header)
        self.assertIn('constexpr int square(int value) {', self.header)
        self.assertNotIn('sum_of(const', self.source)

    def test_mutable_namespace_variable_becomes_inline_in_header(self):
        self.assertIn('inline int report_count = 0;', self.header)

    def test_conditional_initializer_moves_whole(self):
        self.assertIn('platform_text =\n#if defined(__APPLE__)\n\t\t"apple";\n#else\n\t\t"other";\n#endif', self.header)
        self.assertNotIn('#else', self.rest)

    def test_header_less_group_includes_the_declaring_header(self):
        counter = (self.root / 'src/shapes_counter.cpp').read_text()
        self.assertIn('#include "widget.hpp"', counter)
        self.assertIn('int Counter::next() {', counter)

    def test_reaches_types_through_the_sources_own_includes(self):
        self.assertIn('#include "palette.hpp"', self.source)
        self.assertNotIn('color.hpp', self.source + self.header)

    def test_conditional_branches_move_with_their_code(self):
        self.assertIn('#if DEMO_FEATURE\n\t\tout << " feature";\n#else', self.source)

    def test_macro_tested_in_directive_includes_its_header(self):
        self.assertIn('#if DEMO_VERBOSE', self.source)
        self.assertIn('#include "config.hpp"', self.source)

    def test_helpers_and_both_overloads_are_private_to_the_new_source(self):
        self.assertEqual(self.source.count('std::string describe('), 2)
        self.assertIn('namespace {', self.source)
        self.assertNotIn('describe', self.rest)

    def test_remaining_source_keeps_own_header_platform_include_and_new_header(self):
        self.assertIn('#include "widget.hpp"', self.rest)
        self.assertIn('#include "shapes.hpp"', self.rest)
        self.assertIn('#if defined(_WIN32)\n\t#include <windows.h>\n#endif', self.rest)
        self.assertNotIn('#include "config.hpp"', self.rest)
        self.assertIn('<numeric>', self.prune['dropped'])

    def test_registration_added_the_new_source_once(self):
        cmake = (self.root / 'CMakeLists.txt').read_text()
        self.assertEqual(cmake.count('src/shapes.cpp'), 1)
        self.assertEqual(cmake.count('src/shapes_counter.cpp'), 1)
        self.assertNotIn('shapes.hpp', cmake)

    def test_class_segmentation_before_outlining(self):
        base = Path(self.tmp.name) / 'pristine'
        if not base.exists():
            shutil.copytree(CORPUS, base)
            _run(['git', 'init', '-q'], base)
            _run(['cmake', '-S', '.', '-B', 'b', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'], base)
        g = _cli(['analyze', 'src/widget.cpp', '--build', 'b', '--class-line', '66'], base)
        self.assertIn('report', g)
        self.assertIn('name', g['report']['refs'])
        segs = segments.segment(g, max_lines=12, penalty=1.0)
        self.assertTrue(all(s['lines'] <= 12 or len(s['entities']) == 1 for s in segs))


if __name__ == '__main__':
    unittest.main()
