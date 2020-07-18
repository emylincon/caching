import numpy as np
import pandas as pd
import pyfpgrowth

transactions = [[1, 2, 5],
                [2, 4],
                [2, 3],
                [1, 2, 4],
                [1, 3],
                [2, 3],
                [1, 3],
                [1, 2, 3, 5],
                [1, 2, 3]]

# Definition : find_frequent_patterns(transactions, support_threshold)
patterns = pyfpgrowth.find_frequent_patterns(transactions, 2)
print('p', patterns)
# —_—_—
# Definition : generate_association_rules(patterns, confidence_threshold)
''':arg
Given a set of frequent itemsets, return a dict of association rules in the form {(left):
((right), confidence)}

'''
rules = pyfpgrowth.generate_association_rules(patterns, 0.7)

print(rules)
