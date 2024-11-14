#imports
from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import lancedb
import os
from google_img_source_search import ReverseImageSearcher
import numpy as np

app = Flask(__name__)
CORS(app)

# Loading the CLIP model
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Connecting to the database
db = lancedb.connect("./my_lancedb_new")
table_name = "my_table"
tbl = db.open_table(table_name)

def cosine_similarity(vector1, vector2):
    """
    Calculate the cosine similarity between two vectors.
    """
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    return dot_product / (norm_vector1 * norm_vector2)

def embedding_from_text(query):
    text_inputs = processor(text=query, return_tensors="pt", truncation=True)
    query_vector = model.get_text_features(**text_inputs)
    return query_vector[0].detach().numpy()

def embedding_from_image(image):
    inputs = processor(images=image, return_tensors="pt")
    image_vector = model.get_image_features(**inputs)
    return image_vector[0].detach().numpy()

def search_lancedb(query_vector, nprobes=100000, limit=100000):
    results = tbl.search(query_vector).metric('cosine').nprobes(nprobes).limit(limit).to_pandas()
    results['cosine_similarity'] = results.apply(lambda row: cosine_similarity(query_vector, row['vector']), axis=1)
    sorted_results = results.sort_values(by='cosine_similarity', ascending=False).head(10)
    return sorted_results



@app.route('/search', methods=['POST'])
def search():
    data = request.form
    text_input = data.get('textInput')
    image_file = request.files.get('imageInput')
    
    # Generating embedding of user input (Text and image)
    if text_input:
        query_vector = embedding_from_text(text_input)
    elif image_file:
        image = Image.open(image_file).convert('RGB')
        query_vector = embedding_from_image(image)
    else:
        return jsonify({'error': 'No valid input provided'}), 400

    # Getting 10 results from the lancedb vector database
    results = search_lancedb(query_vector)

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
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No data provided'}), 400 

    image_url = data.get('image_url')
    list_of_links = get_ecommerce_links(image_url)
    
    # Prepare response with links
    formatted_links = []
    for link in list_of_links:
        formatted_links.append({
            'page_title': link.page_title,
            'page_url': link.page_url,
            'image_url': link.image_url
        })
    
    return jsonify({'links': formatted_links})

def get_ecommerce_links(image_url):
    """
    Pass an image link as input and return the top 10 links.
    """
    rev_img_searcher = ReverseImageSearcher()
    res = rev_img_searcher.search(image_url)
    return res[:10] #10 results

if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)#
