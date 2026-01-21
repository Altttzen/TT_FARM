import random
import time

def sleep_jitter(base: float, jitter: float = 0.35):
    time.sleep(max(0.05, random.uniform(base - jitter, base + jitter)))

def chance(p: float) -> bool:
    return random.random() < p
