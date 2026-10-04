
EDGE_GUESS = 0.5  # seconds given to a stretch that has a wall on one side only

# two pointers like 
def fill_missing_times(words):
    n = len(words)
    i = 0
    while i < n:
        if words[i]["start"] is not None:
            i += 1
            continue

        # words[i] is missing. Move j forward to the first word that has a time.
        j = i
        while j < n and words[j]["start"] is None:
            j += 1

        # The stretch is words[i] ... words[j-1], so it has (j - i) words.
        # words[i-1] is the timed word before it, if i > 0.
        # words[j]   is the timed word after it,  if j < n.

        has_before = i > 0   # is there a timed word before the stretch?
        has_after = j < n    # is there a timed word after it?

        if not has_before and not has_after:
            raise ValueError("cannot fill word times: no word in the transcript has a timestamp")

        if has_before and has_after:      
            left = words[i - 1]["end"]
            right = words[j]["start"]
        elif has_after:                   
            right = words[j]["start"]
            left = max(0, right - EDGE_GUESS)
        else:                           
            left = words[i - 1]["end"]
            right = left + EDGE_GUESS

        share = (right - left) / (j - i)
        for k in range(i, j):
            words[k]["start"] = left + (k - i) * share
            words[k]["end"] = left + (k - i + 1) * share


        i = j
    return words