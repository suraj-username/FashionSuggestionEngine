from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import lancedb
import os

# Include the reverse image search related imports
from google_img_source_search import ReverseImageSearcher

app = Flask(__name__)
CORS(app)

# Load the CLIP model and processor for embedding generation
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Connect to the Lancedb database and load the table once
db = lancedb.connect("./my_lancedb_new")
table_name = "my_table"
tbl = db.open_table(table_name)  # Load the table once

def embedding_from_text(query):
    text_inputs = processor(text=query, return_tensors="pt", truncation=True)
    query_vector = model.get_text_features(**text_inputs)
    return query_vector[0].detach().numpy()

def embedding_from_image(image):
    inputs = processor(images=image, return_tensors="pt")
    image_vector = model.get_image_features(**inputs)
    return image_vector[0].detach().numpy()

def search_lancedb(query_vector):
    # Query Lancedb with cosine similarity metric and limit results to top 10
    results = tbl.search(query_vector).metric('cosine').nprobes(10).limit(10).to_pandas()
    return results

@app.route('/search', methods=['POST'])
def search():
    data = request.form
    text_input = data.get('textInput')
    image_file = request.files.get('imageInput')
    
    # Generate the embedding based on text or image input
    if text_input:
        query_vector = embedding_from_text(text_input)
    elif image_file:
        image = Image.open(image_file).convert('RGB')
        query_vector = embedding_from_image(image)
    else:
        return jsonify({'error': 'No valid input provided'}), 400

    # Query the Lancedb and get the top 10 results
    results = search_lancedb(query_vector)

    # Format results for JSON response
    formatted_results = []
    for index, row in results.iterrows():
        formatted_results.append({
            'image_url': row['payload']['image_url'],
            'product_title': row['payload']['meta']['product_title']
        })
    return jsonify({'results': formatted_results})

# Reverse image search endpoint
@app.route('/reverse-search', methods=['POST'])
def reverse_search():
    data = request.get_json()  # Get the JSON data
    if data is None:
        return jsonify({'error': 'No data provided'}), 400  # Handle case where no JSON is provided

    image_url = data.get('image_url')  # Retrieve the image URL from the incoming JSON
    list_of_links = get_ecommerce_links(image_url)
    
    # Prepare response with links
    formatted_links = []
    for link in list_of_links:
        formatted_links.append({
            'page_title': link.page_title,
            'page_url': link.page_url,
            'image_url': link.image_url
        })
    
    return jsonify({'links': formatted_links})  # Return the result as a JSON response

def get_ecommerce_links(image_url):
    """
    Pass an image link as input and return the top 10 links.
    """
    rev_img_searcher = ReverseImageSearcher()
    res = rev_img_searcher.search(image_url)
    return res[:10]  # Return only the top 10 results

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
