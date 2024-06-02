import matplotlib.pyplot as plt
import numpy as np
import os
import psutil
from scipy.io import wavfile
from scipy.signal import spectrogram

def print_memory_usage(stage):
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"{stage}: RSS = {mem_info.rss / (1024 ** 2):.2f} MB, VMS = {mem_info.vms / (1024 ** 2):.2f} MB")

def analyze_wav(file_path, block_size):
    print_memory_usage("Start")
    

    # Einlesen der WAV-Datei
    sample_rate, data = wavfile.read(file_path)
    samples, channels = data.shape
    

    print(f"Sample Rate: {sample_rate} Hz")
    print_memory_usage("After reading WAV file")

    # Falls das Signal Stereo ist, nur einen Kanal verwenden
    if len(data.shape) == 2:
        data = data[:, 0]
    print_memory_usage("After extracting one channel")

    # Berechnung des Spektrogramms
    f, t, Sxx = spectrogram(data, fs=sample_rate, window='hann', nperseg=block_size, noverlap=700, scaling='spectrum')
    print_memory_usage("After computing spectrogram")

    # Plot des Spektrogramms
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.title('Spectrogram of the WAV file with Block size = ' + str(block_size))
    plt.colorbar(label='Intensity [dB]')
    plt.show()
    print_memory_usage("After plotting")

# Pfad zur WAV-Datei und Blockgröße
file_path = './songs/nicht_zu_laut_abspielen.wav'
block_size = 1024  # Blockgröße

# Aufrufen der Funktion
analyze_wav(file_path, block_size)
