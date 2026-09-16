# Transforming
# In this lesson, we explore text transformation tasks with LLMs:
# translation, tone adjustment, format conversion, and proofreading.

from openai.types.chat import ChatCompletionMessageParam

from agent_common.llm_config import LLMSettings
from openai_client import create_client


def get_completion(
    prompt: str, model: str | None = None, temperature: float = 0
) -> str | None:
    messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": prompt}]
    settings = LLMSettings.from_environment()
    with create_client(settings) as client:
        response = client.chat.completions.create(
            model=model or settings.model,
            messages=messages,
            temperature=temperature,
        )
    return response.choices[0].message.content


def translation_basic() -> None:
    prompt = """
    Translate the following English text to Spanish:
    ```Hi, I would like to order a blender```
    """
    response = get_completion(prompt)
    print(response)


def detect_language() -> None:
    prompt = """
    Tell me which language this is:
    ```Combien coute le lampadaire?```
    """
    response = get_completion(prompt)
    print(response)


def translate_to_multiple_styles() -> None:
    prompt = """
    Translate the following text to French and Spanish
    and English pirate:
    ```I want to order a basketball```
    """
    response = get_completion(prompt)
    print(response)


def spanish_formal_informal() -> None:
    prompt = """
    Translate the following text to Spanish in both the
    formal and informal forms:
    'Would you like to order a pillow?'
    """
    response = get_completion(prompt)
    print(response)


def universal_translator_demo() -> None:
    user_messages = [
        "La performance du systeme est plus lente que d'habitude.",
        "Mi monitor tiene pixeles que no se iluminan.",
        "Il mio mouse non funziona",
        "Moj klawisz Ctrl jest zepsuty",
        "Wo de pingmu zai shanshuo",
    ]

    for issue in user_messages:
        detect_prompt = f"Tell me what language this is: ```{issue}```"
        lang = get_completion(detect_prompt)
        print(f"Original message ({lang}): {issue}")

        translate_prompt = f"""
        Translate the following text to English and Korean:
        ```{issue}```
        """
        translated = get_completion(translate_prompt)
        print(translated)
        print("-" * 40)


def tone_transformation() -> None:
    prompt = """
    Translate the following from slang to a business letter:
    'Dude, this is Joe, check out this spec on this standing lamp.'
    """
    response = get_completion(prompt)
    print(response)


def format_conversion_json_to_html() -> None:
    data_json = {
        "restaurant employees": [
            {"name": "Shyam", "email": "shyamjaiswal@gmail.com"},
            {"name": "Bob", "email": "bob32@gmail.com"},
            {"name": "Jai", "email": "jai87@gmail.com"},
        ]
    }

    prompt = f"""
    Translate the following Python dictionary from JSON to an HTML
    table with column headers and title:
    {data_json}
    """
    response = get_completion(prompt)
    print(response)


def spellcheck_examples() -> None:
    text_samples = [
        "The girl with the black and white puppies have a ball.",
        "Yolanda has her notebook.",
        "Its going to be a long day. Does the car need it's oil changed?",
        "Their goes my freedom. There going to bring they're suitcases.",
        "Your going to need you're notebook.",
        "That medicine effects my ability to sleep. Have you heard of the butterfly affect?",
        "This phrase is to cherck chatGPT for speling abilitty",
    ]

    for sample in text_samples:
        prompt = f"""
        Proofread and correct the following text and rewrite the corrected version.
        If you do not find any errors, just say "No errors found".
        Text: ```{sample}```
        """
        response = get_completion(prompt)
        print(response)


def rewrite_review() -> None:
    review_text = """
    Got this for my daughter for her birthday cuz she keeps taking
    mine from my room. Yes, adults also like pandas too. She takes
    it everywhere with her, and it's super soft and cute. One of the
    ears is a bit lower than the other, and I don't think that was
    designed to be asymmetrical. It's a bit small for what I paid for it
    though. I think there might be other options that are bigger for
    the same price. It arrived a day earlier than expected, so I got
    to play with it myself before I gave it to my daughter.
    """

    prompt = f"proofread and correct this review: ```{review_text}```"
    response = get_completion(prompt)
    print(response)


def rewrite_review_advanced() -> None:
    review_text = """
    Got this for my daughter for her birthday cuz she keeps taking
    mine from my room. Yes, adults also like pandas too. She takes
    it everywhere with her, and it's super soft and cute. One of the
    ears is a bit lower than the other, and I don't think that was
    designed to be asymmetrical. It's a bit small for what I paid for it
    though. I think there might be other options that are bigger for
    the same price. It arrived a day earlier than expected, so I got
    to play with it myself before I gave it to my daughter.
    """

    prompt = f"""
    Proofread and correct this review. Make it more compelling.
    Ensure it follows APA style guide and targets an advanced reader.
    Output in markdown format.
    Text: ```{review_text}```
    """
    response = get_completion(prompt)
    print(response)


def print_case_title(index: int, title: str) -> None:
    print(f"\n[{index}] {title}")
    print("-" * 60)


def case_1_translation() -> None:
    print_case_title(1, "翻译（基础翻译、语言识别、多风格翻译、正式/非正式语气）")
    translation_basic()
    detect_language()
    translate_to_multiple_styles()
    spanish_formal_informal()


def case_2_universal_translator() -> None:
    print_case_title(2, "Universal Translator 场景")
    universal_translator_demo()


def case_3_tone_transformation() -> None:
    print_case_title(3, "Tone Transformation（俚语转商务信）")
    tone_transformation()


def case_4_format_conversion() -> None:
    print_case_title(4, "Format Conversion（字典转 HTML 表格）")
    format_conversion_json_to_html()


def case_5_spellcheck() -> None:
    print_case_title(5, "Spellcheck/Grammar check（批量纠错）")
    spellcheck_examples()


def case_6_review_rewrite() -> None:
    print_case_title(6, "长评审稿的纠错与高级改写")
    rewrite_review()
    rewrite_review_advanced()


def run_all_cases() -> None:
    case_1_translation()
    case_2_universal_translator()
    case_3_tone_transformation()
    case_4_format_conversion()
    case_5_spellcheck()
    case_6_review_rewrite()


def main() -> None:
    print("===============================")
    # 按章节运行单个案例：
    # case_1_translation()
    # case_2_universal_translator()
    case_3_tone_transformation()
    # case_4_format_conversion()
    # case_5_spellcheck()
    # case_6_review_rewrite()

    # 一次性跑完整课：
    # run_all_cases()


if __name__ == "__main__":
    main()
