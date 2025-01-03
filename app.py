import os
import time
from flask import Flask, request, jsonify, render_template
from transformers import BartTokenizer, BartForConditionalGeneration

# Suppress info and warning messages from TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

app = Flask(__name__)

# Paths to your local BART model and tokenizer
model_path = "bart_model"  # Adjust this path as needed
tokenizer_path = "bart_tokenizer"  # Adjust this path as needed

# Load the BART model and tokenizer
model = BartForConditionalGeneration.from_pretrained(model_path)
tokenizer = BartTokenizer.from_pretrained(tokenizer_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    input_text = data.get('text', '')

    if not input_text.strip():
        return jsonify({'error': 'Input text is empty.'}), 400

    try:
        # Tokenize the input text
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True, max_length=1024)

        # Measure the time taken for summarization
        start_time = time.time()

        # Generate the summary
        summary_ids = model.generate(inputs['input_ids'], max_length=150, num_beams=4, early_stopping=True)

        # Decode the summary
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        end_time = time.time()
        elapsed_time = end_time - start_time

        return jsonify({
            'summary': summary,
            'time_taken': f"{elapsed_time:.2f} seconds"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
