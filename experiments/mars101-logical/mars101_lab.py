#!/usr/bin/env python3
"""MARS-101-inspired, executable *logical* reconstruction experiment.

This is a modern test harness, NOT a port of HITAC-3030 software, a replica of
the original terminal protocol, or an interface to any railway system.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import tempfile
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


FORMAT = "MARS101-LAB-LOGICAL-V1"

# Entirely fictitious data. The historical MARS-101 timetable, fares, encoding,
# carriage ordering, and seat-allocation priorities have not been recovered.
DEMO_PLAN = {
    "TEST-101": {
        "stops": ["A", "B", "C", "D"],
        "seats": ["1-01", "1-02", "1-03", "1-04", "2-01", "2-02"],
        "fare_per_segment": 100,
    }
}


class RequestError(ValueError):
    """An invalid or contradictory request, with no committed state change."""


class DivergenceError(RuntimeError):
    """The two independently calculated lanes cannot be safely reconciled."""


class AuditError(RuntimeError):
    """Stored events or inventory do not match deterministic replay."""


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def blank_lane(plan: dict) -> dict:
    return {
        "occupancy": {
            train: [0] * (len(info["stops"]) - 1)
            for train, info in plan.items()
        },
        "reservations": {},
    }


def empty_document(plan: dict | None = None) -> dict:
    plan = copy.deepcopy(plan if plan is not None else DEMO_PLAN)
    if not plan:
        raise ValueError("at least one fictitious train is required")
    for train, info in plan.items():
        if len(info["stops"]) < 2 or len(set(info["stops"])) != len(info["stops"]):
            raise ValueError(f"invalid stop order for {train}")
        if not info["seats"] or len(set(info["seats"])) != len(info["seats"]):
            raise ValueError(f"invalid seat inventory for {train}")
        if not isinstance(info["fare_per_segment"], int) or info["fare_per_segment"] < 0:
            raise ValueError("fare_per_segment must be a nonnegative integer")
    return {
        "format": FORMAT,
        "plan": plan,
        "A": blank_lane(plan),
        "B": blank_lane(plan),
        "events": [],
    }


@contextmanager
def process_lock(lock_path: Path) -> Iterator[None]:
    """Single-writer lock for concurrent terminals, on Linux and Windows."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0)
            lock_file.write(b"0")
            lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def atomic_write(path: Path, document: dict, *, replace: bool) -> None:
    """Commit state+audit records together; preserve prior state on failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not replace and path.exists():
        raise FileExistsError(f"already exists: {path}")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=".mars101-", delete=False
        ) as output:
            temporary = output.name
            output.write(canonical(document))
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        temporary = None
        if os.name != "nt":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def read_document(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if document.get("format") != FORMAT:
        raise AuditError("unknown reconstruction-state format")
    return document


def table_lookup(plan: dict, request: dict) -> tuple[str, int, int, dict]:
    """TC: resolve train and station symbols into seat-file segment indices."""
    train = request.get("train")
    if train not in plan:
        raise RequestError("unknown train")
    info = plan[train]
    start, end = request.get("from"), request.get("to")
    if start not in info["stops"] or end not in info["stops"]:
        raise RequestError("unknown station")
    left, right = info["stops"].index(start), info["stops"].index(end)
    if left >= right:
        raise RequestError("the boarding station must precede the destination")
    return train, left, right, info


def available_mask(occupancy: list[int], left: int, right: int, seat_count: int) -> int:
    """FC: overlay segment occupancy patterns to find interval-wide vacancies."""
    occupied = 0
    for segment in range(left, right):
        occupied |= occupancy[segment]
    return ((1 << seat_count) - 1) & ~occupied


def seat_indices(mask: int, seat_count: int) -> list[int]:
    return [index for index in range(seat_count) if (mask >> index) & 1]


def lane_execute(lane: dict, plan: dict, request: dict, sequence: int) -> dict:
    """Each independent FC lane applies the same validated request."""
    operation = request.get("op")
    if operation == "CANCEL":
        reservation_id = request.get("reservation")
        if not isinstance(reservation_id, str) or not reservation_id:
            raise RequestError("reservation id required")
        booking = lane["reservations"].get(reservation_id)
        if booking is None or not booking["active"]:
            return {"status": "NOT_FOUND", "reservation": reservation_id}
        train = booking["train"]
        occupied = lane["occupancy"][train]
        for segment in range(booking["left"], booking["right"]):
            for index in booking["seat_indices"]:
                bit = 1 << index
                if not (occupied[segment] & bit):
                    raise AuditError("inconsistent seat file during cancellation")
                occupied[segment] &= ~bit
        booking["active"] = False
        return {"status": "OK", "operation": "CANCEL", "reservation": reservation_id}

    if operation not in {"INQUIRE", "RESERVE"}:
        raise RequestError("op must be INQUIRE, RESERVE, or CANCEL")

    train, left, right, info = table_lookup(plan, request)
    count = request.get("count", 1)
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 16:
        raise RequestError("count must be an integer from 1 to 16 (lab bound)")

    mask = available_mask(lane["occupancy"][train], left, right, len(info["seats"]))
    indices = seat_indices(mask, len(info["seats"]))
    if operation == "INQUIRE":
        return {
            "status": "OK",
            "operation": "INQUIRE",
            "train": train,
            "from": request["from"],
            "to": request["to"],
            "available": len(indices),
        }
    if len(indices) < count:
        return {"status": "SOLD_OUT", "operation": "RESERVE", "available": len(indices)}

    # The historical car-selection/seat-packing priority is not documented in
    # enough detail for exact reproduction. Stable first-fit is a lab surrogate.
    selected = indices[:count]
    for segment in range(left, right):
        for index in selected:
            bit = 1 << index
            if lane["occupancy"][train][segment] & bit:
                raise AuditError("seat collision")
            lane["occupancy"][train][segment] |= bit
    reservation = f"L{sequence:06d}"
    lane["reservations"][reservation] = {
        "train": train,
        "left": left,
        "right": right,
        "seat_indices": selected,
        "active": True,
    }
    return {
        "status": "OK",
        "operation": "RESERVE",
        "reservation": reservation,
        "train": train,
        "from": request["from"],
        "to": request["to"],
        "seats": [info["seats"][index] for index in selected],
        "fare": (right - left) * info["fare_per_segment"] * count,
        "ticket": "LAB-ONLY / NOT VALID FOR TRAVEL",
    }


def compute_event(document: dict, request: dict, *, corrupt_lane: str | None = None) -> dict:
    """SC: apply to independent copies, final cross-check, then commit."""
    if not isinstance(request.get("request_id"), str) or not request["request_id"]:
        raise RequestError("non-empty request_id required")
    sequence = len(document["events"]) + 1
    result_a = lane_execute(document["A"], document["plan"], request, sequence)
    result_b = lane_execute(document["B"], document["plan"], request, sequence)
    if corrupt_lane in {"A", "B"}:
        train = next(iter(document["plan"]))
        document[corrupt_lane]["occupancy"][train][0] ^= 1
    if result_a != result_b or digest(document["A"]) != digest(document["B"]):
        raise DivergenceError("dual-lane comparison failed; no transaction committed")

    previous = document["events"][-1]["hash"] if document["events"] else "GENESIS"
    record = {
        "seq": sequence,
        "request": copy.deepcopy(request),
        "response": result_a,
        "previous": previous,
        "lane_digest": digest(document["A"]),
    }
    record["hash"] = digest(record)
    document["events"].append(record)
    return result_a


def verify(document: dict) -> dict:
    """Independently replay every recorded request and compare all resulting state."""
    replay = empty_document(document["plan"])
    seen: set[str] = set()
    try:
        for recorded in document["events"]:
            rid = recorded["request"]["request_id"]
            if rid in seen:
                raise AuditError(f"duplicate request id in event {recorded['seq']}")
            seen.add(rid)
            response = compute_event(replay, recorded["request"])
            if response != recorded["response"] or replay["events"][-1] != recorded:
                raise AuditError(f"event verification failed at {recorded['seq']}")
    except (RequestError, DivergenceError, KeyError, TypeError, ValueError) as exc:
        raise AuditError(f"history is not replayable: {exc}") from exc
    if replay != document:
        raise AuditError("stored inventory or journal diverges from replay")
    return {
        "status": "PASS",
        "events": len(document["events"]),
        "lane_digest": digest(document["A"]),
        "last_event_hash": document["events"][-1]["hash"] if document["events"] else None,
    }


class ReservationMachine:
    """Single logical MARS-101 experiment with dual simulated file lanes."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._thread_lock = threading.RLock()
        self._lock_path = self.path.with_name(self.path.name + ".lock")

    def initialize(self, plan: dict | None = None) -> None:
        with self._thread_lock, process_lock(self._lock_path):
            atomic_write(self.path, empty_document(plan), replace=False)

    def submit(self, request: dict, *, inject_divergence: str | None = None) -> dict:
        with self._thread_lock, process_lock(self._lock_path):
            document = read_document(self.path)
            verify(document)
            rid = request.get("request_id")
            for event in document["events"]:
                if event["request"]["request_id"] == rid:
                    if event["request"] != request:
                        raise RequestError("request_id already used for different input")
                    return copy.deepcopy(event["response"])
            candidate = copy.deepcopy(document)
            response = compute_event(candidate, request, corrupt_lane=inject_divergence)
            atomic_write(self.path, candidate, replace=True)
            return response

    def audit(self) -> dict:
        return verify(read_document(self.path))

    def history(self) -> list[dict]:
        doc = read_document(self.path)
        verify(doc)
        return doc["events"]


