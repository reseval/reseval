import * as express from 'express';
import db from '../../db';

const router = express.Router();

router.post('/', async (req, res) => {
    const newResponse = req.body;
    try {
        const result = await db.responses.insert(
            newResponse.Stem,
            newResponse.Participant,
            newResponse.OrderAsked,
            newResponse.Response);
        res.json(result);
    } catch (err) {
        console.log(err);
        let err_message = "";
        if (err instanceof Error) {
            err_message = err.message;
        }
        res.status(500).json({ err: err_message });
    }
})

export default router;
