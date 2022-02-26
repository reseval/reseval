import * as express from 'express';
import db from '../../db';

const router = express.Router();

router.get('/', async (_, res) => {
    try {
        const conditions = await db.conditions.all();
        res.json(conditions);
    } catch (err: unknown) {
        console.log(err);
        let err_message = "";
        if (err instanceof Error) {
            err_message = err.message;
        }
        res.status(500).json({ err: err_message });
    }
});

export default router;
