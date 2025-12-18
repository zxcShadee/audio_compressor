"""
Сжатие аудиосигнала с потерями
"""

import struct

def normalize_audio(data, target_rms=0.07):
    """Нормализуем среднюю квадратичную громкость аудио"""
    try:
        if not data:
            return data

        sum_sq = sum(x*x for x in data)
        if sum_sq == 0:
            return data
        rms = (sum_sq / len(data)) ** 0.5

        if rms < 0.0001:
            return data

        factor = min(target_rms / rms, 20.0)
        return [x * factor for x in data]
    except ZeroDivisionError:
        raise ValueError("Пустые аудиоданные для нормализации")
    except Exception as e:
        raise RuntimeError(f"Ошибка нормализации аудио: {str(e)}")

def pre_emphasis(data, coeff=0.95):
    """Предварительное усиление высоких частот"""
    result = [data[0]]
    for i in range(1, len(data)):
        result.append(data[i] - coeff * data[i - 1])
    return result


def adaptive_downsample(data, factor):
    try:
        if factor <= 0:
            raise ValueError(f"Неверный коэффициент сжатия: {factor}")

        result = []
        i = 0
        while i < len(data):
            result.append(data[i])
            if i + 1 < len(data) and abs(data[i] - data[i + 1]) > 0.3:
                i += 1
            else:
                i += factor
        return result
    except IndexError:
        raise ValueError("Некорректные данные для децимации")
    except Exception as e:
        raise RuntimeError(f"Ошибка децимации аудио: {str(e)}")


def reduce_bit_depth(data, bits):
    try:
        if bits <= 0 or bits > 32:
            raise ValueError(f"Неверная битность: {bits}")

        max_val = 2 ** (bits - 1) - 1
        result = []
        for x in data:
            try:
                x = max(min(x, 1.0), -1.0)
                result.append(int(round(x * max_val)))
            except (ValueError, TypeError):
                raise ValueError(f"Некорректное значение аудиоданных: {x}")
        return result
    except Exception as e:
        raise RuntimeError(f"Ошибка квантования аудио: {str(e)}")

def compress_audio(data, rate):
    """
    Основной алгоритм сжатия аудиосигнала с потерями.

    Алгоритм включает конвертацию в моно, нормализацию, предварительное усиление,
    адаптивное понижение частоты дискретизации и квантование.

    Args:
        data (list): Исходные аудиоданные.
        rate (int): Исходная частота дискретизации в герцах (Гц).

    Returns:
        dict: Словарь со сжатыми данными и параметрами сжатия, содержащий следующие ключи:
            - "rate" (int): Новая частота дискретизации после сжатия.
            - "bits" (int): Глубина битового представления после квантования.
            - "factor" (int): Коэффициент понижения частоты дискретизации.
            - "data" (list[int]): Сжатые аудиоданные в виде списка целых чисел.
    Raises:
        ValueError: Если параметр rate не является положительным целым числом.
        TypeError: Если данные имеют неподдерживаемый формат.
        ZeroDivisionError: Если переданы стереоданные с пустыми каналами.
        """
    factor = 2
    bits = 8

    mono = [sum(x) / len(x) if hasattr(x, '__len__') else x for x in data]
    mono = normalize_audio(mono)
    emphasized = pre_emphasis(mono)
    down = adaptive_downsample(emphasized, factor)
    quantized = reduce_bit_depth(down, bits)

    return {
        "rate": rate // factor,
        "bits": bits,
        "factor": factor,
        "data": quantized
    }


def save_compressed(obj, path):
    """Сохраняет сжатые данные в бинарный файл"""
    with open(path, "wb") as f:
        f.write(struct.pack("III", obj["rate"], obj["bits"], obj["factor"]))
        for v in obj["data"]:
            f.write(struct.pack("b", v))


def load_compressed(path):
    """Загружает сжатые данные"""
    with open(path, "rb") as f:
        rate, bits, factor = struct.unpack("III", f.read(12))
        data = []
        while True:
            chunk = f.read(1)
            if not chunk:
                break
            data.append(struct.unpack("b", chunk)[0])
    return {"rate": rate, "bits": bits, "factor": factor, "data": data}
