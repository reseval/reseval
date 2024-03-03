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

    # Split responses using blacklist
    filtered, residual = [], []
    for response in responses:
        (
            residual if response['Participant'] in blacklist else filtered
        ).append(response)

    # Print the impact of the filter
    participants = set(response['Participant'] for response in responses)
    print(
        f'Filtered out {len(blacklist)} of the {len(participants)} '
        'participants that ranked the low-anchor above the high-anchor')

    return filtered, residual


def count(responses, num):
    """Filter out participants that have an incorrect number of responses"""
    # Count responses
    participants = {}
    for response in responses:
        participant = response['Participant']
        if participant not in participants:
            participants[participant] = 1
        else:
            participants[participant] += 1

    # Filter out bad participants
    blacklist = [
        participant for participant, count in participants.items()
        if count != num]
    filtered = []
    for response in responses:
        if response['Participant'] not in blacklist:
            filtered.append(response)

    # Print the impact of the filter
    print(f'Filtered out {len(blacklist)} participants: {blacklist}')

    return filtered
