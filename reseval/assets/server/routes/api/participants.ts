import * as express from 'express';
import db from '../../db';

const router = express.Router();

router.post('/insert', async (request, response) => {
    const participant = request.body;
    try {
        const result = await db.participants.insert(participant);
        response.json(result);
    } catch (err) {
        console.log(err);
        let err_message = "";
        if (err instanceof Error) {
            err_message = err.message;
        }
        response.status(500).json({ err: err_message });
    }
});

router.post('/update', async (request, response) => {
    const participant = request.body;
    try {
        const result = await db.participants.update(participant);
        response.json(result);
    } catch (err) {
        console.log(err);
        let err_message = "";
        if (err instanceof Error) {
            err_message = err.message;
        }
        response.status(500).json({ err: err_message });
    }
});

export default router;
