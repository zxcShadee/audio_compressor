"""
Точка входа в программу.
Пользователь выбирает режим: сжатие или восстановление.
"""

from audio_io import read_wav, write_wav
from compression_ import compress_audio, save_compressed, load_compressed
from restoration import restore_audio


def main():
    try:
        mode = input("Введите режим (compress / restore): ").strip()

        if mode == "compress":
            path = input("Введите путь к WAV файлу: ").strip()
            data, rate = read_wav(path)
            compressed = compress_audio(data, rate)
            save_compressed(compressed, "compressed.bin")
            print("Файл сжат: compressed.bin")

        elif mode == "restore":
            path = input("Введите путь к compressed.bin: ").strip()
            compressed = load_compressed(path)
            restored, rate = restore_audio(compressed)
            write_wav("restored.wav", restored, rate)
            print("Файл восстановлен: restored.wav")

        else:
            raise ValueError("Неизвестный режим")

    except Exception as exc:
        print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()
