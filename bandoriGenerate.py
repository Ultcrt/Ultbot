from ultbot.plugins.bandori_interface.update import new_fetch, complete_fetch


if __name__ == "__main__":
    flag = input("0 for update, others for generate")

    func = new_fetch if flag == 0 else complete_fetch

    # 卡牌更新
    print("Getting cards")
    result_cards = func('cards')
    # 活动更新
    print("Getting events")
    result_events = func('events')
    # 卡池更新
    print("Getting gacha")
    result_gacha = func('gacha')

    print("Done")
