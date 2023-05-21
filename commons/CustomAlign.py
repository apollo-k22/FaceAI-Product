from enum import Enum


class CustomAlign(Enum):
    AlignLeft = 0x0001  # Aligns with the left edge.
    AlignRight = 0x0002  # Aligns with the right edge.
    AlignHCenter = 0x0004  # Centers horizontally in the available space.
    AlignJustify = 0x0008  # Justifies the text in the available space.
    AlignTop = 0x0020  # Aligns with the top.
    AlignBottom = 0x0040  # Aligns with the bottom.
    AlignVCenter = 0x0080  # Centers vertically in the available space.
    AlignBaseline = 0x0100  # Aligns with the baseline.

    @staticmethod
    def align_left():
        return 0x0001

    @staticmethod
    def align_hcenter():
        return 0x0004
