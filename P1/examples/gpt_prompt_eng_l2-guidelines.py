from openai.types.chat import ChatCompletionMessageParam

from agent_common.llm_config import LLMSettings
from openai_client import create_client


def get_completion(prompt: str, model: str | None = None) -> str | None:
    messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": prompt}]
    settings = LLMSettings.from_environment()
    with create_client(settings) as client:
        response = client.chat.completions.create(
            model=model or settings.model,
            messages=messages,
            temperature=0,
        )
    print(f"raw response: {response}\n-----------------------------")
    return response.choices[0].message.content


# Principle 1: Write clear and specific instructions

def p1_t1_use_delimiters() -> None:
    # Tactic 1: Use delimiters to clearly indicate distinct parts of the input¶
    # Delimiters can be anything like: ```, """, < >, <tag> </tag>
    # 使用分隔符来清楚地指示输入的不同部分
    # 分隔符也是一种避免**提示词注入攻击**的好方法，比如当你想让模型提取文本中的信息时，可以使用分隔符来明确文本的边界，防止模型误解输入内容。
    text = """
    You should express what you want a model to do by
    providing instructions that are as clear and
    specific as you can possibly make them.
    This will guide the model towards the desired output,
    and reduce the chances of receiving irrelevant
    or incorrect responses. Don't confuse writing a
    clear prompt with writing a short prompt.
    In many cases, longer prompts provide more clarity
    and context for the model, which can lead to
    more detailed and relevant outputs.
    """

    prompt = f"""
    Summarize the text delimited by triple backticks
    into a single sentence.
    ```{text}```
    """

    response = get_completion(prompt)
    print(response)


def p1_t2_structured_output() -> None:
    # Tactic 2: Ask for a structured output
    # JSON, HTML
    # 让模型输出结构化的结果
    prompt = """
    Generate a list of three made-up book titles along
    with their authors and genres.
    Provide them in JSON format with the following keys:
    book_id, title, author, genre.
    """

    response = get_completion(prompt)
    print(response)


def p1_t3_check_conditions_text_1() -> None:
    # Tactic 3: Ask the model to check whether conditions are satisfied
    # 让模型检查条件是否满足
    text_1 = """
    Making a cup of tea is easy! First, you need to get some
    water boiling. While that's happening,
    grab a cup and put a tea bag in it. Once the water is
    hot enough, just pour it over the tea bag.
    Let it sit for a bit so the tea can steep. After a
    few minutes, take out the tea bag. If you
    like, you can add some sugar or milk to taste.
    And that's it! You've got yourself a delicious
    cup of tea to enjoy.
    """

    prompt = f"""
    You will be provided with text delimited by triple quotes.
    If it contains a sequence of instructions,
    re-write those instructions in the following format:

    Step 1 - ...
    Step 2 - ...
    ...
    Step N - ...

    If the text does not contain a sequence of instructions,
    then simply write "No steps provided."

    """ + '"""' + f"{text_1}" + '"""'

    response = get_completion(prompt)
    print("Completion for Text 1:")
    print(response)


def p1_t3_check_conditions_text_2() -> None:
    # 让模型检查条件是否满足
    # 这个应该是不满足的
    text_2 = """
    The sun is shining brightly today, and the birds are
    singing. It's a beautiful day to go for a
    walk in the park. The flowers are blooming, and the
    trees are swaying gently in the breeze. People
    are out and about, enjoying the lovely weather.
    Some are having picnics, while others are playing
    games or simply relaxing on the grass. It's a
    perfect day to spend time outdoors and appreciate the
    beauty of nature.
    """

    prompt = f"""
    You will be provided with text delimited by triple quotes.
    If it contains a sequence of instructions,
    re-write those instructions in the following format:

    Step 1 - ...
    Step 2 - ...
    ...
    Step N - ...

    If the text does not contain a sequence of instructions,
    then simply write "No steps provided."

    """ + '"""' + f"{text_2}" + '"""'

    response = get_completion(prompt)
    print("Completion for Text 2:")
    print(response)


def p1_t4_few_shot_prompting() -> None:
    # Tactic 4: "Few-shot" prompting
    # 给模型提供几个示例，让它学习你想要的格式或风格
    prompt = """
    你的任务是以一致的风格作答。

    <孩子>: 教教我什么是耐心。

    <祖父母>: 雕刻出最深峡谷的河流，始于一股不起眼的泉水；
    最宏伟的交响乐，起于一个单独的音符；
    最精妙的锦缎，也始于一根孤独的丝线。

    <孩子>: 教教我什么是韧性。
    """

    response = get_completion(prompt)
    print(response)


# Principle 2: Give the model time to think

def p2_t1_specify_steps_prompt_1() -> None:
    # Tactic 1: Specify the steps required to complete a task
    # 指定完成任务所需的步骤, COT 思维链
    text = """
    In a charming village, siblings Jack and Jill set out on
    a quest to fetch water from a hilltop
    well. As they climbed, singing joyfully, misfortune
    struck-Jack tripped on a stone and tumbled
    down the hill, with Jill following suit.
    Though slightly battered, the pair returned home to
    comforting embraces. Despite the mishap,
    their adventurous spirits remained undimmed, and they
    continued exploring with delight.
    """

    prompt_1 = f"""
    Perform the following actions:
    1 - Summarize the following text delimited by triple
    backticks with 1 sentence.
    2 - Translate the summary into Chinese.
    3 - List each name in the Chinese summary.
    4 - Output a json object that contains the following
    keys: chinese_summary, num_names.

    Separate your answers with line breaks.

    Text:
    ```{text}```
    """

    response = get_completion(prompt_1)
    print("Completion for prompt 1:")
    print(response)


