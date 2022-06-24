import cors from 'cors';
import express from 'express';
import morgan from 'morgan';
import routes from './server/routes';
import * as path from 'path';

const app = express();

app.use(cors());

// Log incoming requests
app.use(morgan('dev'));

// Serve static files from the client's build directory
app.use(express.static('./client/build'));

// Parses request bodies as JSON
app.use(express.json());

// Add API routes
app.use(routes);

// Reroute bad requests to the index
app.get('*', (_, response) => {
	response.sendFile(path.join(__dirname, './client/build/index.html'));
});

// Default to port 3001
const port = process.env.PORT || 3001;

// Start the server
app.listen(port, () => console.log(`Server listening on port: ${port}`));
