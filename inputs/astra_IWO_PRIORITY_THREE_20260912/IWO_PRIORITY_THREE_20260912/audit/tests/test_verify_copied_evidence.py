"""Synthetic standalone wrapper guards; no simulator or native-run verification."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('portable_evidence_wrapper_under_test',
    PROJECT / 'results/priority_three_20260912/verify_copied_evidence.py')
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)


class PortableEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='UNIT_TEST_PORTABLE_EVIDENCE_', dir=PROJECT / 'tmp')
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(PROJECT / 'tmp'))

    def tearDown(self):
        self.assertTrue(Path(self.temp.name).resolve().is_relative_to(PROJECT / 'tmp'))
        self.temp.cleanup()

    def mapping(self):
        devices = {}
        for key in wrapper.DEVICE_KEYS:
            def entry(role):
                run_id = 'UNIT_TEST_' + key + '_' + role
                folder = self.root / 'results/runs' / run_id
                folder.mkdir(parents=True)
                (folder / 'execution.json').write_text(json.dumps({'run_id': run_id}))
                return {'path': folder.relative_to(self.root).as_posix(), 'run_id': run_id}
            devices[key] = {'reference': entry('reference'), 'controls': {
                role: None if key == '13p2' else entry(role) for role in wrapper.CONTROL_KEYS[key]}}
        return {'schema_version': 1, 'devices': devices}

    def test_rejects_absolute_drive_relative_and_parent_traversal(self):
        for value in ('../outside', r'..\outside', '/outside', r'C:\outside', 'C:outside',
                      r'\\server\share', r'\outside', 'file:stream'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                wrapper.relative_path(self.root, value, kind='new')

    def test_requires_exact_expected_run_identity_and_unique_roles(self):
        mapping = self.mapping()
        normalized = wrapper.validate_mapping(self.root, mapping)
        self.assertIsNone(normalized['13p2']['controls']['dos'])
        mapping['devices']['6p3']['reference']['run_id'] = 'UNIT_TEST_WRONG'
        with self.assertRaisesRegex(ValueError, 'run ID'):
            wrapper.validate_mapping(self.root, mapping)

    def test_rejects_duplicate_role_missing_required_run_and_non13_null(self):
        mapping = self.mapping()
        mapping['devices']['2p0']['controls']['width'] = mapping['devices']['2p0']['reference']
        with self.assertRaisesRegex(ValueError, 'two mapped roles'):
            wrapper.validate_mapping(self.root, mapping)
        mapping['devices']['2p0']['controls']['width'] = None
        with self.assertRaisesRegex(ValueError, 'Only unavailable'):
            wrapper.validate_mapping(self.root, mapping)
        mapping['devices']['2p0']['controls']['width'] = {'path': 'missing', 'run_id': 'missing'}
        with self.assertRaisesRegex(ValueError, 'missing'):
            wrapper.validate_mapping(self.root, mapping)

    def test_missing_13_control_is_incomplete_but_present_failure_is_not_hidden(self):
        report = {'status': 'INCOMPLETE', 'checks': {
            'xmesh': {'status': 'PASS', 'pass_check': True},
            'ymesh': {'status': 'PASS', 'pass_check': True},
            'dos': {'status': 'MISSING', 'pass_check': False}}}
        self.assertEqual(wrapper.scope_status(report), 'INCOMPLETE')
        report['checks']['xmesh'] = {'status': 'FAIL', 'pass_check': False}
        self.assertEqual(wrapper.scope_status(report), 'FAIL')

    def synthetic_modules(self):
        folder = self.root / 'scripts'
        folder.mkdir()
        common = 'from pathlib import Path\nROOT=Path(__file__).resolve().parents[1]\n'
        (folder / 'rebuild_model.py').write_text(common + 'def render(*args): return None\n')
        (folder / 'rebuild_check.py').write_text(common +
            'from rebuild_model import render\ndef load_run(*args): return None\n')
        (folder / 'rebuild_extension_check.py').write_text(common +
            'from rebuild_check import load_run\n')

    def test_copied_import_origins_and_no_bytecode_writes(self):
        self.synthetic_modules()
        with patch.dict(sys.modules):
            for name in wrapper.COPIED_MODULES:
                sys.modules.pop(name, None)
            check, extension, origins = wrapper.load_copied_checkers(self.root)
            self.assertIs(extension.load_run, check.load_run)
            self.assertEqual(set(origins), set(wrapper.COPIED_MODULES))
            self.assertTrue(all(Path(item['path']).is_relative_to(self.root / 'scripts') for item in origins.values()))
            self.assertFalse((self.root / 'scripts/__pycache__').exists())

    def test_foreign_cached_module_refused_without_import(self):
        self.synthetic_modules()
        foreign = types.ModuleType('rebuild_check')
        foreign.__file__ = str(self.root / 'foreign/rebuild_check.py')
        with patch.dict(sys.modules, {'rebuild_check': foreign}):
            with self.assertRaisesRegex(ValueError, 'Foreign cached'):
                wrapper.load_copied_checkers(self.root)

    def test_output_new_and_cannot_overlap_native_evidence(self):
        normalized = wrapper.validate_mapping(self.root, self.mapping())
        out = wrapper.new_output_directory(self.root, normalized, 'UNIT_TEST_FIRST')
        self.assertEqual(out, self.root / 'verification/UNIT_TEST_FIRST')
        with self.assertRaises(FileExistsError):
            wrapper.new_output_directory(self.root, normalized, 'UNIT_TEST_FIRST')
        normalized['2p0']['reference']['path'] = self.root / 'verification/native'
        with self.assertRaisesRegex(ValueError, 'overlap'):
            wrapper.new_output_directory(self.root, normalized, 'UNIT_TEST_SECOND')

    def test_wrapper_contains_no_runner_or_subprocess_import(self):
        import ast
        tree = ast.parse(Path(wrapper.__file__).read_text())
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported += [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or '')
        self.assertFalse(set(imported) & {'subprocess', 'local_probe', 'paper_trial', 'owned_process_lifecycle'})


if __name__ == '__main__':
    unittest.main()

