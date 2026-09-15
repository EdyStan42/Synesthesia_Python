import pygame
import pyaudio
import numpy as np
import random
import math

# --- 1. CONFIGURATION ---
DEVICE_INDEX = 2
RATE = 48000
CHUNK = 1024
CHANNELS = 2

WIDTH, HEIGHT = 1200, 700
CENTER = (WIDTH // 2, HEIGHT // 2)
NUM_ZONES = 20  # How many concentric "rings"
MAX_CIRCLES = 100  # Global cap to keep it clean
ZONE_STEP = 20  # Distance between each ring zone
INNER_RADIUS = 1  # Starting distance from center

# --- 2. AUDIO SETUP ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE,
                input=True, input_device_index=DEVICE_INDEX, frames_per_buffer=CHUNK)

# --- 3. PYGAME SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Radial Zone Synesthesia")
clock = pygame.time.Clock()


class FadingCircle:
    def __init__(self, zone_index, intensity):
        self.zone_index = zone_index

        # --- RADIAL POSITIONING ---
        # Pick a random angle (0 to 360 degrees)
        angle = random.uniform(0, 2 * math.pi)

        # Determine the ring boundaries for this zone
        inner_limit = INNER_RADIUS + (zone_index * ZONE_STEP)
        outer_limit = inner_limit + ZONE_STEP

        # Pick a random distance within that ring
        dist = random.uniform(inner_limit, outer_limit)

        # Convert Polar to Cartesian (x, y)
        self.x = CENTER[0] + dist * math.cos(angle)
        self.y = CENTER[1] + dist * math.sin(angle)

        # Appearance based on intensity (boosted for outer zones)
        boost = 1 + (zone_index * 0.15)
        self.radius = 2
        self.max_radius = int((intensity / 120) ) + 15
        self.opacity = 255

        # Color Gradient: Blue (Center) to Red (Edge)
        ratio = zone_index / (NUM_ZONES - 1)
        self.color = (int(255 * ratio), 50, int(255 * (1 - ratio)))

    def update(self):
        self.radius += 3
        self.opacity -= 6
        return self.opacity > 0

    def draw(self, surface):
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.opacity), (self.radius, self.radius), self.radius, 2)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))


ripples = []
zone_cooldowns = [0] * NUM_ZONES
running = True

print("Radial Zones Active!")

while running:
    screen.fill((5, 5, 15))  # Deep space background

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # 1. Capture Audio
    try:
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(raw_data, dtype=np.int16)
        fft_data = np.abs(np.fft.fft(samples))[:CHUNK // 2]
    except:
        fft_data = np.zeros(CHUNK // 2)

    # 2. Process Concentric Zones
    bins_per_zone = (len(fft_data) - 50) // NUM_ZONES

    for i in range(NUM_ZONES):
        start = 50 + (i * bins_per_zone)
        end = start + bins_per_zone
        intensity = np.mean(fft_data[start:end])

        # 3. Dynamic Threshold (drops as we go outward)
        threshold = 8000 / (1.1 ** (i + 1))

        if intensity > threshold and zone_cooldowns[i] == 0:
            if len(ripples) >= MAX_CIRCLES:
                ripples.pop(0)  # FIFO: Remove oldest

            ripples.append(FadingCircle(i, intensity))
            zone_cooldowns[i] = 0  # Cooldown

        if zone_cooldowns[i] > 0:
            zone_cooldowns[i] -= 1

    # 4. Update and Draw
    for r in ripples[:]:
        if r.update():
            r.draw(screen)
        else:
            ripples.remove(r)

    pygame.display.flip()
    clock.tick(60)

stream.stop_stream()
p.terminate()
pygame.quit()