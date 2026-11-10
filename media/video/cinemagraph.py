"""Turn the Artlist Garden clip into a crisp, locked-off cinemagraph loop.

1. Register each video frame to the original still (affine ECC) and warp it back,
   removing the model's slow zoom/drift.
2. Upscale to the still's size and blend: the sharp still where nothing moves,
   the video where it does (water, mist, fireflies), via a soft motion mask.
3. Loop with a crossfade (no forward/backward ping-pong).
Usage: python3 cinemagraph.py STILL.png CLIP.mp4 OUTDIR [LO_PCT HI_PCT]
"""
import sys, os, cv2, numpy as np
still_p, clip_p, out = sys.argv[1:4]
LO, HI = (float(x) for x in (sys.argv[4:6] if len(sys.argv) > 5 else (75, 97)))
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
cache = os.path.join(out, 'warps.npy')
warps = list(np.load(cache)) if os.path.exists(cache) else None
up = []
for i, f in enumerate(frames):
    if warps is not None:
        warp = warps[i]
    else:
        g = cv2.cvtColor(cv2.resize(f, (int(vw*S), int(vh*S)), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
        try:
            _, warp = cv2.findTransformECC(ref, g, warp, cv2.MOTION_AFFINE, crit, None, 5)
        except cv2.error:
            pass
        globals().setdefault('_w', []).append(warp.copy())
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
if warps is None: np.save(cache, np.stack(globals()['_w']))
# Motion = frame-to-frame change on blurred frames, so 1px edge wobble doesn't count, only real flow.
bl = [cv2.GaussianBlur(cv2.cvtColor(u, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 3) for u in up]
motion = np.mean([np.abs(bl[i+1] - bl[i]) for i in range(len(bl) - 1)], axis=0)
np.save(os.path.join(out, 'motion.npy'), motion)
lo, hi = np.percentile(motion, LO), np.percentile(motion, HI)
m = np.clip((motion - lo) / (hi - lo), 0, 1)
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
m = cv2.dilate(m, np.ones((7, 7), np.uint8))
m = cv2.GaussianBlur(m, (0, 0), 7)[..., None]
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
    a = a + 0.6 * (a - cv2.GaussianBlur(a, (0, 0), 1.6))  # unsharp: closer to the still's crispness
    o = sf * (1 - m) + a * m
    cv2.imwrite(os.path.join(out, f'o{k:04d}.png'), np.clip(o, 0, 255).astype(np.uint8))
print('wrote', L, 'frames')
