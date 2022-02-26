import * as mysql from 'mysql2';

// Load database credentials
require('dotenv').config();
const pool = mysql.createPool({
    host: process.env.MYSQL_HOST,
    user: process.env.MYSQL_USER,
    password: process.env.MYSQL_PASS,
    database: process.env.MYSQL_DBNAME
})

export const Query = (query: string, values?: any) => {
    return new Promise((resolve, reject) => {
        pool.query(query, values, (err, results) => {
            if (err) {
                console.log("process.env.MYSQL_HOST:", process.env.MYSQL_HOST);
                reject(err);
            } else {
                resolve(results);
            }
        })
    })
}

import conditions from './queries/conditions';
import evaluators from './queries/evaluators';
import files from './queries/files';
import participants from './queries/participants';
import responses from './queries/responses';

export default { conditions, evaluators, files, participants, responses, }
