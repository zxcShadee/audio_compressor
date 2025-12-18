"""
Функции для чтения и записи WAV файлов.
"""

import soundfile as sf


def read_wav(path):
    """
    Читает WAV файл.

    Args:
        path (str): путь к файлу

    Returns:
        tuple: (samples, sample_rate)
    """
    data, rate = sf.read(path)
    return data, rate


def write_wav(path, data, rate):
    """
    Записывает WAV файл.

    Args:
        path (str): путь сохранения
        data (list): аудиоданные
        rate (int): частота дискретизации
    """
    sf.write(path, data, rate)
