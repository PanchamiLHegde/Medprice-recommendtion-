import requests
import json
import mysql.connector

def fetch_and_store_data():
    try:
        # API URL
        #url = 'https://medicomp.in/scrape-data?medname=Sugarchek%20Advance%20Glucometer%20Test%20Strip&packSize=50%20Test%20Strips&pincode=560098'    
        # Fetch the data
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Process the response text
        lines = response.text.split('\n')
        cleaned_data = [
            line.replace('data: ', '').strip()
            for line in lines
            if line.strip().startswith('data:')
        ]
        json_data = [json.loads(line) for line in cleaned_data]  # Parse each line as JSON

        # Connect to MySQL database
        db = mysql.connector.connect(
            host="localhost",       # Replace with your database host
            user="root",            # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="medcomp_db",
            auth_plugin="mysql_native_password"  # Replace with your database name
        )
        cursor = db.cursor()

        # Create the table if it doesn't exist, and add the 'service' column for serviceable status
        create_table_query = """
        CREATE TABLE IF NOT EXISTS medicines (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            item VARCHAR(255),
            price FLOAT,
            deliveryCharge FLOAT,
            finalCharge FLOAT,
            deliveryTime INT,
            medicineAvailability BOOLEAN,
            pincode VARCHAR(10),
            service INT
        )
        """
        cursor.execute(create_table_query)

        # Insert data into the database
        for medicine in json_data:
            # Extracting relevant fields from the response
            name = medicine.get('name')  # Platform name (for reference, not used in ML)
            item = medicine.get('item')  # Medicine name (for reference, not used in ML)
            price = medicine.get('price', 0.0)
            delivery_charge = medicine.get('deliveryCharge', 0.0)
            final_charge = medicine.get('finalCharge', 0.0)
            delivery_time = medicine.get('deliveryTime', 'Unknown')
            availability = medicine.get('medicineAvailability', False)
            pincode = '560098'  # Manually setting pincode as per your requirement
            lson = medicine.get('lson', '')  # Get the lson field value
            
            # Determine the serviceable status (1 if "Pincode Serviceable", else 0)
            service = 1 if "Pincode Serviceable" in lson else 0
            
            # Convert delivery time into a numeric value if necessary (example: delivery time in hours)
            if delivery_time == 'Same day':
                delivery_time_num = 0
            elif delivery_time == 'Next day':
                delivery_time_num = 1
            elif '1 - 2 Days' in delivery_time:
                delivery_time_num = 2
            else:
                delivery_time_num = 3  # For any other unspecified delivery times

            # Insert query to store data for ML use
            insert_query = """
            INSERT INTO medicines (name, item, price, deliveryCharge, finalCharge, deliveryTime, medicineAvailability, pincode, service)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name, item, price, delivery_charge, final_charge, delivery_time_num, availability, pincode, service))

        # Commit the transaction
        db.commit()
        print(f"Inserted {cursor.rowcount} rows of data.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    finally:
        # Close the database connection
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db.is_connected():
            db.close()

# Call the function
fetch_and_store_data()
