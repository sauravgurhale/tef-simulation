def _seg(n):
    return f'segment_{n:02d}.mp3'


AUDIO_MAP = {
    # Group 1: intro seg_01, Q1-Q4 → seg_02-05
    1:  {'intro': _seg(1),  'main': _seg(2),  'intro_label': 'Groupe 1 (Q1–Q4)',  'shared_with': None},
    2:  {'intro': _seg(1),  'main': _seg(3),  'intro_label': 'Groupe 1 (Q1–Q4)',  'shared_with': None},
    3:  {'intro': _seg(1),  'main': _seg(4),  'intro_label': 'Groupe 1 (Q1–Q4)',  'shared_with': None},
    4:  {'intro': _seg(1),  'main': _seg(5),  'intro_label': 'Groupe 1 (Q1–Q4)',  'shared_with': None},

    # Group 2: intro seg_06, Q5-Q8 → seg_07-10
    5:  {'intro': _seg(6),  'main': _seg(7),  'intro_label': 'Groupe 2 (Q5–Q8)',  'shared_with': None},
    6:  {'intro': _seg(6),  'main': _seg(8),  'intro_label': 'Groupe 2 (Q5–Q8)',  'shared_with': None},
    7:  {'intro': _seg(6),  'main': _seg(9),  'intro_label': 'Groupe 2 (Q5–Q8)',  'shared_with': None},
    8:  {'intro': _seg(6),  'main': _seg(10), 'intro_label': 'Groupe 2 (Q5–Q8)',  'shared_with': None},

    # Group 3: intro seg_11, Q9-Q14 → seg_12-17
    9:  {'intro': _seg(11), 'main': _seg(12), 'intro_label': 'Groupe 3 (Q9–Q14)', 'shared_with': None},
    10: {'intro': _seg(11), 'main': _seg(13), 'intro_label': 'Groupe 3 (Q9–Q14)', 'shared_with': None},
    11: {'intro': _seg(11), 'main': _seg(14), 'intro_label': 'Groupe 3 (Q9–Q14)', 'shared_with': None},
    12: {'intro': _seg(11), 'main': _seg(15), 'intro_label': 'Groupe 3 (Q9–Q14)', 'shared_with': None},
    13: {'intro': _seg(11), 'main': _seg(16), 'intro_label': 'Groupe 3 (Q9–Q14)', 'shared_with': None},
    14: {'intro': _seg(11), 'main': _seg(17), 'intro_label': 'Groupe 3 (Q9–Q14)', 'shared_with': None},

    # Group 4: intro seg_18, Q15-Q17 → seg_19-21
    15: {'intro': _seg(18), 'main': _seg(19), 'intro_label': 'Groupe 4 (Q15–Q17)', 'shared_with': None},
    16: {'intro': _seg(18), 'main': _seg(20), 'intro_label': 'Groupe 4 (Q15–Q17)', 'shared_with': None},
    17: {'intro': _seg(18), 'main': _seg(21), 'intro_label': 'Groupe 4 (Q15–Q17)', 'shared_with': None},

    # Group 5: intro seg_22, Q18-Q20 → seg_23-25
    18: {'intro': _seg(22), 'main': _seg(23), 'intro_label': 'Groupe 5 (Q18–Q20)', 'shared_with': None},
    19: {'intro': _seg(22), 'main': _seg(24), 'intro_label': 'Groupe 5 (Q18–Q20)', 'shared_with': None},
    20: {'intro': _seg(22), 'main': _seg(25), 'intro_label': 'Groupe 5 (Q18–Q20)', 'shared_with': None},

    # Group 6: intro seg_26, Q21-Q22 → seg_27-28
    21: {'intro': _seg(26), 'main': _seg(27), 'intro_label': 'Groupe 6 (Q21–Q22)', 'shared_with': None},
    22: {'intro': _seg(26), 'main': _seg(28), 'intro_label': 'Groupe 6 (Q21–Q22)', 'shared_with': None},

    # Group 7: intro seg_29, Q23-Q30 (pairs share segments)
    23: {'intro': _seg(29), 'main': _seg(30), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [24]},
    24: {'intro': _seg(29), 'main': _seg(30), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [23]},
    25: {'intro': _seg(29), 'main': _seg(31), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [26]},
    26: {'intro': _seg(29), 'main': _seg(31), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [25]},
    27: {'intro': _seg(29), 'main': _seg(32), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [28]},
    28: {'intro': _seg(29), 'main': _seg(32), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [27]},
    29: {'intro': _seg(29), 'main': _seg(33), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [30]},
    30: {'intro': _seg(29), 'main': _seg(33), 'intro_label': 'Groupe 7 (Q23–Q30)', 'shared_with': [29]},

    # Group 8: intro seg_34, Q31-Q40 → seg_35-44
    31: {'intro': _seg(34), 'main': _seg(35), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    32: {'intro': _seg(34), 'main': _seg(36), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    33: {'intro': _seg(34), 'main': _seg(37), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    34: {'intro': _seg(34), 'main': _seg(38), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    35: {'intro': _seg(34), 'main': _seg(39), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    36: {'intro': _seg(34), 'main': _seg(40), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    37: {'intro': _seg(34), 'main': _seg(41), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    38: {'intro': _seg(34), 'main': _seg(42), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    39: {'intro': _seg(34), 'main': _seg(43), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
    40: {'intro': _seg(34), 'main': _seg(44), 'intro_label': 'Groupe 8 (Q31–Q40)', 'shared_with': None},
}
