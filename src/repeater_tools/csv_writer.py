# src/repeater_tools/csv_writer.py
import csv
from typing import List
from models.repeater import Repeater


class CSVWriter:
    """
    Write out a list of Repeater objects in CHIRP's generic CSV-import format.
    """

    def __init__(self, filename: str):
        self.filename = filename

    def write_chirp_csv(self, repeaters: List[Repeater]) -> None:
        """
        Write `repeaters` to self.filename as a CHIRP‐compatible CSV.
        """
        # CHIRP generic import columns
        header = [
            "Location",    # typically the callsign
            "Name",        # your description field
            "Frequency",   # output freq in MHz
            "Duplex",      # "+", "-", or "OFF"
            "Offset",      # offset in MHz
            "Tone",        # "Tone" or "DCS" or blank
            "rToneFreq",   # CTCSS (Rx) in Hz
            "cToneFreq",   # DCS (Tx) code
            "Mode",        # "FM"
            "TStep",       # channel step, e.g. 0.005
            "Skip",        # "OFF"
            "Comment",     # free‐form
        ]

        with open(self.filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            for rpt in repeaters:
                # Duplex/offset logic
                if rpt.offset is None or rpt.offset == 0:
                    duplex = "OFF"
                    offset = ""
                else:
                    duplex = "+" if rpt.offset_dir == "plus" else "-"
                    offset = f"{rpt.offset:.6f}"

                # Tone logic
                if rpt.tone_mode == "CTCSS" and rpt.tone is not None:
                    tone = "Tone"
                    rToneFreq = f"{rpt.tone:.1f}"
                    cToneFreq = ""
                elif rpt.tone_mode == "DCS" and rpt.tone is not None:
                    tone = "DCS"
                    rToneFreq = ""
                    # CHIRP expects integer DCS code
                    cToneFreq = str(int(rpt.tone))
                else:
                    tone = ""
                    rToneFreq = ""
                    cToneFreq = ""

                # static defaults
                mode  = "FM"
                tstep = "0.005"
                skip  = "OFF"
                comment = f"{rpt.callsign or ''} {rpt.city or ''}, {rpt.state or ''}".strip()

                writer.writerow([
                    rpt.callsign or "",
                    rpt.notes or "",
                    f"{rpt.frequency:.6f}",
                    duplex,
                    offset,
                    tone,
                    rToneFreq,
                    cToneFreq,
                    mode,
                    tstep,
                    skip,
                    comment,
                ])
