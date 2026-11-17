import numpy as np
from parking_analyzer import ParkingAnalyzer


def test_slot_polygon_is_created_between_parallel_boundaries():
    left = (0.2, 10.0, 10, 180)
    right = (0.2, 110.0, 10, 180)
    poly = ParkingAnalyzer._slot_polygon(left, right, 200, 200)
    assert poly is not None
    assert poly.shape == (4, 2)


def test_slot_polygon_rejects_short_overlap():
    left = (0.0, 10.0, 20, 45)
    right = (0.0, 100.0, 20, 45)
    assert ParkingAnalyzer._slot_polygon(left, right, 200, 200) is None


def test_overlap_ratio_is_positive_for_box_inside_slot():
    poly = np.array([[20, 20], [120, 20], [120, 180], [20, 180]], dtype=np.int32)
    ratio = ParkingAnalyzer._overlap_ratio(poly, (40, 50, 80, 100), 200, 200)
    assert ratio > 0.95
