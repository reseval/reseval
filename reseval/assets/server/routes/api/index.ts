import * as express from 'express';
import conditionsRouter from './conditions';
import filesRouter from './files';
import participantsRouter from './participants';
import responsesRouter from './responses';

const router = express.Router();

router.use('/conditions', conditionsRouter);
router.use('/files', filesRouter);
router.use('/participants', participantsRouter);
router.use('/responses', responsesRouter);

export default router;
