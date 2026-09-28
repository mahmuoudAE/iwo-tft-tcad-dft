"""Mocked process lifecycle tests: no simulator or real process termination."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import owned_process_lifecycle as life


class Clock:
    def __init__(self): self.value = 0.
    def __call__(self): return self.value
    def sleep(self, duration): self.value += duration


class Tree:
    def __init__(self, clock, root_exit=.2, child_exit=.9, child_code=0, stuck=False):
        self.clock, self.root_exit, self.child_exit = clock, root_exit, child_exit
        self.child_code, self.stuck = child_code, stuck
        self.killed, self.closed, self.scans, self.missed_short_lived = False, False, 0, 0
        self.uncertain_lineage = False
    def scan(self): self.scans += 1
    def live(self):
        if self.killed and not self.stuck: return []
        return [123] if self.clock() < self.child_exit else []
    def terminate_owned(self): self.killed = True
    def evidence(self):
        return [dict(pid=100, parent_pid=None, created_filetime=10,
                     still_running=False, exit_code=0),
                dict(pid=123, parent_pid=100, created_filetime=20,
                     still_running=bool(self.live()), exit_code=None if self.live() else self.child_code)]
    def close(self): self.closed = True


class Api:
    def __init__(self):
        self.records = {100: (10, 30), 200: (20, 0), 300: (25, 0), 400: (50, 0)}
        self.opened, self.closed, self.killed = [], [], []
    def snapshot(self): return [(999, 888), (300, 200), (200, 100), (400, 100)]
    def times(self, handle): return self.records[handle]
    def running(self, handle): return self.records[handle][1] == 0
    def open(self, pid): self.opened.append(pid); return pid if pid in self.records else None
    def close(self, handle): self.closed.append(handle)
    def exit_code(self, handle): return 0
    def terminate(self, handle): self.killed.append(handle); self.records[handle] = (self.records[handle][0], 60)


class OwnedLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='UNIT_TEST_LIFECYCLE_', dir=ROOT / 'tmp')
        self.folder = Path(self.tmp.name).resolve()
        self.assertTrue(self.folder.is_relative_to(ROOT / 'tmp'))
        self.guard = self.folder / 'pending.json'
    def tearDown(self): self.tmp.cleanup()

    def run_wait(self, clock, tree, deadline=5., signature=None):
        proc = Mock(pid=100)
        proc.poll.side_effect = lambda: 0 if clock() >= tree.root_exit or tree.killed else None
        result = life.wait_owned_tree(proc, self.folder, deadline, self.guard,
            clock=clock, sleep=clock.sleep, tree_factory=lambda *a, **k: tree,
            signature=signature or (lambda _: ('UNIT_TEST_CONSTANT_SIGNATURE',)))
        return proc, result

    def test_descendants_outlive_launcher_and_late_output_restarts_quiet_period(self):
        clock = Clock(); tree = Tree(clock)
        def signature(_):
            return ('UNIT_TEST_SIGNATURE', 1 if clock() < 1.25 else 2)
        proc, result = self.run_wait(clock, tree, signature=signature)
        self.assertGreaterEqual(clock(), 2.)
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['status'], 'PROCESS_EXITED_NOT_YET_VALIDATED')
        self.assertTrue(result['lifecycle']['observed_owned_all_exited'])
        self.assertGreaterEqual(result['lifecycle']['output_quiet_seconds_observed'], .75)
        self.assertTrue(result['lifecycle']['native_completion_required_separately'])
        self.assertFalse(tree.killed)
        self.assertTrue(tree.closed)
        self.assertFalse(self.guard.exists())
        self.assertEqual(list(self.folder.iterdir()), [])  # no fabricated banner/output
        proc.kill.assert_not_called()

    def test_original_deadline_includes_owned_cleanup_and_never_returns_success(self):
        clock = Clock(); tree = Tree(clock, root_exit=100, child_exit=100)
        _, result = self.run_wait(clock, tree, deadline=2.)
        self.assertLessEqual(clock(), 2.)
        self.assertTrue(tree.killed)
        self.assertIsNone(result['returncode'])
        self.assertEqual(result['status'], 'TIMEOUT_OWN_PROCESS_TREE_TERMINATED')
        self.assertFalse(result['lifecycle']['output_drain_passed'])
        self.assertFalse(self.guard.exists())

    def test_stuck_owned_process_persists_identity_guard_and_blocks_next_launch(self):
        clock = Clock(); tree = Tree(clock, child_exit=100, stuck=True)
        _, result = self.run_wait(clock, tree, deadline=2.)
        self.assertLessEqual(clock(), 2.)
        self.assertEqual(result['status'], 'OWNED_PROCESS_CLEANUP_UNRESOLVED')
        self.assertIsNone(result['returncode'])
        api = Api(); api.records[123] = (20, 0)
        with self.assertRaisesRegex(RuntimeError, 'next launch blocked'):
            life.ensure_no_pending_owned(self.guard, api)
        self.assertEqual(api.killed, [])
        # A reused PID with a different creation time is unrelated and untouched.
        api.records[123] = (99, 0)
        life.ensure_no_pending_owned(self.guard, api)
        self.assertFalse(self.guard.exists())
        self.assertEqual(api.killed, [])

    def test_tracking_failure_fails_closed_and_never_invents_completion(self):
        clock = Clock(); proc = Mock(pid=100); proc.poll.return_value = None
        def failed(*args, **kwargs): raise OSError('UNIT_TEST_TRACKING_FAILURE')
        result = life.wait_owned_tree(proc, self.folder, 2., self.guard, clock=clock,
                                      sleep=clock.sleep, tree_factory=failed)
        proc.kill.assert_called_once()
        self.assertIsNone(result['returncode'])
        self.assertTrue(json.loads(self.guard.read_text())['unobserved_children_possible'])
        with self.assertRaisesRegex(RuntimeError, 'tracking failed'):
            life.ensure_no_pending_owned(self.guard, Api())

    def test_nonzero_owned_engine_exit_is_not_hidden_by_launcher_zero(self):
        clock = Clock(); tree = Tree(clock, child_code=7)
        _, result = self.run_wait(clock, tree)
        self.assertEqual(result['lifecycle']['launcher_returncode'], 0)
        self.assertIsNone(result['returncode'])
        self.assertEqual(result['status'], 'OWNED_DESCENDANT_EXIT_NONZERO')
        self.assertTrue(result['lifecycle']['native_completion_required_separately'])

    def test_handle_pinned_lineage_finds_grandchild_and_rejects_reused_parent_pid(self):
        api = Api(); clock = Clock(); proc = Mock(pid=100, _handle=100)
        tree = life.OwnedTree(proc, api=api, clock=clock)
        tree.scan()
        self.assertEqual(set(tree.entries), {100, 200, 300})
        self.assertNotIn(999, api.opened)  # unrelated root never opened or recorded
        self.assertIn(400, api.closed)  # parent exited before unrelated child creation
        api.records[200] = (20, 40)
        tree.terminate_owned()
        self.assertEqual(api.killed, [300])
        tree.close()
        self.assertNotIn(100, api.closed)  # borrowed Popen root handle is not closed
        self.assertIn(200, api.closed)
        self.assertIn(300, api.closed)

    def test_missing_pending_process_is_cleared_without_any_termination(self):
        self.guard.write_text(json.dumps({'owned_processes': [{'pid': 12345, 'created_filetime': 1}],
                                         'unobserved_children_possible': False}))
        api = Api()
        life.ensure_no_pending_owned(self.guard, api)
        self.assertFalse(self.guard.exists())
        self.assertEqual(api.killed, [])

    def test_reused_child_pid_is_rejected_after_refresh_and_marks_lineage_uncertain(self):
        api = Api()
        api.records[100] = (10, 0)
        snapshots = iter([[(200, 100)], [(200, 999)]])
        api.snapshot = lambda: next(snapshots)
        tree = life.OwnedTree(Mock(pid=100, _handle=100), api=api)
        tree.scan()
        self.assertEqual(set(tree.entries), {100})
        self.assertTrue(tree.uncertain_lineage)
        self.assertEqual(api.killed, [])
        self.assertIn(200, api.closed)

    def test_vanished_observed_child_cannot_hide_a_surviving_grandchild(self):
        api = Api(); del api.records[200]
        tree = life.OwnedTree(Mock(pid=100, _handle=100), api=api)
        tree.scan()
        self.assertTrue(tree.uncertain_lineage)
        self.assertEqual(tree.missed_short_lived, 1)
        self.assertNotIn(300, tree.entries)
        clock = Clock(); mocked = Tree(clock); mocked.uncertain_lineage = True
        _, result = self.run_wait(clock, mocked)
        self.assertEqual(result['status'], 'OWNED_PROCESS_CLEANUP_UNRESOLVED')
        self.assertTrue(json.loads(self.guard.read_text())['unobserved_children_possible'])

    def test_running_parent_undefined_exit_filetime_is_not_a_lineage_bound(self):
        api = Api(); api.records[100] = (10, 1)
        original_running = api.running
        api.running = lambda h: True if h == 100 else original_running(h)
        tree = life.OwnedTree(Mock(pid=100, _handle=100), api=api)
        tree.scan()
        self.assertIn(200, tree.entries)
        self.assertFalse(tree.uncertain_lineage)
        tree.close()

    def test_parent_exit_during_scan_reads_exit_time_after_signaled_state(self):
        api = Api(); api.records[100] = (10, 0)
        original_running = api.running
        def exit_on_query(handle):
            if handle == 100:
                api.records[100] = (10, 40)
                return False
            return original_running(handle)
        api.running = exit_on_query
        tree = life.OwnedTree(Mock(pid=100, _handle=100), api=api)
        tree.scan()
        self.assertIn(200, tree.entries)
        self.assertIn(300, tree.entries)
        self.assertFalse(tree.uncertain_lineage)
        tree.close()

    def test_cleanup_scans_again_after_termination_before_declaring_closure(self):
        clock = Clock()
        class LateChild(Tree):
            def __init__(self):
                super().__init__(clock, root_exit=100, child_exit=100)
                self.terminations, self.discovered = 0, False
            def scan(self):
                super().scan()
                if self.terminations == 1 and not self.discovered:
                    self.discovered, self.killed = True, False
            def terminate_owned(self):
                self.terminations += 1
                super().terminate_owned()
        tree = LateChild()
        _, result = self.run_wait(clock, tree, deadline=2.)
        self.assertTrue(tree.discovered)
        self.assertEqual(tree.terminations, 2)
        self.assertFalse(self.guard.exists())
        self.assertIsNone(result['returncode'])

    def test_atomic_guard_update_failure_preserves_prelaunch_poison(self):
        old = {'unobserved_children_possible': True, 'owned_processes': []}
        self.guard.write_text(json.dumps(old))
        with patch.object(Path, 'replace', side_effect=OSError('UNIT_TEST_STORAGE_FAILURE')):
            with self.assertRaises(OSError):
                life.write_guard(self.guard, {'unobserved_children_possible': False})
        self.assertEqual(json.loads(self.guard.read_text()), old)
        with self.assertRaisesRegex(RuntimeError, 'tracking failed'):
            life.ensure_no_pending_owned(self.guard, Api())


if __name__ == '__main__':
    unittest.main()
