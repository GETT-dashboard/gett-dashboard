
## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

Make sure you have the database running in the backend and confiure the connection in db.js file

## Running project in a Docker
Run `docker build -t <image name>[:<tag name>] .` to build a Docker image with the project within.

Run `docker run -p 3000:3000 <image name>[:<tag name>]` to start the docker.

## Folder Descriptions

### /app
- **/_components:** This folder contains all of the reusable components used throughout the project
- **/api/login:** This folder contains the authentication mechanism for the application
- **/dashboard:** This is main page where the dashboard is rendered. It contains all the logic for filter selections and associated operations
- **/lib:** Houses all of the queries that are used for fetching data from the backend aswell as establishing the actual connecting with the database

### /public: Contains static assests like images used in the dashboard

### /util

- **description.js:** Contains the logic for generating the description for each visualisation
- **formatqurry.js:** Contains a utility function that can be used for debugging the prepared statemtents sql queries
- **highlevelpositions.js:** Contains list of pre-determined high level positions
- **translate-labels.js:** Used for translating labels to german


## Before running:
Change values in /lib/db.js to match your SQL database