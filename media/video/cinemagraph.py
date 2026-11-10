"""Turn the Artlist Garden clip into a crisp, locked-off cinemagraph loop.

1. Register each video frame to the original still (affine ECC) and warp it back,
   removing the model's slow zoom/drift.
2. Upscale to the still's size and blend: the sharp still where nothing moves,
   the video where it does (water, mist, fireflies), via a soft motion mask.
3. Loop with a crossfade (no forward/backward ping-pong).
Usage: python3 cinemagraph.py STILL.png CLIP.mp4 OUTDIR
"""
import sys, os, cv2, numpy as np
still_p, clip_p, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
still = cv2.imread(still_p)
H, W = still.shape[:2]
cap = cv2.VideoCapture(clip_p); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
vh, vw = frames[0].shape[:2]
S = 0.5  # register at half of the clip's size for speed
ref = cv2.cvtColor(cv2.resize(still, (int(vw*S), int(vh*S)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-6)
warp = np.eye(2, 3, dtype=np.float32)
up = []
for i, f in enumerate(frames):
    g = cv2.cvtColor(cv2.resize(f, (int(vw*S), int(vh*S)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    try:
        _, warp = cv2.findTransformECC(ref, g, warp, cv2.MOTION_AFFINE, crit, None, 5)
    except cv2.error:
        pass
    # warp maps ref(still) coords -> frame coords; build it in full-still coordinates
    M = warp.copy().astype(np.float64)
    sx = (vw*S) / W  # still px -> registration px
    A = np.array([[sx, 0, 0], [0, sx * (W / vw) * (vh / H) if False else (vh*S)/H, 0], [0, 0, 1]])
    A[1,1] = (vh*S)/H
    B = np.array([[1/S * 1, 0, 0], [0, 1/S, 0], [0, 0, 1]])  # registration px -> frame px
    full = B @ np.vstack([M, [0, 0, 1]]) @ A  # still px -> frame px
    u = cv2.warpAffine(f, full[:2].astype(np.float32), (W, H), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    up.append(u)
    if i % 20 == 0: print('frame', i, np.round(warp, 4).tolist(), flush=True)
stack = np.stack([cv2.cvtColor(u, cv2.COLOR_BGR2GRAY).astype(np.float32) for u in up])
motion = stack.std(axis=0)
np.save(os.path.join(out, 'motion.npy'), motion)
lo, hi = np.percentile(motion, 55), np.percentile(motion, 92)
m = np.clip((motion - lo) / (hi - lo), 0, 1)
m = cv2.dilate(m, np.ones((9, 9), np.uint8))
m = cv2.GaussianBlur(m, (0, 0), 9)
m = np.clip(m * 1.2, 0, 1)[..., None]
cv2.imwrite(os.path.join(out, 'mask.png'), (m[..., 0] * 255).astype(np.uint8))
# match the video's overall color to the still so blended edges don't show
vm = np.mean(np.stack(up[::10]), axis=0)
gain = (still.astype(np.float32).mean(axis=(0, 1)) + 1) / (vm.mean(axis=(0, 1)) + 1)
sf = still.astype(np.float32)
N = len(up); X = 24  # crossfade frames
L = N - X
for k in range(L):
    a = up[k + X].astype(np.float32)
    if k >= L - X:  # fade into the loop's start
        t = (k - (L - X) + 1) / (X + 1)
        a = a * (1 - t) + up[k - (L - X)].astype(np.float32) * t
    a = a * gain
    o = sf * (1 - m) + a * m
    cv2.imwrite(os.path.join(out, f'o{k:04d}.png'), np.clip(o, 0, 255).astype(np.uint8))
print('wrote', L, 'frames')
