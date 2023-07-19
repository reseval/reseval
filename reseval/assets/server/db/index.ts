import * as mysql from 'mysql2';

// Load database credentials
require('dotenv').config();
const pool = mysql.createPool({
    host: process.env.RDS_HOSTNAME || process.env.MYSQL_HOST,
    user: process.env.RDS_USERNAME || process.env.MYSQL_USER,
    password: process.env.RDS_PASSWORD || process.env.MYSQL_PASS,
    database: process.env.RDS_DB_NAME || process.env.MYSQL_DBNAME
})

export const Query = (query: string, values?: any) => {
    return new Promise((resolve, reject) => {
        pool.query(query, values, (err, results) => {
            if (err) {
                reject(err);
            } else {
                resolve(results);
            }
        })
    })
}

import conditions from './queries/conditions';
import files from './queries/files';
import participants from './queries/participants';
import responses from './queries/responses';

export default { conditions, files, participants, responses, }