def p2_t1_specify_steps_prompt_2() -> None:
    # Tactic 1: Specify the steps required to complete a task
    # 指定完成任务所需的步骤
    text = """
    In a charming village, siblings Jack and Jill set out on
    a quest to fetch water from a hilltop
    well. As they climbed, singing joyfully, misfortune
    struck—Jack tripped on a stone and tumbled
    down the hill, with Jill following suit.
    Though slightly battered, the pair returned home to
    comforting embraces. Despite the mishap,
    their adventurous spirits remained undimmed, and they
    continued exploring with delight.
    """
    prompt_2 = f"""
    Your task is to perform the following actions: 
    1 - Summarize the following text delimited by 
    <> with 1 sentence.
    2 - Translate the summary into Chinese.
    3 - List each name in the Chinese summary.
    4 - Output a json object that contains the 
    following keys: chinese_summary, num_names.

    Use the following format:
    Text: <text to summarize>
    Summary: <summary>
    Translation: <summary translation>
    Names: <list of names in summary>
    Output JSON: <json with summary and num_names>

    Text: <{text}>
    """
    response = get_completion(prompt_2)
    print("\nCompletion for prompt 2:")
    print(response)


def p2_t2_student_solution_check() -> None:
    # Tactic 2: Instruct the model to work out its own solution before rushing to a conclusion
    # 让模型在下结论前先自己解决问题
    # 注意学生的答案是不对的, 这个模型下没有用COT，模型也判断正确了
    # 教程本意是展示在没有让模型先思考的情况下，模型可能会直接判断学生正确了 
    prompt = """
    判断学生的解法是否正确。

    问题：
    我正在建设一个太阳能发电装置，需要你帮我计算财务成本。
    - 土地成本是每平方英尺 100 美元
    - 我可以买到每平方英尺 250 美元的太阳能板
    - 我谈了一个维护合同，每年固定 10 万美元，外加每平方英尺 10 美元
    第一年的总运营成本，如何表示为关于平方英尺数的函数？

    学生的解答：
    设 x 为装置面积（单位：平方英尺）。
    成本：
    1. 土地成本：100x
    2. 太阳能板成本：250x
    3. 维护成本：100,000 + 100x
    总成本：100x + 250x + 100,000 + 100x = 450x + 100,000
    """

    response = get_completion(prompt)
    print(response)


def p2_t2_student_solution_check_with_reasoning() -> None:
    prompt = """
    你的任务是判断学生的解法是否正确。
    请按以下步骤解决问题：
    - 先独立算出你自己的解法，并给出最终总成本。
    - 再将你的解法与学生解法对比，评估学生是否正确。
    在你自己完成计算之前，不要先下结论。

    请使用以下格式：
    问题：
    ```
    在此填写问题
    ```
    学生解法：
    ```
    在此填写学生解法
    ```
    实际解法：
    ```
    在此填写你的推导步骤和最终结果
    ```
    学生解法是否与刚刚计算出的实际解法一致：
    ```
    是 或 否
    ```
    学生评分：
    ```
    正确 或 错误
    ```

    问题：
    ```
    我正在建设一个太阳能发电装置，需要你帮我计算财务成本。
    - 土地成本是每平方英尺 100 美元
    - 我可以买到每平方英尺 250 美元的太阳能板
    - 我谈了一个维护合同，每年固定 10 万美元，外加每平方英尺 10 美元
    第一年的总运营成本，如何表示为关于平方英尺数的函数？
    ```
    学生解法：
    ```
    设 x 为装置面积（单位：平方英尺）。
    成本：
    1. 土地成本：100x
    2. 太阳能板成本：250x
    3. 维护成本：100,000 + 100x
    总成本：100x + 250x + 100,000 + 100x = 450x + 100,000
    ```
    实际解法：
    """

    response = get_completion(prompt)
    print(response)


# ## Prompting Principles
#- **Principle 1: Write clear and specific instructions**
#- **Principle 2: Give the model time to “think”**

# Model limitations: hallucinations

def model_limitations_hallucination_demo() -> None:
    # 模型幻觉：Boie is a real company, the product name is not real.
    # 感觉新模型幻觉少了很多
    prompt = """
    帮我介绍下天津二汽车生产的欧亚K7汽车的性能和价格。
    """

    prompt = "Tell me about AeroGlide UltraSlim Smart Toothbrush by Boie"

    response = get_completion(prompt)
    print(response)


def main() -> None:
    # print(get_completion("Hello!"))
    # p1_t1_use_delimiters()
    print("===============================")
    # 如果连续调用，模型会输出类似下边的思考过程才会是正式结果，为什么？
    # **Creating a JSON response**
    #
    #  I need to keep the answer simple and not use any tools. It should be short and possibly in a markdown code block, starting with the language name. I’ll create a JSON format that includes keys like book_id, title, author, and genre. I’m thinking of three made-up titles. It feels clear that I should format it as an array of objects. So, let’s get ready to craft that valid JSON!```json

    # Principle 1
    # p1_t2_structured_output()
    # p1_t3_check_conditions_text_1()
    # p1_t3_check_conditions_text_2()
    # p1_t4_few_shot_prompting()

    # Principle 2  COT OR ReAct
    # p2_t1_specify_steps_prompt_1()
    # p2_t1_specify_steps_prompt_2()
    # p2_t2_student_solution_check()
    # p2_t2_student_solution_check_with_reasoning()

    # Model limitation
    model_limitations_hallucination_demo()


if __name__ == "__main__":
    main()
