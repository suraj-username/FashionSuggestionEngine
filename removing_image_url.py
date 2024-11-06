import json

# Function to filter out entries with 'image_url' as 'N/A'
def filter_data(input_file, output_file):
    with open(input_file, 'r') as infile:
        # Create an empty list to store filtered data
        filtered_data = []
        
        # Read the file line by line
        for line in infile:
            try:
                # Load the current line as a JSON object
                data = json.loads(line.strip())
                
                # If 'image_url' is not 'N/A', add the entry to the filtered data
                if data.get('image_url') != 'N/A':
                    filtered_data.append(data)
            except json.JSONDecodeError:
                print("Error decoding line, skipping.")
        
    # Write the filtered data to a new JSON file
    with open(output_file, 'w') as outfile:
        # Write each entry as a JSON object on a new line
        for entry in filtered_data:
            json.dump(entry, outfile)
            outfile.write('\n')
    print(f"Filtered data saved to {output_file}")

# File paths
input_file = 'train_data.json'
output_file = 'new_train_data.json'

# Call the function
filter_data(input_file, output_file)
