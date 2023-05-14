class GameStatus:
    def __init__(self, pokeMMO_instance):
        # Retrieve the necessary attributes from the PokeMMO instance
        self.handle = pokeMMO_instance.handle
        # ... additional code ...

    def check_game_status(self, threshold=0.986):
        face_area = self.get_box_coordinate_from_center(
            box_width=65,
            box_height=65,
            offset_x=0,
            offset_y=65,
        )
        face_area_l = face_area[0]
        face_area_r = face_area[1]

        templates = [
            self.face_down_color,
            self.face_up_color,
            self.face_left_color,
            self.face_right_color,
        ]
        template_names = [
            "face_down_color",
            "face_up_color",
            "face_left_color",
            "face_right_color",
        ]

        for template, template_name in zip(templates, template_names):
            if self.find_items(
                template_color=template,
                threshold=threshold,
                max_matches=5,
                top_left=face_area_l,
                bottom_right=face_area_r,
            ):
                # print(f"{template_name} detected.")
                return "NORMAL"

        if self.find_items(self.enemy_hp_bar_color, threshold=0.99, max_matches=10):
            # print("Enemy HP bar detected.")
            return "BATTLE"
        else:
            # print("Unknown game state.")
            return "OTHER"
