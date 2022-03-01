import * as express from 'express';

const router = express.Router();

// TODO - If we resume or extend training, can we have this start at the correct ID?
//        Would need to write current index to database and retrieve it on startup.
let ID = 0;

router.get('/', async (request, response) => {
    response.json(ID);
    ID += 1;
});

export default router;
