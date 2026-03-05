from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/rank', methods=['POST'])
def rank_candidates():
    data = request.json
    jd = clean_text(data['job_description'])
    resumes = [clean_text(r) for r in data['resumes']]
    
    texts = [jd] + resumes
    vec = TfidfVectorizer(stop_words='english')
    matrix = vec.fit_transform(texts)
    
    scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    
    ranked = sorted(
        [{"id": i, "score": float(s)} for i, s in enumerate(scores)],
        key=lambda x: x['score'], reverse=True
    )
    return jsonify(ranked)

if __name__ == '__main__':
    app.run(debug=True)