import pickle

# Step 2: Open the pickle file in binary read mode
with open('partial-divider_salad_agents2_seed1_model1-bd_model2-bd.pkl', 'rb') as file:
    # Step 3: Load the data from the file
    data = pickle.load(file)

# Now you can use the 'data' variable
print(data)