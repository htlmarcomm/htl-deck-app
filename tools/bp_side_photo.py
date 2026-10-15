# -*- coding: utf-8 -*-
"""Builds the building photo for the project slides' left panel from the supplied BFSI
screenshot: the whole panel, with the white title lettering painted out (so the title
stays editable text). Prints the /media path."""
import hashlib
import io
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT = sys.argv[1]

raw = cv2.imread(SHOT)
crop = raw[16:893, 19:401].copy()  # the whole panel, 382 x 877 (same shape as 314 x 720)
h, w = crop.shape[:2]
lo = crop.min(axis=2)
mask = np.zeros((h, w), np.uint8)
mask[:250, :270][lo[:250, :270] > 205] = 255  # white lettering sits in the top 250px, left 270px
mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
clean = cv2.inpaint(crop, mask, 5, cv2.INPAINT_TELEA)
im = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB))
buf = io.BytesIO()
im.save(buf, "JPEG", quality=92)
data = buf.getvalue()
name = hashlib.sha1(data).hexdigest()[:16] + ".jpg"
open(os.path.join(ROOT, "public", "media", name), "wb").write(data)
print("/media/" + name)
