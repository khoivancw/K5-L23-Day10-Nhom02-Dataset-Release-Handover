"""Self-check for the detection <-> panoptic cross-check (region_hint), no dataset needed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validator"))
from validate import overlap, region_hint  # noqa: E402


def grid(x, y, w, h, step=2):
    """Sampled mask points filling a rectangle, like mask_samples does."""
    return [(px, py) for py in range(y, y + h, step) for px in range(x, x + w, step)]


def seg(box):
    return {"bbox": box}


class OverlapTest(unittest.TestCase):
    def test_identical_and_disjoint(self):
        self.assertEqual(overlap([0, 0, 10, 10], [0, 0, 10, 10]), 1)
        self.assertEqual(overlap([0, 0, 10, 10], [20, 20, 5, 5]), 0)

    def test_half_shift(self):
        self.assertAlmostEqual(overlap([0, 0, 10, 10], [5, 0, 10, 10]), 50 / 150)


class RegionHintTest(unittest.TestCase):
    box = [10, 10, 30, 30]

    def hint(self, name, detections, box=None):
        box = box or self.box
        result = region_hint(seg(box), name, grid(*box), detections)
        return result and result[1]

    def test_consistent_pair_is_not_flagged(self):
        self.assertIsNone(self.hint("chair", [("chair", self.box)]))

    def test_same_place_different_class(self):
        self.assertEqual(self.hint("chair", [("couch", self.box)]), "class_disagreement")

    def test_large_mask_without_box(self):
        self.assertEqual(self.hint("chair", []), "missing_box")

    def test_shifted_box_same_class(self):
        self.assertEqual(self.hint("chair", [("chair", [25, 10, 30, 30])]), "bbox_drift")

    def test_one_mask_over_two_boxes(self):
        wide = [0, 0, 60, 30]
        boxes = [("chair", [0, 0, 30, 30]), ("chair", [30, 0, 30, 30])]
        self.assertEqual(self.hint("chair", boxes, wide), "instance_merge")

    def test_tiny_segment_is_ignored(self):
        self.assertIsNone(region_hint(seg([0, 0, 4, 4]), "chair", grid(0, 0, 4, 4), []))


if __name__ == "__main__":
    unittest.main()
