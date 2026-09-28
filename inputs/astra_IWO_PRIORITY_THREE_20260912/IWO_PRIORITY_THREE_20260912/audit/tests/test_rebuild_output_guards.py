"""Synthetic path-guard fixtures only; no native evidence or simulator use."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import rebuild_delivery as delivery
import rebuild_overview as overview
import rebuild_report as report
import rebuild_check as check
import rebuild_extension_check as extension
import rebuild_depth_audit as depth


class RebuildOutputGuardTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(prefix='SYNTHETIC_OUTPUT_GUARD_', dir=ROOT / 'tmp')
        self.addCleanup(self.fixture.cleanup)
        self.project = Path(self.fixture.name).resolve()
        self.raw = self.project / 'results/local_session_20260910/runs'
        self.selected = self.raw / 'SYNTHETIC_SELECTED'
        self.unfinished = self.raw / 'SYNTHETIC_UNFINISHED_NEIGHBOR'
        self.selected.mkdir(parents=True)
        self.unfinished.mkdir()
        self.marker = self.unfinished / 'UNIT_TEST_ONLY.txt'
        self.marker.write_text('Synthetic path fixture; not an ATLAS run.\n', encoding='utf-8')
        self.assertFalse((self.unfinished / 'execution.json').exists())

    def test_incomplete_unselected_neighbor_rejected_before_delivery_or_overview_loads(self):
        out = self.unfinished / 'MUST_NOT_BE_CREATED'
        for module, function in ((delivery, delivery.package), (overview, overview.overview)):
            with self.subTest(tool=module.__name__), patch.object(module, 'ROOT', self.project), \
                    patch.object(module.check, 'load_run') as loader:
                with self.assertRaisesRegex(ValueError, 'reserved raw-run namespace'):
                    function([self.selected], out)
                loader.assert_not_called()
                self.assertFalse(out.exists())
        self.assertEqual(list(self.unfinished.iterdir()), [self.marker])

    def test_report_rejects_incomplete_neighbor_before_loading_or_writing(self):
        out = self.unfinished / 'MUST_NOT_BE_CREATED'
        error = io.StringIO()
        with patch.object(report, 'ROOT', self.project), patch.object(report, 'load_run') as loader, \
                contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit) as caught:
                report.main(['--runs', str(self.selected), '--out', str(out)])
            self.assertEqual(caught.exception.code, 2)
            loader.assert_not_called()
        self.assertIn('reserved raw-run namespace', error.getvalue())
        self.assertFalse(out.exists())
        self.assertEqual(list(self.unfinished.iterdir()), [self.marker])

    def test_normal_new_report_locations_still_reach_evidence_validation(self):
        out = self.project / 'results/rebuild_20260912/NEW_SYNTHETIC_REPORT'
        for module, function in ((delivery, delivery.package), (overview, overview.overview)):
            with self.subTest(tool=module.__name__), patch.object(module, 'ROOT', self.project), \
                    patch.object(module.check, 'load_run', side_effect=ValueError('SYNTHETIC evidence gate')) as loader:
                with self.assertRaisesRegex(ValueError, 'SYNTHETIC evidence gate'):
                    function([self.selected], out)
                loader.assert_called_once_with(self.selected)
                self.assertFalse(out.exists())
        with patch.object(report, 'ROOT', self.project), \
                patch.object(report, 'load_run', side_effect=ValueError('SYNTHETIC evidence gate')) as loader:
            with self.assertRaisesRegex(ValueError, 'SYNTHETIC evidence gate'):
                report.main(['--runs', str(self.selected), '--out', str(out)])
            loader.assert_called_once_with(self.selected)
            self.assertFalse(out.exists())

    def numerical_args(self, module, out):
        names = ('reference', 'width', 'xmesh', 'ymesh') if module is check else ('reference', 'xmesh', 'ymesh', 'dos')
        args = []
        for name in names:
            args += ['--' + name, str(self.selected)]
        return args + ['--out', str(out)]

    def test_numerical_clis_reject_incomplete_neighbor_before_evidence_reads(self):
        out = self.unfinished / 'MUST_NOT_BE_CREATED.json'
        for module, entry in ((check, 'load_run'), (extension, 'assess')):
            error = io.StringIO()
            with self.subTest(tool=module.__name__), patch.object(module, 'ROOT', self.project), \
                    patch.object(module, entry) as reader, contextlib.redirect_stderr(error):
                with self.assertRaises(SystemExit) as caught:
                    module.main(self.numerical_args(module, out))
                self.assertEqual(caught.exception.code, 2)
                reader.assert_not_called()
            self.assertIn('reserved raw-run namespace', error.getvalue())
            self.assertFalse(out.exists())
        self.assertEqual(list(self.unfinished.iterdir()), [self.marker])

    def test_depth_rejects_reserved_namespace_even_for_source_outside_runs(self):
        # This source is deliberately outside /runs: source-parent detection
        # alone cannot protect the separate unfinished raw-run namespace.
        source = self.project / 'SYNTHETIC_ARCHIVED_COPY'
        out = self.unfinished / 'MUST_NOT_BE_CREATED'
        error = io.StringIO()
        with patch.object(depth, 'ROOT', self.project), patch.object(depth, 'strictload_run') as reader, \
                contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit) as caught:
                depth.main([str(source), '--out', str(out)])
            self.assertEqual(caught.exception.code, 2)
            reader.assert_not_called()
        self.assertIn('reserved raw-run namespace', error.getvalue())
        self.assertFalse(out.exists())
        self.assertEqual(list(self.unfinished.iterdir()), [self.marker])

    def test_existing_numerical_certificate_is_preserved_before_reading(self):
        out = self.project / 'SYNTHETIC_RETAINED_CERTIFICATE.json'
        original = b'{"UNIT_TEST_ONLY": "must be preserved"}\n'
        out.write_bytes(original)
        with patch.object(check, 'ROOT', self.project), patch.object(check, 'load_run') as reader, \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                check.main(self.numerical_args(check, out))
            self.assertEqual(caught.exception.code, 2)
            reader.assert_not_called()
        self.assertEqual(out.read_bytes(), original)

    def test_certificate_created_during_validation_is_not_overwritten(self):
        out = self.project / 'SYNTHETIC_CONCURRENT_CERTIFICATE.json'
        original = b'{"UNIT_TEST_ONLY": "other writer"}\n'
        def another_writer(_):
            out.write_bytes(original)
            raise ValueError('SYNTHETIC evidence gate')
        with patch.object(check, 'ROOT', self.project), patch.object(check, 'load_run', side_effect=another_writer), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                check.main(self.numerical_args(check, out))
            self.assertEqual(caught.exception.code, 2)
        self.assertEqual(out.read_bytes(), original)

    def test_normal_numerical_and_depth_locations_still_reach_evidence_checks(self):
        for module in (check, extension):
            out = self.project / ('SYNTHETIC_NEW_' + module.__name__ + '.json')
            error_gate = (patch.object(check, 'load_run', side_effect=ValueError('SYNTHETIC evidence gate'))
                          if module is check else patch.object(extension, 'assess', return_value={'status': 'FAIL', 'validated_scope': 'NONE'}))
            with self.subTest(tool=module.__name__), patch.object(module, 'ROOT', self.project), \
                    error_gate as reader, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.main(self.numerical_args(module, out)), 2)
                reader.assert_called_once()
                self.assertTrue(out.is_file())
        out = self.project / 'SYNTHETIC_NEW_DEPTH_REPORT'
        with patch.object(depth, 'ROOT', self.project), \
                patch.object(depth, 'strictload_run', side_effect=ValueError('SYNTHETIC evidence gate')) as reader, \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                depth.main([str(self.selected), '--out', str(out)])
            reader.assert_called_once_with(self.selected)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
