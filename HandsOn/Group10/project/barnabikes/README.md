# Barnabikes

Web project to visualize bike stations and bars in Barcelona on an interactive map. 

# Barnabikes (in cloud)
You can see the code running in the cloud at:
https://frontend-29lp.onrender.com

And the code is available at:
https://github.com/sergioes55/projetoOpenData

## Structure
- `frontend/` — React application (Vite)
- `backend/` — Node.js/Express API (connected to GraphDB)

## Installation

### 1. Install dependencies
```bash
cd frontend
npm install
cd ../backend
npm install
```

### 2. Run the backend
```bash
npm start
```

### 3. Run the frontend
In other terminal:
```bash
cd frontend
npm run dev
```

The frontend will be available at:
http://localhost:5173

The backend will be available at:
http://localhost:4000

## Customization
- Modify the endpoints and SPARQL queries in `backend/server.js` according to your ontology/data.
- UI design and components are located in `frontend/src/`.

