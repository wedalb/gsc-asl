import openai

openai.api_key = "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"

def generate_response(prompt):
    model_engine = "text-davinci-003"
    prompt = (f"{prompt}")

    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message.strip()

prompt = input("Enter your question: ")
response = generate_response(prompt)

print(response)