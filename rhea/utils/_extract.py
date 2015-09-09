

def extract_freq(clock, f=1):
    if hasattr(clock, 'frequency'):
        freq = clock.frequency
    else:
        freq = f
    return freq