from flask import Flask, render_template, request, jsonify
import openai
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

openai.api_key = 'dont steal my key pls >-<'

def extract_video_id(url):
    if "youtube.com" in url:
        print(str(url.split("v=")[1].split("&")[0] + " is the video id"))
        return url.split("v=")[1].split("&")[0] 
    elif "youtu.be" in url:
        print(str(url.split("/")[-1] + " is the video id"))
        return url.split("/")[-1]
    return None

def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item['text'] for item in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def generate_quiz(transcript, num_questions=5):
    prompt = f"Create {num_questions} multiple-choice questions from this YouTube transcript: {transcript}. Make sure each question has 4 options."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates quizzes."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return None



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        youtube_url = request.form.get("youtube_url")
        num_questions = request.form.get("num_questions")  # Get the number of questions
        video_id = extract_video_id(youtube_url)

        if video_id:
            transcript = fetch_transcript(video_id)
            if transcript:
                quiz = generate_quiz(transcript, num_questions)
                if quiz:
                    return jsonify({"quiz": quiz})
                else:
                    return jsonify({"error": "Failed to generate quiz"}), 500
            else:
                return jsonify({"error": "Failed to fetch transcript"}), 500
        else:
            return jsonify({"error": "Invalid YouTube URL"}), 400

    return render_template("index.html")



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
