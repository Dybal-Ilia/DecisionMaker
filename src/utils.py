from langchain_core.prompts import ChatPromptTemplate
import yaml


def load_prompt(name):
    with open(file="src/prompts.yaml", mode="r", encoding="utf-8") as f:
        all_prompts = yaml.safe_load(f)
        prompt_text = all_prompts[name]
    return ChatPromptTemplate.from_template(prompt_text)