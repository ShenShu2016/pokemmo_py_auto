from time import sleep

from thefuzz import fuzz


class Word_Recognizer:
    def __init__(self):
        self.ratio_functions = {
            "ratio": fuzz.ratio,
            "partial_ratio": fuzz.partial_ratio,
            "token_sort_ratio": fuzz.token_sort_ratio,
            "token_set_ratio": fuzz.token_set_ratio,
        }

    def compare_with_target(
        self, recognized_text, target_words, mode="token_set_ratio", threshold=80
    ):
        if mode not in self.ratio_functions:
            raise ValueError(
                f"Invalid mode: {mode}. Must be one of {list(self.ratio_functions.keys())}."
            )

        recognized_text = recognized_text.replace("\n", " ")

        target_text = " ".join(target_words)

        # print("recognized_text", recognized_text)
        # print("target_text", target_text)

        ratio_function = self.ratio_functions[mode]
        match_ratio = ratio_function(recognized_text, target_text)

        is_match = match_ratio >= threshold

        return is_match, match_ratio

    def compare_with_target_all_types(
        self, recognized_text, target_words, threshold=80
    ):
        recognized_text = recognized_text.replace("\n", " ")

        target_text = " ".join(target_words)

        # print("recognized_text", recognized_text)
        # print("target_text", target_text)

        match_results = {}
        for mode, ratio_function in self.ratio_functions.items():
            match_ratio = ratio_function(recognized_text, target_text)
            is_match = match_ratio >= threshold
            match_results[mode] = (is_match, match_ratio)

        return match_results


if __name__ == "__main__":
    from constant import target_words_dict
    from main import PokeMMO

    pokeMMO = PokeMMO()

    while True:
        result = pokeMMO.get_text_from_box_coordinate((214, 482), (627, 583))
        print("get_text_from_box_coordinate", result)
        # remove '\n'
        is_match, match_ratio = pokeMMO.word_recognizer.compare_with_target(
            result, target_words_dict["battle_option"]
        )
        print(f"Match: {is_match}, Match Ratio: {match_ratio}")
        sleep(10)

    while True:
        # result = pokeMMO.get_text_from_box_coordinate((214, 482), (627, 583))
        # print("get_text_from_box_coordinate", result)
        # # remove '\n'
        # is_match, match_ratio = pokeMMO.word_recognizer.compare_with_target(
        #     result, target_words_dict["battle_option"]
        # )
        # print(f"Match: {is_match}, Match Ratio: {match_ratio}")

        my_name_ORC = pokeMMO.get_text_from_center(
            box_width=125, box_height=25, offset_x=0, offset_y=104, config="--psm 7"
        )  # Player Name and guild name
        # is_match, match_ratio = pokeMMO.word_recognizer.compare_with_target(
        #     my_name_ORC, target_words=target_words_dict["name_area"], threshold=60
        # )
        # print(
        #     f"my_name_ORC: {my_name_ORC}, is_match: {is_match}, match_ratio: {match_ratio}"
        # )
        results = pokeMMO.word_recognizer.compare_with_target(
            my_name_ORC,
            target_words=target_words_dict["name_area"],
            threshold=40,
            mode="partial_ratio",
        )
        for mode, (is_match, match_ratio) in results.items():
            print(f"Mode: {mode}, Match: {is_match}, Match Ratio: {match_ratio}")
        sleep(3)
