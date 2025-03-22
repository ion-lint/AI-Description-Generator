import os
from flask import Flask, render_template, request, jsonify
import difflib
import matplotlib.pyplot as plt
import io, base64
import openai

app = Flask(__name__)

# OpenAI API key
openai.api_key = ""

def generate_text(product_name, style):
    """Generates a sales text using the OpenAI API."""
    if style == "rational":
        user_prompt = f"Write a sales description for the product «{product_name}» focusing on benefits."
    elif style == "emotional":
        user_prompt = f"Write an emotional description for the product «{product_name}» using vivid adjectives and an inspiring tone."
    else:
        user_prompt = f"Write a sales text for the product «{product_name}». Do not repeat the original prompt verbatim."

    try:
        # Correct call to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are an assistant for creating compelling sales texts..."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=1.2
        )

        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error generating text via the OpenAI API."

def highlight_diff(generated, base_text):
    """Highlights differences between the generated text and the original description."""
    diff = list(difflib.ndiff(base_text.split(), generated.split()))
    highlighted = []
    for token in diff:
        if token.startswith('+ '):
            highlighted.append(f"<mark>{token[2:]}</mark>")
        elif token.startswith('  '):
            highlighted.append(token[2:])
    return ' '.join(highlighted)

def get_sentiment_score(text):
    """Dummy evaluation of the text's sales effectiveness (can be replaced with an ML model in the future)."""
    return 0.65

def create_bar_chart(ordinary_score, rational_score, emotional_score):
    """Creates a bar chart comparing sales effectiveness scores."""
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ["Basic", "Rational", "Emotional"]
    scores = [ordinary_score, rational_score, emotional_score]
    colors = ['#656565', '#00ffa2', '#f7f7f7']
    ax.bar(categories, scores, color=colors)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Sales Effectiveness Score", fontsize=12)
    ax.set_title("Comparison of Descriptions", fontsize=14)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    product_name = data.get('product_name')
    ordinary_text = data.get('ordinary_text')

    if not product_name or not ordinary_text:
        return jsonify({"error": "Please provide the product name and the base description."}), 400

    # Generate descriptions
    rational_text = generate_text(product_name, "rational")
    emotional_text = generate_text(product_name, "emotional")

    # Highlight differences
    rational_diff = highlight_diff(rational_text, ordinary_text)
    emotional_diff = highlight_diff(emotional_text, ordinary_text)

    # Dummy evaluation of sales effectiveness
    ordinary_score = get_sentiment_score(ordinary_text)
    rational_score = get_sentiment_score(rational_text)
    emotional_score = get_sentiment_score(emotional_text)

    # Create bar chart
    chart = create_bar_chart(ordinary_score, rational_score, emotional_score)

    return jsonify({
        "product_name": product_name,
        "ordinary_text": ordinary_text,
        "rational_text": rational_text,
        "emotional_text": emotional_text,
        "rational_diff": rational_diff,
        "emotional_diff": emotional_diff,
        "chart": chart,
        "ordinary_score": round(ordinary_score * 100, 2),
        "rational_score": round(rational_score * 100, 2),
        "emotional_score": round(emotional_score * 100, 2)
    })

if __name__ == '__main__':
    app.run(debug=True)
