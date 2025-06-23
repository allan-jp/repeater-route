# repeater.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Repeater:
    callsign:     Optional[str]
    notes:        Optional[str]    # the repeater’s human‐readable notes?
    frequency:    float            # output freq (MHz)
    offset:       Optional[float]  # MHz offset magnitude
    offset_dir:   Optional[str]    # 'plus' or 'minus'
    tone_mode:    Optional[str]    # 'CTCSS' or 'DCS'
    tone:         Optional[float]  # PL or DCS code
    latitude:     float
    longitude:    float
    city:         Optional[str]
    county:       Optional[str]
    state:        Optional[str]
    fm_analog:    Optional[str]

    @staticmethod
    def from_row(row) -> "Repeater":
        # basic freqs
        freq = row["frequency"]
        inp  = row["input_freq"]

        # compute offset & direction
        offset = None
        offset_dir = None
        if freq is not None and inp is not None:
            delta = inp - freq
            offset = abs(delta)
            offset_dir = "plus" if delta > 0 else "minus"

        # pick tone mode & code
        pl  = row["pl"]
        tsq = row["tsq"]
        fm_analog = row["fm_analog"]

        if pl is not None:
            tone_mode = "CTCSS"; tone = pl
        elif tsq is not None:
            tone_mode = "DCS";   tone = tsq
        else:
            tone_mode = None;    tone = None

        return Repeater(
            callsign     = row["callsign"],
            notes        = row["notes"],
            frequency    = freq,
            offset       = offset,
            offset_dir   = offset_dir,
            tone_mode    = tone_mode,
            tone         = tone,
            latitude     = row["latitude"],
            longitude    = row["longitude"],
            city         = row["nearest_city"],
            county       = row["county"],
            state        = row["state"],
            fm_analog    = fm_analog
        )

