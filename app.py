import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

FEEDING_TABLE = [
    (3,   6.67, 6.67),
    (4,   6.0,  6.0),
    (5,   5.6,  5.6),
    (6.6, 4.85, 4.85),
    (7.1, 4.79, 4.79),
    (7.6, 4.74, 4.74),
    (8.3, 4.82, 4.82),
    (9,   4.67, 4.67),
    (10,  4.4,  4.4),
    (11.1,4.14, 4.14),
    (12.5,3.84, 3.84),
    (14.2,3.66, 3.66),
    (16.6,3.49, 3.49),
    (20,  3.25, 3.25),
    (25,  2.8,  2.8),
    (33.3,2.4,  2.4),
    (40,  2.25, 2.25),
    (50,  2.2,  2.2),
    (66.6,2.1,  2.1),
    (100, 1.8,  1.8),
]

def get_feed_ratio(grams):
    best = None
    best_diff = float('inf')
    for entry in FEEDING_TABLE:
        diff = abs(entry[0] - grams)
        if diff < best_diff:
            best_diff = diff
            best = entry
    return best

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    try:
        grams = float(data['grams'])
        feed = float(data['feed'])

        if grams <= 0 or feed <= 0:
            return jsonify({'error': 'Values must be greater than zero.'}), 400

        entry = get_feed_ratio(grams)
        if entry is None or entry[1] is None:
            return jsonify({'error': 'No feeding ratio available for this weight range (too early stage).'}), 400

        kilograms = grams / 1000
        ratio_high = entry[1] / 100
        ratio_low  = entry[2] / 100

        count_low  = feed / (ratio_high * kilograms)
        count_high = feed / (ratio_low  * kilograms)

        biomass_low  = round(count_low  * grams / 1000, 2)
        biomass_high = round(count_high * grams / 1000, 2)

        return jsonify({
            'prawn_count_low':  round(count_low),
            'prawn_count_high': round(count_high),
            'biomass_low':      biomass_low,
            'biomass_high':     biomass_high,
            'body_weight':      entry[0],
            'feed_pct_high':    entry[1],
            'feed_pct_low':     entry[2],
        })
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid input. Please enter valid numbers.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))