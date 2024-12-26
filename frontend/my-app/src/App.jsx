import React, { useState } from 'react';
import './App.css';

function App() {
  const [medicine, setMedicine] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setMedicine(e.target.value);
    handleFuseRes();
  };

  const handleFuseRes = async () => {
    const fuseResponse = await fetch(`http://localhost:5000/api/recommendations/suggestions/${medicine}`);
    if (fuseResponse.ok) {
      const fuseData = await fuseResponse.json();
      document.getElementsByClassName('fuseRes')[0].innerHTML = '';
      for (let i = 0; i < fuseData.length; i++) {
        document.getElementsByClassName('fuseRes')[0].innerHTML += `
        <option value="${fuseData[i].item}">
        `
      }
      // console.log(fuseData);
    } else {
      // console.log("FUSE error");
    }
  };

  const handleSearch = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/recommendations/${medicine}`);
      // console.log(medicine);
      if (response.ok) {
        const data = await response.json();
        // console.log(data);
        setRecommendation(data);
        setError('');
      } else {
        setError('Medicine not found');
        setRecommendation(null);
      }
    } catch (error) {
      setError('Error fetching data');
      setRecommendation(null);
    }
  };

  const ParseFloat = (str,val) => {
    str = str.toString();
    str = str.slice(0, (str.indexOf(".")) + val + 1); 
    return Number(str);   
  }

  return (
    <div className="App">
      <div className="header">
        <h1>GetMed</h1>
        <p>Your trusted medicine recommendation platform</p>
      </div>
      <div className="search-section">
        <input
          type="text"
          list='fuseRes'
          placeholder="Enter medicine name"
          value={medicine}
          onChange={handleInputChange}
        />
        <datalist id='fuseRes' className='fuseRes'></datalist>
        <button onClick={handleSearch}>Search</button>
      </div>

      {error && <p className="error">{error}</p>}

      {recommendation && (
        <div className="result-section">
          <div className="filters">
            <h2>Filters</h2>
            <div>
              <label>Price</label>
              <input type="range" min="0" max="200" />
            </div>
            <div>
              <label>Delivery Price</label>
              <input type="range" min="0" max="150" />
            </div>
            <div>
              <h3>Availability</h3>
              <div>
                <input type="checkbox" id="all" />
                <label htmlFor="all">All</label>
              </div>
              <div>
                <input type="checkbox" id="in-stock" />
                <label htmlFor="in-stock">In Stock</label>
              </div>
              <div>
                <input type="checkbox" id="out-stock" />
                <label htmlFor="out-stock">Out of Stock</label>
              </div>
            </div>
          </div>

          <div className="details">
            <h2>Best Platform</h2>
            <h3>{recommendation.platform}</h3>
            <p>Medicine Price: ₹{ParseFloat(recommendation.price,2)}</p>
            <p>Delivery Price: ₹{recommendation.deliveryPrice}</p>
            <p>Availability: {recommendation.availability ? 'In Stock' : 'Out of Stock'}</p>
            <p>Delivery Time: {recommendation.deliveryTime} days</p>
            <h3>Total: ₹{ParseFloat(recommendation.price + recommendation.deliveryPrice,2)}</h3>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;