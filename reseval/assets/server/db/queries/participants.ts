import { Query } from '..';

const all = () => Query('SELECT * FROM participants');

function insert(participant: any) {
    /* Insert into the participant table */
    const keys = Object.keys(participant);
    const values = Object.values(participant);
    const query =
        `INSERT INTO participants (${keys.join(', ')})` +
        ` VALUES (${'?, '.repeat(keys.length - 1) + '?'})`;
    return Query(query, values);
}

function update(participant: any) {
    /* Insert into the participant table */
    // Get participant ID
    const ID = participant.ID;
    delete participant.ID;

    // Get update command
    const keys = Object.keys(participant);
    const set = keys.map((key: any, index: Number) =>
        key +
        ' = "' +
        participant[key] +
        (index == keys.length - 1 ? '"' : '", ')
    );

    // Don't update if there are no contents
    if (set.length === 0) return null;

    // Create MySQL query
    const query = `UPDATE participants SET ${set} WHERE ID="${ID}"`
    return Query(query);
}

export default { all, insert, update };
