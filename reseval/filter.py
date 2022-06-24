def anchors(responses, conditions, low_anchor, high_anchor):
    """Removes participants that rate the low anchor above the high anchor"""
    low_index = conditions.index(low_anchor)
    high_index = conditions.index(high_anchor)

    # Make blacklist of bad participants
    blacklist = set()
    for response in responses:
        scores = response['Response']
        scores = [scores[i:i + 3] for i in range(0, len(scores), 3)]
        if scores[low_index] > scores[high_index]:
            blacklist.add(response['Participant'])

    # Filter out bad participants
    filtered = []
    for response in responses:
        if response['Participant'] not in blacklist:
            filtered.append(response)

    return filtered
