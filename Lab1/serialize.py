from typing import Union

class PyObject():
    """

    """
    @staticmethod
    def set(obj: Union[dict, list, tuple, str, int, float, bool, None]):
        string = PyObject.__set(obj)
        return string

    @staticmethod
    def __set(obj: Union[dict, list, tuple, str, int, float, bool, None]):
        type_ = type(obj)
        if type_ == dict:
            return PyObject.__set_dict(obj)
        elif type_ == list:
            return PyObject.__set_list(obj)
        elif type_ == tuple:
            return PyObject.__set_tuple(obj)
        elif type_ == str:
            return PyObject.__set_str(obj)
        elif type_ == int or type_ == float:
            return PyObject.__set_num(obj)
        elif type_ == bool:
            return PyObject.__set_bool(obj)
        elif obj is None:
            return PyObject.__set_none()
        else:
            raise Exception(f"Invalid type: {type_}")

    @staticmethod
    def __set_dict(obj: dict):
        string = "{"

        for key, value in obj.items():
            string += f'{key}: {PyObject.__set(value)}, '

        return string[:-2] + "}"

    @staticmethod
    def __set_list(obj: list):
        string = "["

        for item in obj:
            string += f"{PyObject.__set(item)}, "

        return string[:-2] + "]"

    @staticmethod
    def __set_tuple(obj: tuple):
        string = "("

        for item in obj:
            string += f"{PyObject.__set(item)}, "

        return string[:-2] + ")"

    @staticmethod
    def __set_str(obj: str):
        return f"'{obj}'"

    @staticmethod
    def __set_num(obj: Union[int, float]):
        return f'{str(obj)}'

    @staticmethod
    def __set_bool(obj: bool):
        return str(obj)

    @staticmethod
    def __set_none():
        return "None"

    @staticmethod
    def get(obj: str):
        return PyObject.__get(obj)

    @staticmethod
    def __get(obj: str):
        if obj[0] == "{" and obj[-1] == "}":
            return PyObject.__get_dict(obj)
        elif obj[0] == "[" and obj[-1] == "]":
            return PyObject.__get_list(obj)
        elif obj[0] == "(" and obj[-1] == ")":
            return PyObject.__get_tuple(obj)
        elif obj[0] == "'" and obj[-1] == "'":
            return PyObject.__get_str(obj)
        elif obj.replace(".", "", 1).isdigit():
            return PyObject.__get_num(obj)
        elif obj == "True":
            return PyObject.__get_true()
        elif obj == "False":
            return PyObject.__get_false()
        elif obj == "None":
            return PyObject.__get_none()
        else:
            raise Exception(f"Invalid value: {obj}")

    @staticmethod
    def __get_dict(obj: str):
        return {key.strip(): PyObject.__get(value.strip())
                for key, value in [item.split(":")
                                   for item in obj[1:-1].split(",")]}

    @staticmethod
    def __get_list(obj: str):
        return [PyObject.__get(item.strip()) for item in obj[1:-1].split(",")]

    @staticmethod
    def __get_tuple(obj: str):
        return tuple(PyObject.__get(item.strip()) for item in obj[1:-1].split(","))

    @staticmethod
    def __get_str(obj: str):
        return obj[1:-1]

    @staticmethod
    def __get_num(obj: str):
        if "." in obj:
            return float(obj)
        else:
            return int(obj)

    @staticmethod
    def __get_true():
        return True

    @staticmethod
    def __get_false():
        return False

    @staticmethod
    def __get_none():
        return None


if __name__ == '__main__':
    print(PyObject.set({"a": 1, "b": 2}))
    print(PyObject.set([1, 2, 3]))
    print(PyObject.set((1, 2, 3)))
    print(PyObject.set("string"))
    print(PyObject.set(1))
    print(PyObject.set(1.0))
    print(PyObject.set(True))
    print(PyObject.set(False))
    print(PyObject.set(None))
    print(PyObject.get("{a: 1, b: 2}"), type(PyObject.get("{a: 1, b: 2}")))
    print(PyObject.get("[1, 2, 3]"), type(PyObject.get("[1, 2, 3]")))
    print(PyObject.get("(1, 2, 3)"), type(PyObject.get("(1, 2, 3)")))
    print(PyObject.get("'string'"), type(PyObject.get("'string'")))
    print(PyObject.get("1"), type(PyObject.get("1")))
    print(PyObject.get("1.0"), type(PyObject.get("1.0")))
    print(PyObject.get("True"), type(PyObject.get("True")))
    print(PyObject.get("False"), type(PyObject.get("False")))
    print(PyObject.get("None"), type(PyObject.get("None")))

