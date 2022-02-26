import { Query } from '..';

const insert = (
    Stem: string,
    Participant: string,
    OrderAsked: number,
    Response: string) => Query(
        'INSERT INTO responses (Stem, Participant, OrderAsked, Response) ' +
        'VALUES (?, ?, ?, ?)', [Stem, Participant, OrderAsked, Response]);

export default { insert }
