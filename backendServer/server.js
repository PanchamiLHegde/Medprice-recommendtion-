const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const Fuse = require('fuse.js');
const fuseOptions = {
  includeScore: true, // Include the matching score in results
  threshold: 0.4,     // Match threshold (lower is stricter, higher is more lenient)
  keys: []            // We're searching directly on the string array
};


const app = express();
const port = 5000;

// Middleware
app.use(cors());
app.use(express.json());
let allMedName=[];
let fuse;

// Create a MySQL connection pool
const db = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'Tonikroos@8', // Update with your MySQL password
  database: 'medcomp_db', // Ensure the database matches your setup
});

// Endpoint to get recommendations for a specific medicine
app.get('/api/recommendations/:medicine', (req, res) => {
  const medicine = req.params.medicine;

  const query = `
    SELECT 
      name, 
      price, 
      deliveryCharge, 
      medicineAvailability, 
      deliveryTime 
    FROM medicines 
    WHERE item = ?
  `;

  db.execute(query, [medicine], (err, results) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: 'Database error' });
    }

    if (results.length > 0) {
      const bestRecommendation = results[0]; // For simplicity, take the first match
      res.json({
        platform: bestRecommendation.name,
        price: bestRecommendation.price,
        deliveryPrice: bestRecommendation.deliveryCharge,
        availability: bestRecommendation.medicineAvailability,
        deliveryTime: bestRecommendation.deliveryTime,
      });
    } else {
      res.status(404).json({ error: 'Medicine not found' });
    }
  });
});

app.get('/api/recommendations/suggestions/:medicine', (req, res) => {
  const medicine = req.params.medicine;

  const fuseResults = fuse.search(medicine);
  console.log(fuse);
  console.log(fuseResults);
  if (fuseResults.length > 0) {
    console.log('Best Match:', fuseResults[0].item); // Closest match
    // console.log('All Matches:', fuseResults.map(result => result.item));
    res.json(fuseResults);
  }
});

db.execute("SELECT * FROM medicines", (err, results) => {
  if (err) {
    console.error('Database error:', err);
  }
  for(let i=0;i<results.length;i++)
    allMedName.push(results[i].item);
  // console.log(allMedName);
  fuse = new Fuse(allMedName, fuseOptions);
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});