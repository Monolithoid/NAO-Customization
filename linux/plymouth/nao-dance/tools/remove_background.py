"""Segment extracted video frames; install rembg[cpu]==2.0.87 first."""
import argparse
from pathlib import Path
from PIL import Image
from rembg import new_session, remove

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', type=Path, help='Directory containing frame-XX.png')
parser.add_argument('output', type=Path, help='Output directory for RGBA frames')
args = parser.parse_args()
files = sorted(args.input.glob('frame-*.png'))
if not files:
    parser.error('No input frames found')
args.output.mkdir(parents=True, exist_ok=True)
session = new_session('birefnet-general-lite', providers=['CPUExecutionProvider'])
for source in files:
    with Image.open(source) as image:
        cutout = remove(image.convert('RGB'), session=session)
    cutout.save(args.output / source.name)
    print(source.name, flush=True)
