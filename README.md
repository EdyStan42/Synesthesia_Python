# Audio-Reactive Planetary Visualizer

## Overview
This project is a real-time, audio-reactive visualizer built in Python. It captures live audio input and translates the frequency spectrum into a dynamic, orbiting solar system. The central "Sun" throbs in time with the heavy bass, while a series of orbiting "planets" react to the mid and high frequencies. As the planets orbit, their colors map beautifully across a spectrum from deep blue (inner orbits) to vibrant red (outer orbits), leaving a smooth motion-blur trail behind them.

![Example_video](VideoProject5.mp4)

## Requirements & Setup
To run this visualizer, you will need Python installed on your machine along with a few external libraries. 

Install the required dependencies using pip:
* `pip install pygame`
* `pip install pyaudio`
* `pip install numpy`

**Audio Routing Note:** 
This script is designed to listen to your system's audio output. To achieve this, you will need a virtual audio routing tool (like VB-Audio Virtual Cable on Windows or BlackHole on macOS). You must route your desktop audio through this virtual cable and set the `DEVICE_INDEX` in the script to match the cable's input index.

## How It Works
The visualizer uses `pyaudio` to capture chunks of audio data and `numpy` to perform a Fast Fourier Transform (FFT), breaking the audio signal down into its component frequencies.

* **The Sun (Bass):** The lowest frequency bins (indices 2 to 10) are averaged and mapped to the central body. It features a custom glowing effect and throbs based on bass intensity.
* **The Planets (Mids/Highs):** The remaining frequency spectrum is divided evenly among the 70 orbiting planets.
* **Dynamic Scaling:** The outer planets receive an exponential multiplier (`1.01 ** i`) to their intensity. High frequencies carry less energy than bass, so this ensures the outer planets still react visibly to the music.

## Configuration
You can easily tweak the visualizer's behavior by modifying the variables at the top of the script:
* `DEVICE_INDEX`: Change this to match your specific audio input device.
* `NUM_PLANETS`: Adjusts the number of orbiting bodies (default is 70).
* `ROTATION_BASE_SPEED`: Controls how fast the planets orbit the sun.
* `WIDTH` / `HEIGHT`: Sets the size of the Pygame window.

## Troubleshooting: Finding Your Device Index
If the visualizer crashes on startup or doesn't react to audio, you likely have the wrong `DEVICE_INDEX`. Run this short script in your terminal or IDE to list all available audio devices and find the correct index for your virtual audio cable:

```python
import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Index {i}: {info['name']}")
p.terminate()
