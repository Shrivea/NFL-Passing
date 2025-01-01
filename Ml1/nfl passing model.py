import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

# Load the dataset
df = pd.read_csv("NFL_Passing_STAT.csv")

# Step 1: Assign unique IDs
df['Player_id'] = df['Player'].factorize()[0]
#print(df['Player_id'])
print(df)
# Step 2: Aggregate previous pass yards
df['Prev_Yards'] = df.groupby('Player_id')['Pass Yds'].shift(1)
print(df['Prev_Yards'])
# Drop rows with NaN values in 'Prev_Yards'
df = df.dropna(subset=['Prev_Yards'])
print(df)

# Calculate average previous yards for each player
player_avg_prev_yards = df.groupby('Player_id')['Prev_Yards'].mean().reset_index()
player_avg_prev_yards.rename(columns={'Prev_Yards': 'Avg_Prev_Yards'}, inplace=True)

# Merge the average previous yards back into the main DataFrame
df = df.merge(player_avg_prev_yards, on='Player_id', how='left')
print(df)
# Step 3: Prepare features and target for training
X = df[['Avg_Prev_Yards', 'Cmp%', 'TD', 'INT', 'Rate']]  # Features
y = df['Pass Yds']  # Target

# Ensure that all rows are included in the feature set
print(f"Total rows in dataset: {df.shape[0]}")

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Step 5: Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mae = mean_absolute_error(y_test, y_pred)
#print(f"Mean Absolute Error: {mae:.2f}")

# Step 6: Create a DataFrame for predictions
# X_test does not have the original index, so we need to merge back using index
X_test_with_index = X_test.copy()
X_test_with_index['Actual Pass Yds'] = y_test.values
X_test_with_index['Predicted Pass Yds'] = y_pred

# Reset index to align with original DataFrame
X_test_with_index.reset_index(drop=True, inplace=True)

# Ensure the original DataFrame with all data
df_with_predictions = df.copy()
df_with_predictions['Predicted Pass Yds'] = pd.NA  # Initialize with missing values

# Update only the rows that are in X_test
df_with_predictions.loc[X_test.index, 'Predicted Pass Yds'] = X_test_with_index['Predicted Pass Yds'].values

# Save the DataFrame with predictions to a new CSV file
df_with_predictions.to_csv("NFL_Passing_Predictions.csv", index=False)

#print("Predictions saved to NFL_Passing_Predictions.csv")
