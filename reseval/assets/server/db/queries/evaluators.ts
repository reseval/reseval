import { Query } from '..';

function insert(Participant: string) {
    return Query(
        'INSERT INTO `evaluators` (`ID`, `Participant`) ' +
        'VALUES (NULL, "' + Participant + '")');
}

function one(Participant: string) {
    return Query(
        'SELECT `ID` FROM evaluators WHERE `Participant` = "' + Participant + '"')
}

export default { insert, one }
