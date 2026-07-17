import re
import keyword


class Helper:
    class_regices = (
        re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$"),
        re.compile(r"^-[A-Za-z_-][A-Za-z0-9_-]*$"),
    )
    attr_name_regex = re.compile(r'^[^\s\x00-\x1f\x7f-\x9f"\'<>/=]+$')

    @staticmethod
    def is_css_identifier(s: str):
        if any([i.match(s) for i in Helper.class_regices]):
            return True
        return False

    @staticmethod
    def is_html_attr_name(s: str):
        m = Helper.attr_name_regex.match(s)
        if m:
            return True
        return False

    @staticmethod
    def preprocess(non_py_word:str)->str|None:
        if not non_py_word.isidentifier():
            if "-" in non_py_word:
                if non_py_word.rindex("-") == len(non_py_word) - 1:
                    raise ValueError(f"`-` in end of non_py_word `{non_py_word}` creates opening for ambiguity.")
                non_py_word = non_py_word.replace("-", "_")
            else:
                raise ValueError(f"non_py_word `{non_py_word}` contains characters that can't be casted to python identifier without data loss.")

        while non_py_word in keyword.kwlist:
            non_py_word += "_"
        return non_py_word


    @staticmethod
    def compile(tag:str, attr:dict[str, str], style:dict[str, str], classes:list[str]):
        pass
