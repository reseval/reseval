import * as express from 'express';
import db from '../../db';

const router = express.Router();

router.get('/:participant', async (request, response) => {
    const participant = request.params.participant;
    try {
        const evaluator_id = await db.evaluators.one(participant);
        response.json(evaluator_id);
    } catch (err: unknown) {
        console.log(err);
        let err_message = "";
        if (err instanceof Error) {
            err_message = err.message;
        }
        response.status(500).json({ err: err_message });
    }
});

router.post('/insert', async (request, response) => {
    const participant = request.body['Participant'];
    try {
        const result = await db.evaluators.insert(participant);
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
