import random


async def random_line(filepath: str, delete: bool = True):
    with open(filepath, 'r') as file:
        keys = file.readlines()

    if not keys:
        return False
    random_key = random.choice(keys)
    if delete:
        keys.remove(random_key)

        with open(filepath, 'w') as file:
            file.writelines(keys)

    return random_key.strip()


def get_all_lines(filepath: str, delete_empty: bool = True):
    lines = []
    with open(filepath, 'r') as file:
        lines = file.readlines()

    if delete_empty:
        lines = [line.strip() for line in lines if line.strip()]

    return lines
