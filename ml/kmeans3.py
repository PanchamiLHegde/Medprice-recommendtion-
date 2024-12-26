import mysql.connector
import pandas as pd
from sklearn.cluster import KMeans

# Connect to the database
db = mysql.connector.connect(
    host="localhost",       # Replace with your database host
    user="root",            # Replace with your username
    password="",  # Replace with your password
    database="medcomp_db",#Replace with your database name
    auth_plugin="mysql_native_password"
)

# Fetch the data for clustering
query = """
SELECT id, price, deliveryCharge, finalCharge, deliveryTime, medicineAvailability
FROM medicines
WHERE id BETWEEN 1 AND 522
"""
df = pd.read_sql(query, db)

# Perform K-means clustering
features = ['price', 'deliveryCharge', 'finalCharge', 'deliveryTime', 'medicineAvailability']
kmeans = KMeans(n_clusters=5, random_state=42)  # Adjust `n_clusters` based on your needs
df['cluster'] = kmeans.fit_predict(df[features])

# Update the database with cluster assignments
cursor = db.cursor()
for _, row in df.iterrows():
    cursor.execute("""
        UPDATE medicines
        SET cluster = %s
        WHERE id = %s
    """, (int(row['cluster']), int(row['id'])))
db.commit()

# Fetch updated data with clusters
query_with_clusters = """
SELECT id, name, price, deliveryCharge, finalCharge, deliveryTime, medicineAvailability, service, cluster
FROM medicines
WHERE id BETWEEN 1 AND 522
"""
df_with_clusters = pd.read_sql(query_with_clusters, db)

# Analyze categories (reusing the earlier logic)
categories = {
    "Pain Relief": range(1, 44),
    "Cold and Cough": range(44, 122),
    "Diabetes": range(122, 232),
    "Thyroid": range(232, 264),
    "Blood Pressure": range(264, 281),
    "Gastrics": range(281, 317),
    "Heart Related": range(317, 418),
    "Daily Use Products": range(418, 523)
}

def analyze_category(data):
    cluster_means = data.groupby('cluster')[['price', 'deliveryCharge', 'finalCharge', 'deliveryTime', 'medicineAvailability']].mean()
    best_cluster = cluster_means['finalCharge'].idxmin()
    best_platforms = data[data['cluster'] == best_cluster]['name'].unique()
    return best_platforms, cluster_means.loc[best_cluster]

results = {}
for category, id_range in categories.items():
    category_data = df_with_clusters[df_with_clusters['id'].isin(id_range)]
    best_platforms, best_cluster_stats = analyze_category(category_data)
    results[category] = {
        "Best Platforms": best_platforms,
        "Cluster Stats": best_cluster_stats.to_dict()
    }

# Display results
for category, result in results.items():
    print(f"Category: {category}")
    print(f"Best Platforms: {', '.join(result['Best Platforms'])}")
    print("Cluster Stats:", result['Cluster Stats'])
    print("-" * 40)

# Close database connection
db.close()
def get_category_recommendations(category_name, results):
    if category_name in results:
        data = results[category_name]
        return {
            "Best Platforms": ", ".join(data["Best Platforms"]),
            "Cluster Stats": data["Cluster Stats"]
        }
    else:
        return {"error": "Category not found. Please check the name and try again."}

# Example usage:
category_name = input("Enter the category name: ")
recommendation = get_category_recommendations(category_name, results)

if "error" in recommendation:
    print(recommendation["error"])
else:
    print(f"Category: {category_name}")
    print(f"Best Platforms: {recommendation['Best Platforms']}")
    for stat, value in recommendation["Cluster Stats"].items():
        print(f"{stat}: {value}")
