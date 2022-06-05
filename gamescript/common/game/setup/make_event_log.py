from gamescript import battleui


def make_event_log(battle_ui_image, screen_rect):
    event_log = battleui.EventLog(battle_ui_image["event_log.png"], (0, screen_rect.height))
    troop_log_button = battleui.UIButton(battle_ui_image["event_log_button1.png"], 0)  # war tab log

    event_log_button = [
        battleui.UIButton(battle_ui_image["event_log_button2.png"], 1),  # army tab log button
        battleui.UIButton(battle_ui_image["event_log_button3.png"], 2),  # leader tab log button
        battleui.UIButton(battle_ui_image["event_log_button4.png"], 3),  # subunit tab log button
        battleui.UIButton(battle_ui_image["event_log_button5.png"], 4),  # delete current tab log button
        battleui.UIButton(battle_ui_image["event_log_button6.png"], 5)]  # delete all log button

    event_log_button = [troop_log_button] + event_log_button
    battleui.UIScroll(event_log, event_log.rect.topright)  # event log scroll

    return {"event_log": event_log, "troop_log_button": troop_log_button, "event_log_button": event_log_button}
