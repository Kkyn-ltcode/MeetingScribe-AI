import wave

def merge_wavs(output_file, input_files):
    with wave.open(output_file, 'wb') as out:
        for i, f in enumerate(input_files):
            with wave.open(f, 'rb') as w:
                if i == 0:
                    out.setparams(w.getparams())
                out.writeframes(w.readframes(w.getnframes()))
            print(f"Added {f}")
    print(f"Merged into {output_file}")

merge_wavs("bnw.wav", [
    "narrator.wav",
    "director1.wav",
    "narrator2.wav",
    "director2.wav",
    "director3.wav"
])