import time

import matplotlib.pyplot as plt
import numpy as np
import pyaudio

from SignalContext import SignalContext
from custom_types import Frames, Hz
from output import play_signal
from signals.BandPassSignal import BandPassSignal
from signals.ConstantSignal import ConstantSignal
from signals.ScaledSignal import ScaledSignal
from signals.SineSignal import SineSignal
from signals.StreamingSignal import StreamingSignal
from signals.SummingSignal import SummingSignal
from signals.WavSignal import WavSignal
from signals.WindowMaxSignal import WindowMaxSignal

# human hearing: 20hz - 20khz
from util.frames import to_frames

FS = Hz(44100)
MIN_FREQ = 20
MAX_FREQ = 10000
NUM_BANDS = 10
NUM_TAPS = 201

RUN_TYPE = "play"

cutoffs = np.geomspace(MIN_FREQ, MAX_FREQ, NUM_BANDS+1)
bands = list(zip(cutoffs[:-1], cutoffs[1:]))

wav = WavSignal(SignalContext({
    "uuid": "wav",
    "type": "wav",
    "file": "resources/wav/please_turn_off_the_air.wav",
}))

stream_signal = StreamingSignal(SignalContext({
    "uuid": "stream",
    "type": "stream",
    "source_fs": FS,
}))

stream_gain = ConstantSignal(SignalContext({
    "uuid": "stream-gain",
    "type": "constant",
    "value": 10,
    "dur": FS*20,
}))

stream_amp = ScaledSignal(SignalContext.with_refs({
    "uuid": "stream-amp",
    "type": "scaled",
}, {"child": stream_signal, "factor": stream_gain}))

base_signal = stream_amp

LENGTH = Frames(len(wav.get_source_buffer()))

extracted_bands = []
envelopes = []
components = []
for lower, upper in bands:
    bp = BandPassSignal(SignalContext.with_refs({
        "uuid": f"bp-{lower}-{upper}",
        "type": "bp",
        "band_start": lower,
        "band_stop": upper,
        "window": "hanning",
        "num_taps": NUM_TAPS,
    }, {"child": base_signal}))

    extracted_bands.append(bp)

    env = WindowMaxSignal(SignalContext.with_refs({
        "uuid": f"env-{lower}-{upper}",
        "type": "win_max",
        "length": 1 / (1*upper),
    }, {"child": bp}))

    envelopes.append(env)

    carrier = SineSignal(SignalContext({
        "uuid": f"carrier-{lower}",
        "type": "sine",
        "freq": lower,
        "dur": LENGTH / FS
    }))

    component = ScaledSignal(SignalContext.with_refs({
        "uuid": f"component-{lower}-{upper}",
        "type": "scaled",
    }, {"child": carrier, "factor": env}))

    components.append(component)

component_sum = SummingSignal(SignalContext.with_refs({
    "uuid": "bp_sum",
    "type": "sum"
}, {"children": components}))


if RUN_TYPE == "draw":
    fig, (axes) = plt.subplots(2+len(components), 1)
    wav_out = wav.get_temporal(FS, 0, LENGTH)
    bp_out = component_sum.get_temporal(FS, 0, LENGTH)
    axes[0].plot(wav_out)
    for i in range(len(components)):
        axes[i+1].plot(components[i].get_temporal(FS, 0, LENGTH))
        axes[i+1].plot(envelopes[i].get_temporal(FS, 0, LENGTH))
        print(extracted_bands[i].band_start)
    axes[len(components)+1].plot(bp_out, color='green')
    plt.show()
    exit()
elif RUN_TYPE == "analyze":
    fig, (axes) = plt.subplots(2, 3)
    exit()

WIDTH = 4
CHANNELS = 1
FRAMES_PER_BUFFER = 256

p = pyaudio.PyAudio()


RECORD_LEN = 5*FS

in_buf = np.zeros(RECORD_LEN)
out_buf = np.zeros(RECORD_LEN)
frames = 0


def callback(in_data, frame_count, time_info, status):
    global frames
    # print(f"got here: {frames} + {frame_count}")
    start = time.time_ns()
    buf = np.frombuffer(in_data, dtype=np.float32)
    in_buf[frames:frames+len(buf)] = buf
    stream_signal.put_data(buf)
    _, upper = stream_signal.get_range(FS)
    out = component_sum.get_temporal(FS, to_frames(upper-len(buf)), to_frames(upper))
    out_buf[frames:frames+len(buf)] = out

    frames += len(buf)

    if frames + len(buf) > RECORD_LEN:
        flag = pyaudio.paComplete
    else:
        flag = pyaudio.paContinue

    result = out.astype(np.float32).tobytes()

    end = time.time_ns()

    print(f"took {end-start} ns for {len(buf)/FS*1000000000} ns of data")

    return result, flag


stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=FS,
                input=True,
                output=True,
                frames_per_buffer=FRAMES_PER_BUFFER,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.01)

stream.stop_stream()
stream.close()

p.terminate()

print(f"frames processed: {frames}")
print(f"streamed length: {stream_signal.dur}")

fig, (axes) = plt.subplots(5, 1)
axes[0].plot(in_buf[:frames])
axes[1].plot(stream_signal.get_temporal(FS, 0, frames))
axes[2].plot(stream_amp.get_temporal(FS, 0, frames))
axes[3].plot(component_sum.get_temporal(FS, 0, frames))
axes[4].plot(out_buf[:frames])
plt.show()
