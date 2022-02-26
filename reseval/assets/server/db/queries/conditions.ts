import { Query } from '..';

const all = () => Query(
    'SELECT `Condition` FROM conditions ORDER BY `Condition`');

export default { all }
