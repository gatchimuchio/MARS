"""MARS-1 比較実験の契約。史実との同一性を検査するものではない。"""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mars1_design_lab", ROOT / "design_lab.py")
assert SPEC is not None and SPEC.loader is not None
import sys

MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class GeometryTests(unittest.TestCase):
    def test_original_numbers_and_derived_drum(self):
        self.assertEqual(MODULE.H.sections, 3)
        self.assertEqual(MODULE.H.maximum_daily_seats, 3600)
        self.assertEqual(MODULE.H.booking_days, 15)
        self.assertEqual(MODULE.H.drum_rpm, 3000)
        geometry = MODULE.derived_geometry()
        self.assertEqual(geometry["seconds_per_revolution"], 0.02)
        self.assertEqual(geometry["bits_per_track"], 2000)
        self.assertEqual(geometry["bits_per_second_per_track"], 100000)
        self.assertEqual(geometry["train_day_section_groups"], 180)
        self.assertEqual(geometry["nominal_group_bits"], 180000)
        self.assertEqual(geometry["full_occupancy_bitmap_bits"], 162000)
        self.assertEqual(geometry["model_reserved_plus_record_tracks"], 100)

    def test_hypothetical_layout_is_injective_and_within_capacity(self):
        seen = set()
        for train in range(4):
            for day in range(15):
                req = MODULE.Request(train, day, (0, 1, 2))
                positions = [MODULE.group_position(req, section) for section in req.sections]
                self.assertEqual(len({offset for _, offset in positions}), 1)
                for track, offset in positions:
                    self.assertLess(track, 200)
                    self.assertIn(offset, (0, 1000))
                    self.assertNotIn((track, offset), seen)
                    seen.add((track, offset))
        self.assertEqual(len(seen), 180)

    def test_rejects_invalid_boundaries(self):
        for req in (
            MODULE.Request(4, 0, (0,)),
            MODULE.Request(0, 15, (0,)),
            MODULE.Request(0, 0, (3,)),
            MODULE.Request(0, 0, (1, 0)),
            MODULE.Request(0, 0, (0, 0)),
            MODULE.Request(0, 0, ()),
        ):
            with self.subTest(req=req), self.assertRaises(ValueError):
                MODULE.check_request(req)


class SearchTests(unittest.TestCase):
    def test_all_strategies_preserve_same_first_fit_and_state(self):
        report = MODULE.run_experiment()
        self.assertTrue(report["all_variants_identical_booking_state"])
        variants = report["variants"]
        self.assertEqual(len({v["output_sha256"] for v in variants.values()}), 1)
        self.assertEqual(len({v["state_sha256"] for v in variants.values()}), 1)
        self.assertEqual({v["accepted"] for v in variants.values()}, {120})

    def test_search_occupies_only_requested_sections(self):
        order = (0,)
        state = {0: 0, 1: 0, 2: 0}
        for req in (MODULE.Request(0, 0, (0,)), MODULE.Request(0, 0, (1, 2))):
            seat, _ = MODULE.search_model("phase_aligned_parallel", state, req, order, 11)
            self.assertEqual(seat, 0)
            for section in req.sections:
                state[section] |= 1 << seat
        self.assertEqual(state, {0: 1, 1: 1, 2: 1})
        for variant in MODULE.VARIANTS:
            seat, ticks = MODULE.search_model(variant, state, MODULE.Request(0, 0, (1,)), order, 11)
            self.assertIsNone(seat)
            self.assertGreater(ticks, 0)
        self.assertEqual(state, {0: 1, 1: 1, 2: 1})

    def test_qualitative_timing_under_stated_surrogates(self):
        results = MODULE.run_experiment()["variants"]
        self.assertLess(results["phase_aligned_parallel"]["mean_search_seconds"],
                        results["section_by_section"]["mean_search_seconds"])
        self.assertLess(results["section_by_section"]["mean_search_seconds"],
                        results["seat_id_random_access"]["mean_search_seconds"])

    def test_seeded_repeatability_and_sensitivity(self):
        self.assertEqual(MODULE.run_experiment(seed=103), MODULE.run_experiment(seed=103))
        left = MODULE.run_experiment(seed=103)
        right = MODULE.run_experiment(seed=104)
        self.assertNotEqual(left["variants"]["seat_id_random_access"]["mean_search_seconds"],
                            right["variants"]["seat_id_random_access"]["mean_search_seconds"])
        self.assertEqual(left["all_variants_identical_booking_state"], True)
        self.assertEqual(right["all_variants_identical_booking_state"], True)

    def test_occupancy_sweep_keeps_correctness_and_changes_latency(self):
        durations = []
        for prefix in (0, 450, 760, 855):
            report = MODULE.run_experiment(seed=1960, count=60, initially_occupied=prefix)
            self.assertTrue(report["all_variants_identical_booking_state"])
            self.assertEqual(report["assumptions"]["initially_occupied_priority_prefix"], prefix)
            durations.append(report["variants"]["seat_id_random_access"]["mean_search_seconds"])
        self.assertEqual(durations, sorted(durations))

    def test_bad_strategy_and_empty_batch_are_not_silent(self):
        with self.assertRaises(ValueError):
            MODULE.run_experiment(count=0)
        with self.assertRaises(ValueError):
            MODULE.search_model("invented", {0: 0}, MODULE.Request(0, 0, (0,)), (0,), 0)


if __name__ == "__main__":
    unittest.main()
