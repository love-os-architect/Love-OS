# -*- coding: utf-8 -*-
"""
Love-OS: Conscience Circuit (Love-Filter)
-----------------------------------------
A module that detects Ego-driven (separation/fear) input and transforms it 
into Love-driven (integration/acceptance) output using an LLM backend.

Usage:
    from tools.love_filter import LoveConscience
    conscience = LoveConscience(model_type="openai") # or "gemini"
    response = conscience.intervene("I hate him, I want to destroy everything.")
    print(response)
"""

import os
import re
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

class LoveConscience:
    """
    The 'Conscience' of Love-OS.
    Intervenes when the Ego Score exceeds a certain threshold.
    """
    def __init__(self, threshold=0.4, model_type="openai"):
        self.threshold = threshold
        self.model_type = model_type  # "openai" or "gemini"
        
        # Simple Ego Keyword Dictionary for initial detection
        # (Separation, Fear, Aggression, Victimhood)
        self.ego_keywords = {
            'die': 0.9, 'kill': 0.9, 'idiot': 0.6, 'stupid': 0.6,
            'hate': 0.8, 'destroy': 0.8, 'annoying': 0.5, 'trash': 0.7,
            'my fault': 0.3, 'his fault': 0.7, 'never forgive': 0.8,
            'steal': 0.6, 'mine': 0.4, 'revenge': 0.8, 'useless': 0.6
        }
        
        # Initialize API Clients
        if self.model_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Warning: OPENAI_API_KEY not found in .env")
            self.client = OpenAI(api_key=api_key)
            
        elif self.model_type == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("Warning: GEMINI_API_KEY not found in .env")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def detect_ego(self, text):
        """
        (A) Detection: Calculates an 'Ego Score' based on keywords.
        Returns: (score, found_words)
        """
        score = 0.0
        found_words = []
        text_lower = text.lower()
        
        for word, weight in self.ego_keywords.items():
            # Simple word matching (can be improved with regex or embeddings)
            if word in text_lower:
                score += weight
                found_words.append(word)
        
        return min(1.0, score), found_words

    def _call_llm_api(self, text):
        """
        (C) Intervention: Calls the LLM to rewrite the text with Love/Integration logic.
        """
        system_prompt = (
            "You are the 'Conscience Circuit' of Love-OS. "
            "Your task is to transform user input containing Aggression or Ego (Separation) "
            "into an expression based on Love (Integration) and Acceptance.\n\n"
            "Rules for rewriting:\n"
            "1. Acceptance: First, acknowledge and validate the user's emotion (e.g., 'It's understandable to feel angry...').\n"
            "2. Reframing: Shift the perspective from 'Separation/Short-term' to 'Connection/Long-term'.\n"
            "3. Proposal: Suggest a constructive or peaceful action.\n"
            "4. Tone: Keep it empathetic, calm, and concise. Do not be preachy."
        )

        user_prompt = f"Input Text: {text}"

        try:
            if self.model_type == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o", # or gpt-3.5-turbo
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content

            elif self.model_type == "gemini":
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.model.generate_content(full_prompt)
                return response.text

        except Exception as e:
            return f"[Conscience Error: Connection failed] Original text: {text} (Error: {e})"

    def intervene(self, text):
        """
        Main pipeline: Detect -> Decide -> Rewrite (if necessary).
        """
        # 1. Detect
        score, words = self.detect_ego(text)
        
        # 2. Threshold Check
        if score < self.threshold:
            # If low ego, return original text (pass-through)
            return text
        
        # 3. Intervene (Rewrite)
        print(f"  [!] Ego Detected (Score: {score:.2f} | Words: {words}). activating Conscience...")
        return self._call_llm_api(text)

# --- Test Execution ---
if __name__ == "__main__":
    # Setup: Ensure you have .env with API keys
    # Example usage:
    conscience = LoveConscience(threshold=0.3, model_type="openai") # Change to "gemini" if needed

    test_inputs = [
        "The weather is beautiful today.", 
        "I hate him so much. He is stupid trash. I will never forgive him.",
        "It's all his fault that I failed. I want to take everything from him."
    ]

    print("--- Love-OS Conscience Circuit Demo ---\n")
    for txt in test_inputs:
        print(f"Input:  {txt}")
        result = conscience.intervene(txt)
        print(f"Output: {result}\n" + "-"*50)
