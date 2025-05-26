import openai

class NLGRegulatoryGenerator:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def generate_fda_report(self, molecule_name: str, batch_id: str, anomalies: dict):
        prompt = (
            f"Generate a professional FDA compliance report for molecule '{molecule_name}', "
            f"batch '{batch_id}'. Summarize the following detected anomalies and suggest corrective actions:\n"
            f"{anomalies}\n\n"
            "Format as a formal FDA submission section."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        return response['choices'][0]['message']['content']

if __name__ == "__main__":
    # Replace with your real API key
    generator = NLGRegulatoryGenerator(api_key="sk-...YOUR_OPENAI_API_KEY...")
    anomalies = {
        "impurity_level": "Exceeded threshold in sample 17A",
        "temperature_variation": "Spike of +2°C during synthesis",
    }
    report = generator.generate_fda_report("Aspirin", "BATCH20250525", anomalies)
    print(report)
