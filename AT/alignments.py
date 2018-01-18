
"""
Computing global and loacl DNA alignments
"""

def build_scoring_matrix(alphabet, diag_score,
                         off_diag_score, dash_score):
    """
    Builds a scoring matrix in a form of dictionay of dictionaries
    returns the matrix
    """
    def get_score(inside_letter, outside_letter):
        """
        Get the correct score for pair
        """
        if outside_letter == "-" or inside_letter == "-":
            return dash_score
        elif outside_letter == inside_letter:
            return diag_score
        else:
            return off_diag_score
    extended_alphabet = alphabet.copy()
    extended_alphabet.add("-")
    outside_dict = {}
    for outside_letter in extended_alphabet:
        inside_dict = {inside_letter: get_score(inside_letter,
                                                outside_letter)
                       for inside_letter in extended_alphabet}
        outside_dict[outside_letter] = inside_dict
    return outside_dict

#test_ =  build_scoring_matrix(set(['A', 'C', 'T', 'G']), 6, 2, -4)
#print(test_)

def compute_alignment_matrix(seq_x, seq_y, scoring_matrix, global_flag):
    """
    Takes two sequences and scoring matrix for the same sybols
    Returns scored matrix
    """
    len_x = len(seq_x)
    len_y = len(seq_y)
    a_matrix = [] 
    for _ in range(len_x + 1):
        a_matrix.append([0 for _ in range(len_y + 1)])
    a_matrix[0][0] = 0
    for x_ind in range(1, len_x + 1):
        val = a_matrix[x_ind - 1][0] + scoring_matrix["-"][seq_x[x_ind - 1]]
        if global_flag or val > 0:
            a_matrix[x_ind][0] = val
    for y_ind in range(1, len_y + 1):
        val = a_matrix[0][y_ind - 1] + scoring_matrix["-"][seq_y[y_ind - 1]]
        if global_flag or val > 0:
            a_matrix[0][y_ind] = val
    for x_ind in range(1, len_x + 1):
        for y_ind in range(1, len_y + 1):
            val1 = a_matrix[x_ind - 1][y_ind - 1] + scoring_matrix[seq_y[y_ind - 1]][seq_x[x_ind - 1]]
            val2 = a_matrix[x_ind - 1][y_ind] + scoring_matrix[seq_x[x_ind - 1]]["-"]
            val3 = val = a_matrix[x_ind][y_ind - 1] + scoring_matrix["-"][seq_y[y_ind - 1]]
            val = max(val1, val2, val3)
            if global_flag or val > 0:
                a_matrix[x_ind][y_ind] = val
    return a_matrix

#test2_ = compute_alignment_matrix('AA', 'TAAT', test_, False)
#
#for x in test2:
#    print(x)
