import cv2
import time
import argparse

def parse_source(s):
    return int(s) if s.isdigit() else s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0", help="0 for webcam, or path to video file")
    ap.add_argument("--pct_thresh", type=float, default=0.02, help="fraction of pixels changed to trigger")
    ap.add_argument("--min_area", type=int, default=1500, help="min blob area to count")
    ap.add_argument("--persist", type=int, default=5, help="frames change must persist")
    ap.add_argument("--roi", default="", help="ROI x,y,w,h (optional)")
    args = ap.parse_args()

    cap = cv2.VideoCapture(parse_source(args.source))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open source: {args.source}. Try --source 1")

    bg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=True)

    roi = None
    if args.roi:
        roi = tuple(int(v) for v in args.roi.split(","))  # x,y,w,h

    consecutive = 0
    prev_changed = False

    # FPS
    frames = 0
    t0 = time.time()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.resize(frame, (640, 360))  # speed

        x0, y0 = 0, 0
        view = frame
        if roi:
            x0, y0, w, h = roi
            view = frame[y0:y0+h, x0:x0+w]

        gray = cv2.cvtColor(view, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        fg = bg.apply(gray)
        fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)[1]
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, None, iterations=2)
        fg = cv2.dilate(fg, None, iterations=2)

        changed_px = cv2.countNonZero(fg)
        total_px = fg.shape[0] * fg.shape[1]
        score = changed_px / float(total_px) if total_px else 0.0

        contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        big = [c for c in contours if cv2.contourArea(c) >= args.min_area]

        triggered = (score >= args.pct_thresh) or (len(big) > 0)
        consecutive = consecutive + 1 if triggered else 0
        changed = consecutive >= args.persist

        # Event output
        if changed and not prev_changed:
            print(f"CHANGE_START score={score:.3f}")
        elif (not changed) and prev_changed:
            print("CHANGE_END")
        prev_changed = changed

        # Draw
        out = frame.copy()
        if roi:
            cv2.rectangle(out, (x0, y0), (x0 + fg.shape[1], y0 + fg.shape[0]), (255, 255, 255), 2)
        for c in big:
            rx, ry, rw, rh = cv2.boundingRect(c)
            cv2.rectangle(out, (x0 + rx, y0 + ry), (x0 + rx + rw, y0 + ry + rh), (255, 255, 255), 2)

        frames += 1
        dt = time.time() - t0
        if dt >= 1.0:
            fps = frames / dt
            frames = 0
            t0 = time.time()

        cv2.putText(out, f"FPS={fps:.1f} score={score:.3f} changed={changed}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("output", out)
        cv2.imshow("mask", fg)

        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
