#!/usr/bin/env python3
import cv2
import numpy as np
import argparse


def bucket_alpha(alpha: np.ndarray, bucket: int) -> np.ndarray:
    h, w = alpha.shape
    H, W = h // bucket, w // bucket
    cropped = alpha[:H * bucket, :W * bucket].astype(np.float32) / 255.0
    block = cropped.reshape(H, bucket, W, bucket)
    avg = block.mean(axis=(1, 3))
    return avg


def assign_levels(alpha_avg: np.ndarray, thresholds: list[float]) -> np.ndarray:
    levels = np.zeros_like(alpha_avg, dtype=np.uint8)
    for i, t in enumerate(thresholds):
        levels[alpha_avg >= t] = i + 1
    return levels


def render_multilevel(levels: np.ndarray, cell_size: int, colors: list[tuple[int, int, int]]) -> np.ndarray:
    H, W = levels.shape
    out = np.full((H * cell_size, W * cell_size, 3), 255, np.uint8)
    for y in range(H):
        for x in range(W):
            level = levels[y, x]
            if level > 0:
                out[y*cell_size:(y+1)*cell_size,
                    x*cell_size:(x+1)*cell_size] = colors[level - 1]

    for y in range(0, H * cell_size, cell_size):
        cv2.line(out, (0, y), (W * cell_size, y), (180, 180, 180), 1)
    for x in range(0, W * cell_size, cell_size):
        cv2.line(out, (x, 0), (x, H * cell_size), (180, 180, 180), 1)
    return out


def main():
    parser = argparse.ArgumentParser(description="convert transparent PNG to occupancy grid.")
    parser.add_argument("input", help="input transparent PNG")
    parser.add_argument("--bucket", type=int, default=8, help="grid cell size (default 8)")
    parser.add_argument("--cell-size", type=int, default=8, help="rendered cell size (default 8)")
    parser.add_argument("--thresholds", nargs="+", type=float, default=[0.1, 0.3, 0.6, 0.9],
                        help="alpha thresholds for occupancy levels (0–1).")
    parser.add_argument("--out-png", default="occupancy_fixed.png")
    parser.add_argument("--out-csv", default="occupancy_fixed.csv")
    args = parser.parse_args()

    img = cv2.imread(args.input, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(args.input)
    if img.shape[2] < 4:
        raise ValueError("Image must have an alpha channel.")

    alpha = img[:, :, 3]

    alpha_avg = bucket_alpha(alpha, args.bucket)
    
    occ_levels = assign_levels(alpha_avg, args.thresholds)

    n_levels = len(args.thresholds)
    colors = [tuple([int(255 * (1 - (i + 1) / (n_levels + 1)))] * 3) for i in range(n_levels)]

    vis = render_multilevel(occ_levels, args.cell_size, colors)

    np.savetxt(args.out_csv, occ_levels, fmt="%d", delimiter=",")
    cv2.imwrite(args.out_png, vis)
    print(f"saved {args.out_png}, {args.out_csv}")
    print(f"alpha mean: {alpha.mean():.2f}, thresholds: {args.thresholds}")


if __name__ == "__main__":
    main()
