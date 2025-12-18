"""
Восстановление аудио: кубическая интерполяция
и спектральное копирование на основе FFT
"""

import math
from compression_ import normalize_audio


def cubic_interpolate(p0, p1, p2, p3, t):
    """Кубическая интерполяция"""
    a = (-0.5*p0) + (1.5*p1) - (1.5*p2) + (0.5*p3)
    b = p0 - (2.5*p1) + (2*p2) - (0.5*p3)
    c = (-0.5*p0) + (0.5*p2)
    d = p1
    return a*t**3 + b*t**2 + c*t + d


def upsample(data, factor):
    try:
        if factor <= 0:
            raise ValueError(f"Неверный коэффициент интерполяции: {factor}")
        if len(data) < 4:
            raise ValueError("Недостаточно данных для интерполяции (нужно минимум 4 точки)")

        result = []
        for i in range(len(data) - 3):
            result.append(data[i])
            for j in range(1, factor):
                t = j / factor
                result.append(cubic_interpolate(
                    data[i], data[i+1], data[i+2], data[i+3], t))
        return result
    except IndexError:
        raise ValueError("Индекс вне диапазона при интерполяции")
    except Exception as e:
        raise RuntimeError(f"Ошибка интерполяции аудио: {str(e)}")

def fft(signal):
    """Рекурсивная реализация БПФ"""
    n = len(signal)
    if n <= 1:
        return signal
    even = fft(signal[0::2])
    odd = fft(signal[1::2])
    result = [0] * n
    for k in range(n // 2):
        angle = -2 * math.pi * k / n
        w = complex(math.cos(angle), math.sin(angle))
        result[k] = even[k] + w * odd[k]
        result[k + n // 2] = even[k] - w * odd[k]
    return result


def ifft(freq):
    """Обратное БПФ"""
    conj = [x.conjugate() for x in freq]
    time = fft(conj)
    return [x.conjugate().real / len(freq) for x in time]


def spectral_copy(data):
    try:
        if not data:
            return data

        n = len(data)
        if n == 0:
            return data

        padded = data + [0.0] * (2**math.ceil(math.log2(n)) - n)
        spectrum = fft(padded)

        half = len(spectrum) // 2
        for i in range(half // 2, half):
            spectrum[i] *= 0.5
            spectrum[i + half] = spectrum[i].conjugate()

        restored = ifft(spectrum)
        return restored[:n]
    except ValueError as e:
        raise ValueError(f"Ошибка в данных для спектрального копирования: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Ошибка спектрального копирования: {str(e)}")

def de_emphasis(data, coeff=0.95):
    """
    Обратное предварительному усилению (pre-emphasis)
    Восстанавливает исходный частотный баланс
    """
    if not data:
        return data

    result = [data[0]]
    for i in range(1, len(data)):
        result.append(data[i] + coeff * result[i - 1])

    return result


def restore_audio(obj):
    """
    Полное восстановление аудиосигнала из сжатого формата.

    Функция выполняет многоступенчатое восстановление аудиоданных, включая повышение
    частоты дискретизации, спектральное копирование высоких частот, обратное
    предварительное усиление и нормализацию. Алгоритм предназначен для работы
    с данными, сжатыми функцией `compress_audio`.

    Args:
        obj (dict): Словарь со сжатыми аудиоданными, полученный от `compress_audio`
            или загруженный из файла через `load_compressed`. Должен содержать:
            - "factor" (int): Коэффициент понижения частоты дискретизации при сжатии.
              Должен быть положительным целым числом (обычно 2).
            - "data" (list[int]): Сжатые аудиоданные в виде списка целых чисел.
              Значения должны быть в диапазоне от -127 до 127 для 8-битного формата.
            - "rate" (int): Частота дискретизации после сжатия в герцах (Гц).
              Должна быть положительным целым числом.

    Returns:
        tuple: Кортеж из двух элементов:
            - restored (list[float]): Восстановленные аудиоданные в виде списка
              значений с плавающей точкой в диапазоне [-1.0, 1.0].
              Длина массива составляет примерно len(obj["data"]) * obj["factor"].
            - restored_rate (int): Восстановленная частота дискретизации в герцах.
              Рассчитывается как obj["rate"] * obj["factor"].

    Raises:
        KeyError: Если входной словарь не содержит обязательных ключей:
                  "factor", "data", "rate".
        TypeError: Если "data" не является списком или "factor"/"rate" не целые числа.
        ValueError: Если "factor" или "rate" не положительные числа.
        ZeroDivisionError: Если "factor" равен нулю.
        """
    factor = obj["factor"]

    up = upsample(obj["data"], factor)

    restored = spectral_copy(up)

    restored = de_emphasis(restored)

    restored = normalize_audio(restored)

    return restored, obj["rate"] * factor
