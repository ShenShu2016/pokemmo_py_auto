def is_go_pc(skill_pp_dict):
    """判断是否需要回城补给"""
    if skill_pp_dict["点到为止"] < 1:
        print("点到为止 用完，回家")
        return True
    elif skill_pp_dict["蘑菇孢子"] < 1:
        print("蘑菇孢子 用完，回家")
        return True
    elif skill_pp_dict["skill_4"] < 1:
        print("skill_4 用完，回家")
        return True
    elif skill_pp_dict["黑夜魔影"] < 5:
        print("黑夜魔影 用完，回家")
        return True
