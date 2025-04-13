import express from 'express';
import cors from 'cors';
import { loggerMiddleware } from './middleware/loggerMiddleware';

const app = express();

app.use(cors());
app.use(express.json());
app.use(loggerMiddleware); 