from compression import reduce_bit_depth, adaptive_downsample


def test_adaptive_downsample_positive():
    data = [0, 1, 2, 3, 4]
    result = adaptive_downsample(data, 2)
    assert len(result) > 0


def test_adaptive_downsample_empty():
    data = []
    assert adaptive_downsample(data, 2) == []


def test_reduce_bit_depth():
    data = [0.0, 1.0, -1.0]
    result = reduce_bit_depth(data, 8)
    assert len(result) == 3
