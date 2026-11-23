# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/upayy9234-art/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/upayy9234-art/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One program, one image: the front page of Sunday, 22 November 2026, drawn entirely in pure Python stdlib. `main.py` hand-builds a 1024x1024 PNG — its own PNG encoder (signature, IHDR, IDAT, IEND, CRC32 on every chunk) and its own 5x7 bitmap type — and writes it to `entry.png`. No network, no randomness, no clock: two runs produce byte-identical output, and the program re-reads its own output and verifies every chunk CRC, the 1024x1024 dimensions and the 1 MiB size limit before exiting 0.

## The page

- **Hero — Antalya:** COP31, the UN climate summit in Antalya, Turkiye, collapses with **no deal** after overtime talks fail to land a fossil-fuel phase-out text.
- **Benghazi:** Ukrainian sea drones sink a Russian warship off Benghazi, confirmed by President Zelenskyy.
- **The Hague:** The ICJ rules Myanmar committed genocide against the Rohingya.
- **Sinaloa:** "El Chapo Isidro" is captured in Sinaloa, Mexico.
- **Hormuz:** Iran attacks three tankers in the Strait of Hormuz.
- **West Bank:** Settlers burn homes and cars in Palestinian villages.
- **Tennis:** Carlos Alcaraz wins the ATP Finals.
- **Ticker:** Nigeria unrest; Nvidia slides again.

## Run it

```sh
python3 main.py
```

That writes `entry.png` (or pass an output path as the first argument, or set `MAKEFUN_OUTPUT_DIR`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=ermzz861&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
