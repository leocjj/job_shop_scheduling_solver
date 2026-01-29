import json


def print_first_level_keys(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        for key in data.keys():
            print(key)


# Example usage
file_path = r"tests3\30_30_10.json"
print_first_level_keys(file_path)


numbers = ",".join(str(i) for i in range(1, 101))
print(numbers)
