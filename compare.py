import numpy as np


def compare_array_differences(original, written, label):
    """Compare the xyz, lengths, and angles arrays within the tuples and report differences."""
    
    diff_arrays = []
    max_diff = []

    for i in range(len(original)):
        # Subtract the written array from the original array
        diff = original[i] - written[i]
        
        # Store the difference array
        diff_arrays.append(diff)
        
        # Compute the maximum absolute difference and store it
        max_diff_value = np.max(np.abs(diff))
        max_diff.append(max_diff_value)

        print(f"{label} - Max difference for tuple {i+1}: {max_diff_value}")

    return diff_arrays, max_diff