# Audio Processing and Music Information Retrieval
import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fftpack import fft, fftfreq
import pyaudio
import wave
import music21
from pydub import AudioSegment
import mir_eval
import essentia
import aubio

def audio_signal_processing():
    """Digital signal processing for audio"""
    try:
        # Generate test audio signals
        duration = 5.0  # seconds
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create complex audio signal
        # Fundamental frequency + harmonics
        fundamental = 440  # A4
        signal_audio = (
            0.6 * np.sin(2 * np.pi * fundamental * t) +  # Fundamental
            0.3 * np.sin(2 * np.pi * 2 * fundamental * t) +  # 2nd harmonic
            0.15 * np.sin(2 * np.pi * 3 * fundamental * t) +  # 3rd harmonic
            0.05 * np.random.randn(len(t))  # Noise
        )
        
        # Apply audio effects
        # Low-pass filter
        nyquist = sample_rate / 2
        cutoff = 2000  # Hz
        b, a = signal.butter(4, cutoff / nyquist, btype='low')
        filtered_signal = signal.filtfilt(b, a, signal_audio)
        
        # Amplitude modulation
        mod_freq = 5  # Hz
        mod_signal = filtered_signal * (1 + 0.3 * np.sin(2 * np.pi * mod_freq * t))
        
        # Reverb simulation (simple delay)
        delay_samples = int(0.1 * sample_rate)  # 100ms delay
        reverb_signal = np.copy(mod_signal)
        reverb_signal[delay_samples:] += 0.3 * mod_signal[:-delay_samples]
        
        # Spectral analysis
        freqs, times, spectrogram = signal.spectrogram(reverb_signal, sample_rate, nperseg=1024)
        
        # Peak detection in frequency domain
        fft_signal = np.abs(fft(reverb_signal[:sample_rate]))  # First second
        fft_freqs = fftfreq(sample_rate, 1/sample_rate)[:sample_rate//2]
        peaks, _ = signal.find_peaks(fft_signal[:sample_rate//2], height=np.max(fft_signal)*0.1)
        
        # Audio features extraction
        # Zero crossing rate
        zcr = np.sum(np.diff(np.sign(reverb_signal)) != 0) / (2 * len(reverb_signal))
        
        # RMS energy
        frame_size = 1024
        hop_length = 512
        rms_energy = []
        for i in range(0, len(reverb_signal) - frame_size, hop_length):
            frame = reverb_signal[i:i + frame_size]
            rms = np.sqrt(np.mean(frame**2))
            rms_energy.append(rms)
        
        # Spectral centroid
        magnitude_spectrum = np.abs(fft(reverb_signal[:frame_size]))
        freqs_frame = fftfreq(frame_size, 1/sample_rate)[:frame_size//2]
        spectral_centroid = np.sum(freqs_frame * magnitude_spectrum[:frame_size//2]) / np.sum(magnitude_spectrum[:frame_size//2])
        
        return {
            'sample_rate': sample_rate,
            'signal_duration': duration,
            'fundamental_freq': fundamental,
            'num_harmonics': 3,
            'filter_cutoff': cutoff,
            'delay_ms': 100,
            'spectrogram_shape': spectrogram.shape,
            'num_peaks_detected': len(peaks),
            'zero_crossing_rate': zcr,
            'average_rms_energy': np.mean(rms_energy),
            'spectral_centroid_hz': spectral_centroid,
            'processing_steps': 8
        }
        
    except Exception as e:
        return {'error': str(e)}

def music_analysis():
    """Music information retrieval and analysis"""
    try:
        # Generate synthetic music data for analysis
        sample_rate = 22050
        duration = 10.0
        
        # Create a simple melody with chord progression
        def generate_note(frequency, duration, sample_rate, amplitude=0.5):
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            # ADSR envelope simulation
            attack_time = 0.1
            decay_time = 0.2
            sustain_level = 0.7
            release_time = 0.3
            
            envelope = np.ones_like(t)
            attack_samples = int(attack_time * sample_rate)
            decay_samples = int(decay_time * sample_rate)
            release_samples = int(release_time * sample_rate)
            
            # Attack
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
            # Decay
            envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain_level, decay_samples)
            # Release
            envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
            
            note = amplitude * envelope * np.sin(2 * np.pi * frequency * t)
            return note
        
        # Note frequencies (C major scale)
        notes = {
            'C4': 261.63,
            'D4': 293.66,
            'E4': 329.63,
            'F4': 349.23,
            'G4': 392.00,
            'A4': 440.00,
            'B4': 493.88,
            'C5': 523.25
        }
        
        # Create melody
        melody_sequence = ['C4', 'E4', 'G4', 'C5', 'G4', 'E4', 'C4']
        note_duration = 0.8
        
        melody = np.array([])
        for note_name in melody_sequence:
            note_signal = generate_note(notes[note_name], note_duration, sample_rate)
            melody = np.concatenate([melody, note_signal])
        
        # Pad to full duration
        if len(melody) < sample_rate * duration:
            padding = np.zeros(int(sample_rate * duration) - len(melody))
            melody = np.concatenate([melody, padding])
        else:
            melody = melody[:int(sample_rate * duration)]
        
        # Music feature extraction
        # Tempo estimation using autocorrelation
        def estimate_tempo(signal, sr):
            # Onset detection
            hop_length = 512
            onset_envelope = np.diff(np.abs(signal))
            onset_envelope = np.maximum(0, onset_envelope)
            
            # Autocorrelation for tempo
            autocorr = np.correlate(onset_envelope, onset_envelope, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peaks corresponding to beat intervals
            min_tempo = 60  # BPM
            max_tempo = 200  # BPM
            min_interval = int(60 / max_tempo * sr / hop_length)
            max_interval = int(60 / min_tempo * sr / hop_length)
            
            if max_interval < len(autocorr):
                tempo_candidates = autocorr[min_interval:max_interval]
                if len(tempo_candidates) > 0:
                    peak_idx = np.argmax(tempo_candidates) + min_interval
                    tempo = 60 / (peak_idx * hop_length / sr)
                    return tempo
            return 120  # Default tempo
        
        estimated_tempo = estimate_tempo(melody, sample_rate)
        
        # Key detection simulation
        def detect_key(signal, sr):
            # Simplified key detection using chroma features
            n_fft = 2048
            hop_length = 512
            
            # Compute short-time Fourier transform
            stft = np.abs(np.array([fft(signal[i:i+n_fft]) for i in range(0, len(signal)-n_fft, hop_length)]))
            
            # Map to chroma (12 semitones)
            chroma = np.zeros((stft.shape[0], 12))
            freqs = fftfreq(n_fft, 1/sr)
            
            for i, freq in enumerate(freqs[:n_fft//2]):
                if freq > 0:
                    # Convert frequency to MIDI note
                    midi_note = 12 * np.log2(freq / 440) + 69  # A4 = 440Hz = MIDI 69
                    chroma_idx = int(midi_note) % 12
                    chroma[:, chroma_idx] += stft[:, i]
            
            # Average chroma over time
            avg_chroma = np.mean(chroma, axis=0)
            
            # Key profiles (major and minor scales)
            major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
            minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
            
            # Find best matching key
            max_correlation = -1
            detected_key = 'C major'
            
            for tonic in range(12):
                major_corr = np.corrcoef(avg_chroma, np.roll(major_profile, tonic))[0, 1]
                minor_corr = np.corrcoef(avg_chroma, np.roll(minor_profile, tonic))[0, 1]
                
                if major_corr > max_correlation:
                    max_correlation = major_corr
                    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                    detected_key = f"{note_names[tonic]} major"
                
                if minor_corr > max_correlation:
                    max_correlation = minor_corr
                    detected_key = f"{note_names[tonic]} minor"
            
            return detected_key, max_correlation
        
        detected_key, key_confidence = detect_key(melody, sample_rate)
        
        # Rhythm analysis
        def analyze_rhythm(signal, sr):
            # Beat tracking using onset detection
            hop_length = 512
            frame_length = 1024
            
            # Onset strength
            onset_frames = []
            for i in range(0, len(signal) - frame_length, hop_length):
                frame = signal[i:i + frame_length]
                frame_energy = np.sum(frame**2)
                onset_frames.append(frame_energy)
            
            onset_frames = np.array(onset_frames)
            
            # Find peaks in onset strength
            peaks, _ = signal.find_peaks(onset_frames, height=np.mean(onset_frames) * 1.5)
            
            # Calculate inter-onset intervals
            if len(peaks) > 1:
                intervals = np.diff(peaks) * hop_length / sr
                avg_interval = np.mean(intervals)
                rhythm_regularity = 1 / (1 + np.std(intervals))
            else:
                avg_interval = 0
                rhythm_regularity = 0
            
            return len(peaks), avg_interval, rhythm_regularity
        
        num_onsets, avg_onset_interval, rhythm_regularity = analyze_rhythm(melody, sample_rate)
        
        # Harmonic analysis
        def analyze_harmony(signal, sr):
            # Pitch detection using autocorrelation
            def autocorr_pitch(signal, sr, min_freq=80, max_freq=1000):
                autocorr = np.correlate(signal, signal, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                
                # Find the peak in the valid pitch range
                min_period = int(sr / max_freq)
                max_period = int(sr / min_freq)
                
                if max_period < len(autocorr):
                    valid_range = autocorr[min_period:max_period]
                    if len(valid_range) > 0:
                        peak_idx = np.argmax(valid_range) + min_period
                        pitch = sr / peak_idx
                        return pitch
                return 0
            
            # Segment signal and detect pitches
            segment_length = sr // 4  # 250ms segments
            pitches = []
            
            for i in range(0, len(signal) - segment_length, segment_length // 2):
                segment = signal[i:i + segment_length]
                pitch = autocorr_pitch(segment, sr)
                if pitch > 0:
                    pitches.append(pitch)
            
            unique_pitches = len(set(pitches)) if pitches else 0
            avg_pitch = np.mean(pitches) if pitches else 0
            
            return unique_pitches, avg_pitch
        
        unique_pitches, avg_pitch = analyze_harmony(melody, sample_rate)
        
        return {
            'melody_length': len(melody),
            'sample_rate': sample_rate,
            'notes_in_sequence': len(melody_sequence),
            'estimated_tempo_bpm': estimated_tempo,
            'detected_key': detected_key,
            'key_confidence': key_confidence,
            'num_onsets': num_onsets,
            'avg_onset_interval_sec': avg_onset_interval,
            'rhythm_regularity': rhythm_regularity,
            'unique_pitches': unique_pitches,
            'average_pitch_hz': avg_pitch,
            'analysis_features': 6
        }
        
    except Exception as e:
        return {'error': str(e)}

def audio_synthesis():
    """Digital audio synthesis techniques"""
    try:
        sample_rate = 44100
        duration = 3.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Subtractive synthesis
        def subtractive_synth(freq, t, sample_rate):
            # Generate rich waveform
            sawtooth = signal.sawtooth(2 * np.pi * freq * t)
            
            # Apply low-pass filter with envelope-controlled cutoff
            envelope = np.exp(-2 * t)  # Exponential decay
            cutoff_freq = 1000 + 2000 * envelope  # Varying cutoff
            
            # Apply filter (simplified)
            nyquist = sample_rate / 2
            filtered_signal = np.copy(sawtooth)
            
            # Simple resonant low-pass simulation
            for i, cutoff in enumerate(cutoff_freq):
                if cutoff < nyquist:
                    norm_cutoff = cutoff / nyquist
                    if norm_cutoff > 0 and norm_cutoff < 1:
                        b, a = signal.butter(2, norm_cutoff, btype='low')
                        # Apply filter to small segment
                        start_idx = max(0, i - 512)
                        end_idx = min(len(filtered_signal), i + 512)
                        if end_idx > start_idx:
                            segment = filtered_signal[start_idx:end_idx]
                            filtered_segment = signal.filtfilt(b, a, segment)
                            filtered_signal[start_idx:end_idx] = filtered_segment
            
            # Apply amplitude envelope
            amplitude_env = envelope * 0.5
            return filtered_signal * amplitude_env
        
        subtractive_sound = subtractive_synth(220, t, sample_rate)  # A3
        
        # FM synthesis
        def fm_synth(carrier_freq, modulator_freq, mod_index, t):
            # Frequency modulation
            modulator = np.sin(2 * np.pi * modulator_freq * t)
            carrier_phase = 2 * np.pi * carrier_freq * t + mod_index * modulator
            fm_signal = np.sin(carrier_phase)
            
            # Apply envelope
            envelope = np.exp(-t / 1.5)  # Slower decay
            return fm_signal * envelope * 0.3
        
        fm_sound = fm_synth(440, 220, 2.0, t)  # Carrier: A4, Modulator: A3
        
        # Additive synthesis
        def additive_synth(fundamental, harmonics, t):
            signal = np.zeros_like(t)
            
            for i, (harmonic_num, amplitude) in enumerate(harmonics):
                freq = fundamental * harmonic_num
                harmonic_signal = amplitude * np.sin(2 * np.pi * freq * t)
                
                # Individual envelope for each harmonic
                envelope = np.exp(-t * (1 + i * 0.5))
                signal += harmonic_signal * envelope
            
            return signal * 0.2
        
        # Harmonic series with decreasing amplitudes
        harmonics = [(1, 1.0), (2, 0.5), (3, 0.33), (4, 0.25), (5, 0.2)]
        additive_sound = additive_synth(330, harmonics, t)  # E4
        
        # Granular synthesis
        def granular_synth(source_signal, grain_size, overlap, pitch_shift):
            grain_samples = int(grain_size * sample_rate)
            hop_size = int(grain_samples * (1 - overlap))
            
            output = np.zeros_like(t)
            
            # Window function for grains
            window = signal.hann(grain_samples)
            
            grain_count = 0
            for i in range(0, len(source_signal) - grain_samples, hop_size):
                if i + grain_samples < len(output):
                    # Extract grain
                    grain = source_signal[i:i + grain_samples] * window
                    
                    # Pitch shift by resampling
                    if pitch_shift != 1.0:
                        new_length = int(len(grain) / pitch_shift)
                        if new_length > 0:
                            indices = np.linspace(0, len(grain) - 1, new_length)
                            grain = np.interp(indices, np.arange(len(grain)), grain)
                            
                            # Pad or truncate to original size
                            if len(grain) > grain_samples:
                                grain = grain[:grain_samples]
                            elif len(grain) < grain_samples:
                                grain = np.pad(grain, (0, grain_samples - len(grain)), 'constant')
                    
                    # Add grain to output
                    output[i:i + len(grain)] += grain
                    grain_count += 1
            
            return output * 0.1, grain_count
        
        # Use additive synthesis as source for granular
        granular_sound, grain_count = granular_synth(additive_sound, 0.1, 0.5, 1.5)  # 100ms grains, 50% overlap, 1.5x pitch
        
        # Physical modeling - simple string simulation
        def string_model(length, tension, density, pluck_position, t, sample_rate):
            # Karplus-Strong algorithm simulation
            delay_line_length = int(sample_rate / (440 * length))  # Simplified
            delay_line = np.random.uniform(-1, 1, delay_line_length) * 0.5
            
            output = np.zeros(len(t))
            
            for i in range(len(t)):
                # Get current sample from delay line
                output[i] = delay_line[0]
                
                # Low-pass filter and feedback
                filtered_sample = 0.996 * (delay_line[0] + delay_line[1]) / 2  # Simple averaging filter
                
                # Shift delay line
                delay_line[:-1] = delay_line[1:]
                delay_line[-1] = filtered_sample
            
            return output * 0.3
        
        string_sound = string_model(1.0, 1.0, 1.0, 0.3, t, sample_rate)
        
        # Combine all synthesis methods
        combined_sound = (
            0.25 * subtractive_sound +
            0.25 * fm_sound +
            0.25 * additive_sound +
            0.25 * granular_sound
        )
        
        # Normalize
        if np.max(np.abs(combined_sound)) > 0:
            combined_sound = combined_sound / np.max(np.abs(combined_sound)) * 0.8
        
        return {
            'sample_rate': sample_rate,
            'synthesis_duration': duration,
            'subtractive_freq': 220,
            'fm_carrier_freq': 440,
            'fm_mod_index': 2.0,
            'additive_harmonics': len(harmonics),
            'grain_count': grain_count,
            'string_model_delay_samples': int(sample_rate / 440),
            'synthesis_methods': 5,
            'output_max_amplitude': np.max(np.abs(combined_sound)),
            'output_rms': np.sqrt(np.mean(combined_sound**2))
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Audio processing and music information retrieval...")
    
    # Audio signal processing
    dsp_result = audio_signal_processing()
    if 'error' not in dsp_result:
        print(f"DSP: {dsp_result['processing_steps']} steps, {dsp_result['num_peaks_detected']} peaks, ZCR: {dsp_result['zero_crossing_rate']:.4f}")
    
    # Music analysis
    music_result = music_analysis()
    if 'error' not in music_result:
        print(f"Music: Tempo {music_result['estimated_tempo_bpm']:.1f} BPM, Key: {music_result['detected_key']}")
    
    # Audio synthesis
    synth_result = audio_synthesis()
    if 'error' not in synth_result:
        print(f"Synthesis: {synth_result['synthesis_methods']} methods, {synth_result['grain_count']} grains generated")