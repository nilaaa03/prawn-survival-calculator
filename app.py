import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

FEEDING_TABLE = [
    (0.2,  None, None), (0.7,  None, None), (1.4,  None, None),
    (2.4,  10.0, 8.0),  (3.6,  8.0,  6.0),  (5.2,  6.0,  5.5),
    (7.0,  5.5,  5.0),  (9.0,  5.0,  4.6),  (11.0, 4.6,  4.2),
    (13.0, 4.2,  3.8),  (15.5, 3.8,  4.1),  (18.0, 4.1,  3.7),
    (20.5, 3.7,  3.4),  (23.0, 3.4,  3.1),  (26.0, 3.1,  2.9),
    (29.0, 2.9,  2.7),  (32.0, 2.7,  2.5),  (35.0, 2.5,  2.3),
    (38.0, 2.3,  2.2),  (42.0, 2.2,  2.1),  (46.0, 2.1,  2.0),
    (50.0, 2.0,  1.9),
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