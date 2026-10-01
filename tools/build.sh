#!/bin/bash
# The build order. Getting it wrong is how the drive shell lost its interface port: a chain
# rebuild re-ran 399 (which rebuilds P22 from scratch) without re-running 502 (which ports it
# for the boss), and 5.9 cm3 of interference sat there until the fast sweep found it.
#
#   geometry -> interfaces -> engraving -> verification
#
# Each stage depends on every stage above it and destroys the work of the stages below.
set -e
cd "$(dirname "$0")/.."
echo "=== geometry"
for s in 393_driveend 394_lighten_merge 396_fixes 397_recladding 398_sidemounts \
         399_drivecap 409_cuffs; do
  printf '  %-24s ' "$s"
  python tools/fcsend.py scripts/$s.py 2>&1 | grep -cE "DONE" | tr -d '\n'; echo
done
echo "=== interfaces (MUST follow 399: it rebuilds P22 unported)"
python tools/fcsend.py scripts/502_interface_build.py 2>&1 | grep -E "P3[01]|ported|clash|DONE"
echo "=== engraving (MUST follow 502: P30/P31 are engraved too)"
for i in $(seq 0 14); do
  python - "$i" <<'PY'
import io, sys
i = int(sys.argv[1])
s = io.open("scripts/412_engrave.py", encoding="utf-8").read()
io.open("scripts/_412_tmp.py", "w", encoding="utf-8", newline="").write(
    s.replace("__I0__", str(i)).replace("__I1__", str(i + 1)))
PY
  python tools/fcsend.py scripts/_412_tmp.py 2>&1 | grep -E "^  P[0-9]" || true
done
rm -f scripts/_412_tmp.py
echo "=== verification"
python tools/fcsend.py scripts/413_mark_visibility.py 2>&1 | tail -3
python tools/fcsend.py scripts/219_stl.py 2>&1 | grep -E "total ~"
python scripts/411_printability.py 2>&1 | sed -n '/^PROBLEMS/,+5p'
python tools/sweep.py
