from dotenv import load_dotenv
import json
from openai import OpenAI
import os
import random
import time
from tqdm import tqdm


load_dotenv()

def call_llm(
    client: OpenAI,
    system_prompt: str,
    user_input: str,
    model: str = "deepseek-chat", 
    temperature: float = 0
) -> str|None:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=temperature,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return None

def run_meta_review(
    llm_client: OpenAI, 
    meta_prompt: str, 
    question_to_review: str, 
    post_title: str, 
    post_body: str
) -> str|None:
    formatted_prompt = meta_prompt.replace("{{INSERT_QUESTION}}", question_to_review)\
        .replace("{{INSERT_POST_TITLE}}", post_title)\
        .replace("{{INSERT_POST_BODY}}", post_body)
    
    return call_llm(
        client=llm_client,
        system_prompt=formatted_prompt,
        user_input="",
        temperature=0
    )

def final_question_selector(
    llm_client: OpenAI,
    final_selector_prompt: str,
    recall_question: str,
    interpreative_question: str,
    contextual_question: str,
    post_title: str, 
    post_body: str
) -> str|None:
    formatted_prompt = final_selector_prompt.replace("{{ITEM_1}}", recall_question)\
        .replace("{{ITEM_2}}", interpreative_question)\
        .replace("{{ITEM_3}}", contextual_question)\
        .replace("{{INSERT_POST_TITLE}}", post_title)\
        .replace("{{INSERT_POST_BODY}}", post_body)
    
    return call_llm(
        client=llm_client,
        system_prompt=formatted_prompt,
        user_input="",
        temperature=0
    )


if __name__ == "__main__":
    llm_client = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://api.deepseek.com")
    
    with open("data/reddit_posts/reddit_posts.json", "r") as f:
        reddit_posts = json.load(f)

    with open("data/prompts/prompts.json", "r") as f:
        base_prompts = json.load(f)
        
    final_questions = []

    for reddit_post in tqdm(reddit_posts):
        time.sleep(random.uniform(1,2))
        post_title = reddit_post.get('post_title')
        post_body = reddit_post.get('post_text')
        post_details = f"{post_title} {post_body}"
        
        base_questions = {}
        for q_type, prompt in base_prompts.items():
            if q_type in ("recall_prompt", "interpretative_prompt", "contextual_prompt"):
                base_questions[q_type] = call_llm(
                    llm_client,
                    prompt,
                    post_details
                )
        
        refined_questions = {}
        for q_type, question in base_questions.items():
            if question:
                refined_questions[q_type] = run_meta_review(
                    llm_client=llm_client,
                    meta_prompt=base_prompts["meta_prompt"],
                    question_to_review=question,
                    post_title=post_title,
                    post_body=post_body
                )
                
        final_question = final_question_selector(
            llm_client=llm_client,
            final_selector_prompt=base_prompts["final_selector_prompt"],
            recall_question=refined_questions.get("recall_prompt", ""),
            interpreative_question=refined_questions.get("interpretative_prompt", ""),
            contextual_question=refined_questions.get("contextual_prompt", ""),
            post_title=post_title,
            post_body=post_body
        )
        
        if final_question:
            final_question = final_question.replace("```json", "").replace("```", "").strip()
            
        final_questions.append(final_question)
        
    with open("data/pop_questions/pop_questions.json", "a") as f:
        json.dump(final_questions, f, indent=2)
