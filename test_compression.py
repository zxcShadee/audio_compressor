"""
Тесты для модулей сжатия и восстановления аудио.
"""

from compression_ import normalize_audio, pre_emphasis, compress_audio
from restoration import cubic_interpolate, upsample, de_emphasis, spectral_copy
import math


# Тесты для сжатия


def test_normalize_audio_simple():
    """Тест нормализации аудио"""
    data = [0.1, 0.2, 0.3]
    result = normalize_audio(data)
    assert len(result) == 3
    assert all(-1.0 <= x <= 1.0 for x in result)


def test_normalize_audio_empty():
    """Тест нормализации пустого аудио"""
    data = []
    result = normalize_audio(data)
    assert result == []


def test_pre_emphasis_simple():
    """Тест предварительного усиления"""
    data = [0.0, 0.5, 1.0, 0.5, 0.0]
    result = pre_emphasis(data)
    assert len(result) == len(data)
    assert result[0] == data[0]


def test_pre_emphasis_short():
    """Тест предварительного усиления короткого сигнала"""
    data = [0.5]
    result = pre_emphasis(data)
    assert result == [0.5]


def test_compress_audio_simple():
    """Тест сжатия аудио"""
    data = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    rate = 44100
    result = compress_audio(data, rate)
    assert "rate" in result
    assert "bits" in result
    assert "factor" in result
    assert "data" in result
    assert result["rate"] == 22050  # 44100 / 2
    assert result["bits"] == 8
    assert result["factor"] == 2
    assert isinstance(result["data"], list)
    assert len(result["data"]) > 0


# Тесты для восстановления

def test_cubic_interpolate_middle():
    """Тест кубической интерполяции в середине"""
    result = cubic_interpolate(0, 1, 2, 3, 0.5)
    assert 1.4 < result < 1.6


def test_cubic_interpolate_edges():
    """Тест кубической интерполяции на краях"""
    p0, p1, p2, p3 = 0, 10, 20, 30
    result_t0 = cubic_interpolate(p0, p1, p2, p3, 0)
    assert abs(result_t0 - p1) < 0.001
    result_t1 = cubic_interpolate(p0, p1, p2, p3, 1)
    assert abs(result_t1 - p2) < 0.001


def test_upsample_basic():
    """Базовый тест повышения частоты дискретизации"""
    data = [0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.5, 0.0, -1.0, 0.0, 1.0, 0.5]
    factor = 2
    result = upsample(data, factor)
    assert len(result) > 0
    assert len(result) > len(data)
    assert abs(result[0] - data[0]) < 0.001


def test_de_emphasis_simple():
    """Тест обратного предварительного усиления"""
    data = [0.1, 0.2, 0.3, 0.2, 0.1]
    result = de_emphasis(data)
    assert len(result) == len(data)
    assert abs(result[0] - data[0]) < 0.001


def test_de_emphasis_empty():
    """Тест обратного предварительного усиления пустого сигнала"""
    data = []
    result = de_emphasis(data)
    assert result == []


def test_spectral_copy_basic():
    """Базовый тест спектрального копирования"""
    data = [math.sin(2 * math.pi * i / 8) for i in range(16)]
    result = spectral_copy(data)
    assert len(result) == len(data)
    assert any(abs(x) > 0.01 for x in result)


def test_spectral_copy_short():
    """Тест спектрального копирования короткого сигнала"""
    data = [1.0, 0.0, -1.0, 0.0]
    result = spectral_copy(data)
    assert len(result) == len(data)
