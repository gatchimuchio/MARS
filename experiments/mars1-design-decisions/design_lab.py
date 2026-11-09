"""MARS-1 制約下の設計判断を比較する再現可能な*代用*実験。

史実の回路・ソフトウェア・性能を再実装したものではない。原典 S17 の数値と
実験者が選んだ仮定を明示的に分離する。外部依存・実鉄道への接続はない。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from dataclasses import asdict, dataclass


SOURCE_ID = "S17"
SOURCE_URL = "https://www.hitachihyoron.com/jp/pdf/1961/ex39/1961_ex_39_09.pdf"


@dataclass(frozen=True)
class HistoricalInputs:
    """S17 原著の掲載値（'約'・'以内'などの限定は報告書に保持する）。"""

    trains: int = 4  # S17 PDF p.2: 取扱列車数
    booking_days: int = 15  # p.2: 予約期間
    maximum_daily_seats: int = 3600  # p.2: 取扱座席数
    maximum_seats_per_train: int = 900  # p.2: 上限
    sections: int = 3  # p.2: 区間数（31ではない）
    drum_rpm: int = 3000  # p.6: 磁気ドラム
    drum_tracks: int = 200  # p.6: 全トラック
    drum_bits: int = 400000  # p.6: 原著記載値。S22と対立あり
    bits_per_group: int = 1000  # p.6: 半トラック=列車×区間×日
    register_tracks_approx: int = 10  # p.6: 約10トラック
    logic_clock_hz_approx: int = 100000  # p.4: 約100kc
    telegraph_baud: int = 50  # p.2: 電信回線
    central_average_s_approx: float = 0.1  # p.2: 平均
    transmission_min_s: float = 1.7  # p.2: 情報伝送
    transmission_max_s: float = 2.6  # p.2: 情報伝送
    total_time_bound_s: float = 3.0  # p.2: 全処理時間、以内


H = HistoricalInputs()


def derived_geometry(h: HistoricalInputs = H) -> dict[str, float | int]:
    """原著にない派生値。実記憶割当・実演算時間ではない。"""
    if h.drum_rpm <= 0 or h.drum_tracks <= 0:
        raise ValueError("invalid drum geometry")
    if h.drum_bits % h.drum_tracks:
        raise ValueError("track bits must be integral")
    bits_per_track = h.drum_bits // h.drum_tracks
    if bits_per_track != 2 * h.bits_per_group:
        raise ValueError("two half-track groups are required by this model")
    groups = h.trains * h.booking_days * h.sections
    model_tracks = h.register_tracks_approx + (
        (h.trains * h.booking_days + 1) // 2
    ) * h.sections
    if model_tracks > h.drum_tracks:
        raise ValueError("synthetic layout exceeds the specified drum")
    return {
        "seconds_per_revolution": 60 / h.drum_rpm,
        "bits_per_track": bits_per_track,
        "bits_per_second_per_track": bits_per_track * h.drum_rpm / 60,
        "seconds_per_bit": 60 / (h.drum_rpm * bits_per_track),
        "train_day_section_groups": groups,
        "nominal_group_bits": groups * h.bits_per_group,
        "model_reserved_plus_record_tracks": model_tracks,
        "theoretical_unassigned_bits": h.drum_bits - model_tracks * bits_per_track,
        "full_occupancy_bitmap_bits": groups * h.maximum_seats_per_train,
    }


@dataclass(frozen=True)
class Request:
    train: int
    day: int
    sections: tuple[int, ...]


def check_request(req: Request, h: HistoricalInputs = H) -> None:
    if not (0 <= req.train < h.trains and 0 <= req.day < h.booking_days):
        raise ValueError("outside train/day boundary")
    if not req.sections or tuple(sorted(set(req.sections))) != req.sections:
        raise ValueError("sections must be unique and ordered")
    if not all(0 <= section < h.sections for section in req.sections):
        raise ValueError("outside section boundary")


def group_position(req: Request, section: int, h: HistoricalInputs = H) -> tuple[int, int]:
    """SURROGATE: 同じ列車・日の3区間を同位相の別トラックへ配置する。"""
    check_request(req, h)
    if section not in req.sections:
        raise ValueError("section not requested")
    group = req.train * h.booking_days + req.day
    track = h.register_tracks_approx + (group // 2) * h.sections + section
    offset = (group % 2) * h.bits_per_group
    if track >= h.drum_tracks:
        raise ValueError("model layout overflow")
    return track, offset


def priority_order(seats: int, seed: int) -> tuple[int, ...]:
    """SURROGATE: 好まれる座席順の内容は不明なので固定乱数順を使用。"""
    order = list(range(seats))
    random.Random(seed).shuffle(order)
    return tuple(order)


def first_free(
    state: dict[int, int], order: tuple[int, ...], sections: tuple[int, ...]
) -> tuple[int, int] | None:
    for rank, seat in enumerate(order):
        if all((state[section] & (1 << seat)) == 0 for section in sections):
            return rank, seat
    return None


def wait_ticks(phase: int, bit_position: int, bits_per_track: int) -> int:
    return (bit_position - phase % bits_per_track) % bits_per_track


def encode_track_block(
    state: dict[int, int], section: int, order: tuple[int, ...],
    placement: str,
) -> int:
    """1,000-bit領域の占有パルス。物理への書込・保持処理は時間計上外。"""
    if placement == "priority":
        physically_ordered_seats = order
    elif placement == "seat_id":
        physically_ordered_seats = tuple(range(len(order)))
    else:
        raise ValueError("unknown record arrangement")
    bits = 0
    for position, seat in enumerate(physically_ordered_seats):
        if state[section] & (1 << seat):
            bits |= 1 << position
    return bits


def search_model(
    variant: str,
    state: dict[int, int],
    req: Request,
    order: tuple[int, ...],
    ready_phase: int,
    h: HistoricalInputs = H,
) -> tuple[int | None, int]:
    """1 tick = 1bit転送時間。電子回路の演算・照合等は含まない。"""
    check_request(req, h)
    if not order or len(order) > h.maximum_seats_per_train:
        raise ValueError("invalid seat catalog")
    if set(order) != set(range(len(order))):
        raise ValueError("order is not a permutation")
    geometry = derived_geometry(h)
    circumference = int(geometry["bits_per_track"])
    offset = group_position(req, req.sections[0], h)[1]

    if variant == "phase_aligned_parallel":
        # 原著の「好まれる順への配列」「シリアル探索」から着想。
        # 各区間の読みを同時に扱う仮定は原機の確定再現ではない。
        tracks = {section: encode_track_block(state, section, order, "priority")
                  for section in req.sections}
        seat = None
        searched = len(order)
        for rank, candidate in enumerate(order):
            if all(not (tracks[section] & (1 << rank)) for section in req.sections):
                seat, searched = candidate, rank + 1
                break
        elapsed = wait_ticks(ready_phase, offset, circumference) + searched
        return seat, elapsed
    elif variant == "section_by_section":
        # 代案：同じ優先順データを区間ごとに全件走査して合成。
        elapsed = 0
        conflicting_positions = 0
        for section in req.sections:
            _, start = group_position(req, section, h)
            elapsed += wait_ticks(ready_phase + elapsed, start, circumference)
            elapsed += len(order)
            conflicting_positions |= encode_track_block(state, section, order, "priority")
        seat = next((candidate for rank, candidate in enumerate(order)
                     if not conflicting_positions & (1 << rank)), None)
        return seat, elapsed
    elif variant == "seat_id_random_access":
        # 代案：ドラム上の「座席ID順」から、要求の優先順にランダム参照。
        # 優先順は上と同一。回転待ちと1bit読みだけを計上する。
        elapsed = 0
        tracks = {section: encode_track_block(state, section, order, "seat_id")
                  for section in req.sections}
        for seat in order:
            available = True
            for section in req.sections:
                _, start = group_position(req, section, h)
                bit = start + seat
                elapsed += wait_ticks(ready_phase + elapsed, bit, circumference) + 1
                if tracks[section] & (1 << seat):
                    available = False
                    break
            if available:
                return seat, elapsed
        return None, elapsed
    else:
        raise ValueError(f"unknown variant: {variant}")


VARIANTS = (
    "phase_aligned_parallel",
    "section_by_section",
    "seat_id_random_access",
)


def run_experiment(seed: int = 1960, count: int = 120, initially_occupied: int = 760) -> dict:
    """同じ架空の注文・同じ位相で、在庫正当性と探索時間のみ比較。"""
    if count < 1:
        raise ValueError("count must be positive")
    h = H
    seats = h.maximum_seats_per_train
    if not 0 <= initially_occupied <= seats:
        raise ValueError("occupied prefix outside seat catalog")
    order = priority_order(seats, seed)
    # SURROGATE: 検索順の先頭N席を既売とする仮想負荷条件。
    occupied_mask = sum(1 << seat for seat in order[:initially_occupied])
    initial_state = {section: occupied_mask for section in range(h.sections)}
    shapes = ((0,), (1,), (2,), (0, 1), (1, 2), (0, 1, 2))
    requests = [Request(train=0, day=0, sections=shapes[i % len(shapes)]) for i in range(count)]
    phase_rng = random.Random(seed ^ 0x5EED)
    circumference = int(derived_geometry(h)["bits_per_track"])
    tick_s = float(derived_geometry(h)["seconds_per_bit"])
    phases = [phase_rng.randrange(circumference) for _ in requests]

    variants: dict[str, dict] = {}
    fingerprints: set[tuple[str, str]] = set()
    for variant in VARIANTS:
        state = dict(initial_state)
        times: list[float] = []
        transcript: list[dict] = []
        for number, (req, phase) in enumerate(zip(requests, phases), start=1):
            seat, ticks = search_model(variant, state, req, order, phase, h)
            expected = first_free(state, order, req.sections)
            if seat != (expected[1] if expected else None):
                raise AssertionError("strategy diverged from independent reference")
            if seat is not None:
                if any(state[section] & (1 << seat) for section in req.sections):
                    raise AssertionError("overlapping reservation")
                for section in req.sections:
                    state[section] |= 1 << seat
            transcript.append({"request": number, "sections": req.sections, "seat": seat})
            times.append(ticks * tick_s)

        transcript_digest = hashlib.sha256(
            json.dumps(transcript, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        state_digest = hashlib.sha256(
            json.dumps({str(k): hex(v) for k, v in sorted(state.items())}, sort_keys=True).encode()
        ).hexdigest()
        fingerprints.add((transcript_digest, state_digest))
        sorted_times = sorted(times)
        p95_index = (95 * len(sorted_times) + 99) // 100 - 1
        variants[variant] = {
            "requests": len(transcript),
            "accepted": sum(x["seat"] is not None for x in transcript),
            "rejected": sum(x["seat"] is None for x in transcript),
            "mean_search_seconds": round(statistics.mean(times), 6),
            "p95_search_seconds": round(sorted_times[p95_index], 6),
            "max_search_seconds": round(max(times), 6),
            "illustrative_mean_with_midpoint_transmission_seconds": round(
                statistics.mean(times) + (h.transmission_min_s + h.transmission_max_s) / 2,
                6,
            ),
            "output_sha256": transcript_digest,
            "state_sha256": state_digest,
        }

    if len(fingerprints) != 1:
        raise AssertionError("different booking outcomes; performance comparison invalid")

    return {
        "experiment_id": "MARS1-CONSTRAINT-DECISION-001",
        "class": "LOGICAL_EXPERIMENT / SURROGATE; not historical hardware",
        "evidence": {"source_id": SOURCE_ID, "source_url": SOURCE_URL, "pages": [2, 4, 5, 6]},
        "historical_inputs": asdict(h),
        "derived_geometry": derived_geometry(h),
        "assumptions": {
            "model": "half-track groups for each train/day/section; aligned tracks per train/day",
            "priority": f"permutation of 0..{seats-1} from seed {seed}, not historical seating order",
            "initially_occupied_priority_prefix": initially_occupied,
            "simulated_train_day": [0, 0],
            "request_pattern": [list(s) for s in shapes],
            "arrival_phase": f"uniform 0..1999 ticks, seed xor 0x5EED; identical across variants",
            "timing_excludes": ["logic gates", "retries", "reliability comparison", "other controller work", "queueing", "mechanical printing"],
            "historical_terminal_protocol_not_modeled": True,
            "transmission_midpoint_used_only_as_illustration": True,
            "preknowledge": "comparator informed by S17: NOT an independent blind redesign",
        },
        "all_variants_identical_booking_state": True,
        "variants": variants,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "geometry"])
    parser.add_argument("--seed", type=int, default=1960)
    parser.add_argument("--requests", type=int, default=120)
    parser.add_argument("--occupied-prefix", type=int, default=760)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    if args.command == "geometry":
        result = {"historical_inputs": asdict(H), "derived_geometry": derived_geometry()}
    else:
        result = run_experiment(seed=args.seed, count=args.requests,
                                initially_occupied=args.occupied_prefix)
    if args.summary and args.command == "run":
        print("MARS-1 SURROGATE | identical booking state:", result["all_variants_identical_booking_state"])
        for key, value in result["variants"].items():
            print(f"{key:26s} mean={value['mean_search_seconds']:.6f}s "
                  f"p95={value['p95_search_seconds']:.6f}s "
                  f"accepted={value['accepted']} rejected={value['rejected']}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
