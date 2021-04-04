import numpy as np
import sounddevice as sd

# TODO: copy over audio code
# TODO: graph RMS intensity over time, real-time?
# TODO: graph with LPF as well


# TODO: figure out how InputStream works...? Stays alive in another thread?




"""
def process_sound(indata, frames, time, status):
    print(indata.shape)

    norm = np.linalg.norm(indata)*10
    norm = min(norm, 100)

    print(norm)
    print("|" * int(norm))


    


with sd.InputStream(samplerate=11025, blocksize=256, channels=1, dtype=np.float32, latency='low', callback=process_sound):
    sd.sleep(10000)

"""
