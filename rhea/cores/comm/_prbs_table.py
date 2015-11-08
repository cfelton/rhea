

# common maximum length PRBS feedback taps, feedback taps
# retrieved from:
# http://www.newwaveinstruments.com/resources/articles/m_sequence_linear_feedback_shift_register_lfsr.htm
prbs_feedback_taps = {
    7:  [(7, 6), (7, 4), (7, 6, 5, 4), (7, 6, 5, 2), ],
    9:  [(9, 5), (9, 8, 7, 2), (9, 8, 6, 5), ],
    11: [(11, 9), (11, 10, 9, 7), (11, 10, 9, 5), (11, 10, 9, 2), ],
    15: [(15, 14), (15, 11), (15, 8), (15, 14, 13, 11), (15, 14, 13, 8), ],
    23: [(23, 18), (23, 14), (23, 22, 21, 16), (23, 22, 21, 8), ],
    31: [(31, 28), (31, 25), (31, 24), (31, 18), ]
}