def new_request(operation: str, **kwargs: Any) -> dict:
    return {"request_id": str(uuid.uuid4()), "op": operation, **kwargs}


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MARS-101 public-design logic experiment")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "inquire", "reserve", "cancel", "audit", "history"):
        sub = commands.add_parser(command)
        sub.add_argument("--state", required=True, help="local experimental state JSON path")
        if command in ("inquire", "reserve"):
            sub.add_argument("--train", default="TEST-101")
            sub.add_argument("--from", dest="origin", required=True)
            sub.add_argument("--to", dest="destination", required=True)
        if command == "reserve":
            sub.add_argument("--count", type=int, default=1)
        if command == "cancel":
            sub.add_argument("--reservation", required=True)
        if command in ("inquire", "reserve", "cancel"):
            sub.add_argument("--request-id", help="reuse exact ID for an idempotent retry")
    commands.add_parser("demo", help="run a complete ephemeral terminal-to-audit demonstration")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_cli().parse_args(argv)
    try:
        if args.command == "demo":
            with tempfile.TemporaryDirectory(prefix="mars101-lab-") as directory:
                machine = ReservationMachine(Path(directory) / "state.json")
                machine.initialize()
                outputs = [
                    machine.submit(new_request("INQUIRE", train="TEST-101", **{"from": "A", "to": "C"})),
                    machine.submit(new_request("RESERVE", train="TEST-101", **{"from": "A", "to": "C"}, count=2)),
                    machine.submit(new_request("INQUIRE", train="TEST-101", **{"from": "A", "to": "C"})),
                    machine.audit(),
                ]
                print(json.dumps(outputs, ensure_ascii=False, indent=2))
                return 0

        machine = ReservationMachine(args.state)
        if args.command == "init":
            machine.initialize()
            output = {"status": "INITIALIZED", "state": args.state}
        elif args.command == "audit":
            output = machine.audit()
        elif args.command == "history":
            output = machine.history()
        elif args.command == "cancel":
            request = {
                "request_id": args.request_id or str(uuid.uuid4()),
                "op": "CANCEL",
                "reservation": args.reservation,
            }
            output = machine.submit(request)
        else:
            request = {
                "request_id": args.request_id or str(uuid.uuid4()),
                "op": args.command.upper(),
                "train": args.train,
                "from": args.origin,
                "to": args.destination,
            }
            if args.command == "reserve":
                request["count"] = args.count
            output = machine.submit(request)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (FileExistsError, FileNotFoundError, OSError, ValueError, AuditError, DivergenceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
