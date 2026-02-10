from langchain_core.prompts import ChatPromptTemplate
import logging
import yaml

def load_prompt(name):
    with open(file="src/prompts.yaml", mode="r", encoding="utf-8") as f:
        all_prompts = yaml.safe_load(f)
        prompt_text = all_prompts[name]
    return ChatPromptTemplate.from_template(prompt_text)

def get_logger():
    logger = logging.getLogger("DecisionMaker")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            fmt="{asctime}-{levelname}-{name}-{message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def load_presets():
    with open(file="src/presets.yaml", mode="r", encoding="utf-8") as f:
        presets = yaml.safe_load(f)
        return presets

def load_team(preset_name:str):
    presets = load_presets()
    return presets[preset_name]