import os
import random
import uuid


def generate_math_captcha():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operators = ['+', '-', '*']
    operator = random.choice(operators)
    question = f"{num1} {operator} {num2}"
    answer = str(eval(question))
    return question, answer


def get_random_filename(directory):
    def wrapper(instance, filename):
        extension = filename.split('.')[-1]
        random_filename = f'{uuid.uuid4()}.{extension}'
        return os.path.join(directory, random_filename)

    return wrapper
