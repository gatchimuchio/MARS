import concurrent.futures
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mars101_lab import (  # noqa: E402
    AuditError,
    DivergenceError,
    RequestError,
    ReservationMachine,
    new_request,
)


class EndToEndReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mars101-test-")
        self.path = Path(self.temporary.name) / "state.json"
        self.machine = ReservationMachine(self.path)
        self.machine.initialize()

    def tearDown(self):
        self.temporary.cleanup()

    def ask(self, operation, *, origin="A", destination="C", count=1):
        return self.machine.submit(
            new_request(operation, train="TEST-101", **{"from": origin, "to": destination}, count=count)
        )

    def test_all_the_way_from_terminal_to_ticket_and_audit(self):
        self.assertEqual(self.ask("INQUIRE")["available"], 6)
        ticket = self.ask("RESERVE", count=2)
        self.assertEqual(ticket["seats"], ["1-01", "1-02"])
        self.assertEqual(ticket["fare"], 400)  # 2 sections, 2 seats, 100 units
        self.assertEqual(self.ask("INQUIRE")["available"], 4)
        self.assertEqual(self.machine.audit()["events"], 3)
        self.assertEqual(ReservationMachine(self.path).audit()["status"], "PASS")

    def test_segmentwise_reuse_without_same_segment_double_booking(self):
        first = self.ask("RESERVE", origin="A", destination="B")
        second = self.ask("RESERVE", origin="B", destination="C")
        self.assertEqual(first["seats"], second["seats"])
        whole = self.ask("RESERVE", origin="A", destination="C")
        self.assertNotEqual(first["seats"], whole["seats"])
        self.assertEqual(self.machine.audit()["status"], "PASS")

    def test_cancel_only_releases_its_own_occupied_segments(self):
        first = self.ask("RESERVE", origin="A", destination="B")
        other = self.ask("RESERVE", origin="B", destination="C")
        self.assertEqual(first["seats"], other["seats"])
        response = self.machine.submit(new_request("CANCEL", reservation=first["reservation"]))
        self.assertEqual(response["status"], "OK")
        self.assertEqual(self.ask("INQUIRE", origin="A", destination="B")["available"], 6)
        self.assertEqual(self.ask("INQUIRE", origin="B", destination="C")["available"], 5)
        self.assertEqual(self.machine.audit()["status"], "PASS")

    def test_idempotent_request_retry(self):
        request = new_request("RESERVE", train="TEST-101", **{"from": "A", "to": "D"}, count=1)
        response = self.machine.submit(request)
        self.assertEqual(self.machine.submit(request), response)
        self.assertEqual(len(self.machine.history()), 1)
        conflicting = dict(request, count=2)
        with self.assertRaises(RequestError):
            self.machine.submit(conflicting)
        self.assertEqual(self.machine.audit()["status"], "PASS")

    def test_sold_out_never_overbooks(self):
        seats = [self.ask("RESERVE")["seats"][0] for _ in range(6)]
        self.assertEqual(len(set(seats)), 6)
        self.assertEqual(self.ask("RESERVE")["status"], "SOLD_OUT")
        self.assertEqual(self.machine.audit()["status"], "PASS")

    def test_divergence_cannot_be_silently_committed(self):
        request = new_request("RESERVE", train="TEST-101", **{"from": "A", "to": "C"})
        with self.assertRaises(DivergenceError):
            self.machine.submit(request, inject_divergence="B")
        self.assertEqual(self.machine.audit()["events"], 0)
        self.assertEqual(self.ask("INQUIRE")["available"], 6)

    def test_invalid_request_has_no_side_effect(self):
        with self.assertRaises(RequestError):
            self.ask("RESERVE", origin="C", destination="A")
        with self.assertRaises(RequestError):
            self.ask("RESERVE", count=0)
        self.assertEqual(self.machine.audit()["events"], 0)

    def test_tampered_inventory_fails_audit(self):
        self.ask("RESERVE")
        doc = json.loads(self.path.read_text(encoding="utf-8"))
        doc["A"]["occupancy"]["TEST-101"][0] ^= 1
        self.path.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaises(AuditError):
            self.machine.audit()

    def test_many_terminals_cannot_double_sell(self):
        # Multiple machine instances simulate separate terminal users/processes.
        def concurrent_reserve(index):
            machine = ReservationMachine(self.path)
            request = {
                "request_id": f"terminal-{index}",
                "op": "RESERVE",
                "train": "TEST-101",
                "from": "A",
                "to": "D",
            }
            return machine.submit(request)

        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(concurrent_reserve, range(14)))
        successful = [value["seats"][0] for value in results if value["status"] == "OK"]
        self.assertEqual(len(successful), 6)
        self.assertEqual(len(set(successful)), 6)
        self.assertEqual(self.machine.audit()["events"], 14)

    def test_independent_terminal_processes_cannot_double_sell(self):
        root = Path(__file__).resolve().parents[1]
        commands = [
            [
                sys.executable,
                str(root / "mars101_lab.py"),
                "reserve",
                "--state",
                str(self.path),
                "--from",
                "A",
                "--to",
                "D",
                "--request-id",
                f"process-{index}",
            ]
            for index in range(9)
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=9) as pool:
            completed = list(
                pool.map(
                    lambda command: subprocess.run(command, capture_output=True, text=True),
                    commands,
                )
            )
        self.assertTrue(all(item.returncode == 0 for item in completed))
        results = [json.loads(item.stdout) for item in completed]
        successful = [item["seats"][0] for item in results if item["status"] == "OK"]
        self.assertEqual(len(successful), 6)
        self.assertEqual(len(set(successful)), 6)
        self.assertEqual(self.machine.audit()["events"], 9)

    def test_demo_cli(self):
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            [sys.executable, str(root / "mars101_lab.py"), "demo"],
            capture_output=True,
            text=True,
            check=True,
        )
        responses = json.loads(completed.stdout)
        self.assertEqual(responses[-1]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
