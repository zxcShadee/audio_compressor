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

    Raises:
        FileNotFoundError: файл не найден
        PermissionError: нет прав на чтение
        RuntimeError: ошибка библиотеки soundfile
    """
    try:
        data, rate = sf.read(path)
        return data, rate
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {path}")
    except PermissionError:
        raise PermissionError(f"Нет прав на чтение файла: {path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла {path}: {str(e)}")


def write_wav(path, data, rate):
    """
    Записывает WAV файл.

    Args:
        path (str): путь сохранения
        data (list): аудиоданные
        rate (int): частота дискретизации

    Raises:
        ValueError: неверные данные или параметры
        PermissionError: нет прав на запись
        RuntimeError: ошибка библиотеки soundfile
    """
    try:
        # Проверка входных данных
        if not data:
            raise ValueError("Пустые аудиоданные")
        if rate <= 0:
            raise ValueError(f"Неверная частота дискретизации: {rate}")

        sf.write(path, data, rate)
    except ValueError as e:
        raise ValueError(f"Неверные параметры записи: {str(e)}")
    except PermissionError:
        raise PermissionError(f"Нет прав на запись в файл: {path}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при записи файла {path}: {str(e)}")
