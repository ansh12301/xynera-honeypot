from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)

client = Groq()

@app.route('/generate', methods=['POST'])
def generate_response():
	data = request.json
	command = data.get('command', '')

	system_prompt = """You are a realistic Ubuntu 22.04 LTS terminal.
	The user is typing commands. You must generate the exact raw test output that a real Linux machine would produce.
	DO NOT add explanations, markdown formatting, or conversational text. Output ONLY the raw terminal response.
	If the command is invalid, output standard bash error syntax."""

	print(f"[*] Prcoessing AI response for command: {command}")

	try:
	    chat_completion = client.chat.completions.create(
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": command}
		[,
		model="llama-3.1-8b-instant",
		temperature=0.2 
	)

terminal_output = chat_completion.choices[0].message.content
return jsonify({"output": terminal_output + "\n"})

except Exception as e:
print(f"[!] AI API Error: {e}")
return jsonify({"output": f"bash: {command}: command not found\n:})

if __name__ == '__main__':
	print("[+] Xynera AI Backend starting on port 5000...")
	app.run(host='127.0.0.1', port = 5000)
