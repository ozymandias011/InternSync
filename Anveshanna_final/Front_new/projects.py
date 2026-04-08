import openai

# Set up Azure OpenAI API credentials
openai.api_type = "azure"
openai.api_base = "https://gourav-openai-service.openai.azure.com/"  # Replace with your Azure OpenAI endpoint
openai.api_version = "2023-05-15"  # Use the latest API version
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")


def get_top_industry_topics(subject):
    """Fetches the top 5 industry-relevant topics for placements in a given subject using ChatGPT."""
    
    prompt = f"""
    List exactly 5 most important topics in {subject} for industry and placements.
    Format: Return only the topic names, one per line, without numbers or bullets.
    Example:
    Topic One
    Topic Two
    Topic Three
    Topic Four
    Topic Five
    """

    try:
        response = openai.ChatCompletion.create(
            engine="gpt-4o-mini",  # Changed to correct engine name
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )

        # Split response into lines and clean up
        topics_text = response["choices"][0]["message"]["content"]
        topics_array = [topic.strip() for topic in topics_text.split('\n') if topic.strip()]
        
        # Ensure we have exactly 5 topics
        topics_array = topics_array[:5]
        
        return topics_array
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

# Test the function
if __name__ == "__main__":
    subject = input("Enter the subject: ")
    topics = get_top_industry_topics(subject)
    
    print(f"\nTop 5 Industry-Relevant Topics in {subject} for Placements:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
