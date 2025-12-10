from machine import Pin, SoftI2C, PWM
from I2C_LCD import I2cLcd
from time import ticks_ms, sleep_ms
from random import randint
import time
import neopixel

# spilið er whack a mole og það er hægt að spila 2 saman.
# spilið virkar þannig að það kveikir á tokkum og þú átt að reyna að ýta á hann á undan hinni manneskjunni.
# sem ýtti á flesta takka vinnur umferðina og fær refsingu svo hinnn fær meyri sens á að vinna.
# fyrstur til að vinna 3 umferðir vinnur allt.

# Initialize two I2C buses and LCDs (two player displays)
i2c2 = SoftI2C(scl=Pin(13), sda=Pin(14), freq=400000)
lcd2 = I2cLcd(i2c2, 39, 2, 16)
i2c1 = SoftI2C(scl=Pin(11), sda=Pin(12), freq=400000)
lcd1 = I2cLcd(i2c1, 39, 2, 16)

# NeoPixel strips used as score indicators for each player (3 LEDs each)
p1_score_led = neopixel.NeoPixel(Pin(35), 3)
p2_score_led = neopixel.NeoPixel(Pin(18), 3)

# Custom character bitmaps for Icelandic/diacritic letters used on the LCD
þ = [0B10000,
     0B10000,
     0B11100,
     0B10010,
     0B10010,
     0B11100,
     0B10000,
     0B10000]
ð = [0B00010,
     0B00111,
     0B00010,
     0B01110,
     0B10010,
     0B10010,
     0B01100,
     0B00000]
á = [0B00010,
     0B00100,
     0B00000,
     0B01110,
     0B00001,
     0B01111,
     0B10001,
     0B01111]
ó = [0B00010,
     0B00100,
     0B00000,
     0B01110,
     0B10001,
     0B10001,
     0B10001,
     0B01110]
ö = [0B01010,
     0B00000,
     0B01110,
     0B10001,
     0B10001,
     0B10001,
     0B01110,
     0B00000]
é = [0B00010,
     0B00100,
     0B00000,
     0B01110,
     0B10001,
     0B11111,
     0B10000,
     0B01110]
ý = [0B00010,
     0B00100,
     0B10001,
     0B10001,
     0B01111,
     0B00001,
     0B01110,
     0B00000]
ú = [0B00010,
     0B00100,
     0B10001,
     0B10001,
     0B10001,
     0B10011,
     0B01101,
     0B00000]

def custom_characters(which_lcd):
    # Load the custom characters into the given LCD device
    which_lcd.custom_char(0, þ)
    which_lcd.custom_char(1, ð)
    which_lcd.custom_char(2, á)
    which_lcd.custom_char(3, ó)
    which_lcd.custom_char(4, é)
    which_lcd.custom_char(5, ý)
    which_lcd.custom_char(6, ú)
    which_lcd.custom_char(7, ö)

# Register custom characters on both LCDs
custom_characters(lcd1)
custom_characters(lcd2)

# Center start button and center LED
button_center = Pin(21, Pin.IN, Pin.PULL_UP)
led_center = Pin(47, Pin.OUT)

# Speaker (PWM) setup for sound effects
speaker = PWM(Pin(48))
speaker.init()
speaker.duty(0)

def button_noise():
    # Simple ascending tone sequence for button feedback
    speaker.duty(512)
    speaker.freq(65)
    sleep_ms(100)
    speaker.freq(400)
    sleep_ms(100)
    speaker.freq(800)
    sleep_ms(100)
    speaker.duty(0)

# -- Buttons and LEDs for the five mole positions (left/right per player) --
# Green mole (left/right)
button_lg = Pin(38, Pin.IN, Pin.PULL_UP)
button_state_before_lg = 0
button_rg = Pin(37, Pin.IN, Pin.PULL_UP)
button_state_before_rg = 0
led_g = Pin(39, Pin.OUT)

# Red mole (left/right)
button_lr = Pin(5, Pin.IN, Pin.PULL_UP)
button_state_before_lr = 0
button_rr = Pin(6, Pin.IN, Pin.PULL_UP)
button_state_before_rr = 0
led_r = Pin(4, Pin.OUT)

# Blue mole (left/right)
button_lb = Pin(9, Pin.IN, Pin.PULL_UP)
button_state_before_lb = 0
button_rb = Pin(10, Pin.IN, Pin.PULL_UP)
button_state_before_rb = 0
led_b = Pin(8, Pin.OUT)

# Yellow mole (left/right)
button_ly = Pin(2, Pin.IN, Pin.PULL_UP)
button_state_before_ly = 0
button_ry = Pin(42, Pin.IN, Pin.PULL_UP)
button_state_before_ry = 0
led_y = Pin(1, Pin.OUT)

# White mole (left/right)
button_lw = Pin(15, Pin.IN, Pin.PULL_UP)
button_state_before_lw = 0
button_rw = Pin(17, Pin.IN, Pin.PULL_UP)
button_state_before_rw = 0
led_w = Pin(16, Pin.OUT)


def punishment_wait():
    # Busy-wait for 2 seconds (used during punishment display)
    punishment_appear = ticks_ms()
    while ticks_ms() != punishment_appear + 2000:
        pass

# Punishment display helpers (show message on the losing player's LCD)
def punishment_one_hand(which_lcd):
    which_lcd.clear()
    which_lcd.putstr(f"{chr(0)}{chr(6)} {chr(0)}arft a{chr(1)}")
    which_lcd.move_to(0, 1)
    which_lcd.putstr(f"nota eina hendi")
    punishment_wait()

def punishment_one_eye(which_lcd):
    which_lcd.clear()
    which_lcd.putstr(f"{chr(0)}{chr(6)} {chr(0)}arft a{chr(1)}")
    which_lcd.move_to(0, 1)
    which_lcd.putstr(f"loka einu auga")
    punishment_wait()

def punishment_only_pinky(which_lcd):
    which_lcd.clear()
    which_lcd.putstr(f"{chr(0)}{chr(6)} {chr(0)}arft a{chr(1)}")
    which_lcd.move_to(0, 1)
    which_lcd.putstr(f"litla putan")
    punishment_wait()

punishment_list = [punishment_one_hand, punishment_one_eye, punishment_only_pinky]
while True:
    # Game state counters
    rounds_completed = 0
    player_1_wins = 0
    player_2_wins = 0
    player_1_punisments = []
    player_2_punisments = []
    p1_score_led.fill([0, 0, 0])
    p2_score_led.fill([0, 0, 0])
    p1_score_led.write()
    p2_score_led.write()

    # Main match loop: first to 3 round wins
    while player_1_wins < 3 and player_2_wins < 3:
        print(rounds_completed)

        # Short pause between rounds
        pause_for = (ticks_ms()) + 1500
        while ticks_ms() < pause_for:
            pass

        # Show instructions on both LCDs
        lcd1.clear()
        lcd2.clear()
        lcd1.putstr(f"mi{chr(1)}ju takki til")
        lcd1.move_to(0, 1)
        lcd1.putstr(f"a{chr(1)} byrja umfer{chr(1)}")
        lcd2.putstr(f"mi{chr(1)}ju takki til")
        lcd2.move_to(0, 1)
        lcd2.putstr(f"a{chr(1)} byrja umfer{chr(1)}")

        # Light center LED to indicate waiting for start
        led_center.value(1)

        # Wait for center button press (edge-detect: high->low)
        while True:
            button_center_state_before = 1
            while True:
                button_center_state = button_center.value()
                if button_center_state_before == 1 and button_center_state == 0:
                   round_start = True
                   led_center.value(0)
                   button_noise()
                   break
                button_center_state_before = button_center_state
            break

        # Initialize round scores
        player_1_score = 0
        player_2_score = 0

        # Setup timings for the round
        game_start = ticks_ms()
        mole_spawn = game_start + 3000  # first mole appears after 3s
        random_num = randint(3, 5)  # number of moles per round
        print(random_num)
        print(game_start)
        current_mole = 0

        # Text hide timers for LCD feedback messages
        text_disappear_1 = 0
        text_disappear_2 = 0

        # Show initial scores
        lcd1.clear()
        lcd2.clear()
        lcd1.putstr(f"Stig {player_1_score}")
        lcd2.putstr(f"Stig {player_2_score}")

        # Main mole-spawn loop for a single round
        while True:
            which_button = randint(0,4)  # choose one of 5 mole positions
            # For each position, check timers, then spawn mole and monitor buttons
            if which_button == 0:
                # Clear temporary messages when their timers expire and check round end
                if text_disappear_1 == ticks_ms():
                    lcd1.clear()
                    lcd1.putstr(f"Stig {player_1_score}")
                    if current_mole > random_num - 1:
                        break
                if text_disappear_2 == ticks_ms():
                    lcd2.clear()
                    lcd2.putstr(f"Stig {player_2_score}")
                    if current_mole > random_num - 1:
                        break

                # Spawn logic: when mole_spawn time equals current time
                if ticks_ms() == mole_spawn:
                    if current_mole > random_num - 1:
                        break
                    print("mole", current_mole + 1, "spawned")
                    led_g.value(1)
                    mole_spawned = ticks_ms()
                    mole_despawn = mole_spawned + 2000  # mole visible for 2s

                    # Wait while mole is active and check button presses for both players
                    while True:
                        button_state_lg = button_lg.value()
                        button_state_rg = button_rg.value()

                        # Mole despawn by timeout
                        if ticks_ms() == mole_despawn:
                            print("mole", current_mole + 1, "despawned")
                            led_g.value(0)
                            current_mole += 1
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break

                        # Player 1 hit (left green)
                        elif button_state_before_lg == 1 and button_state_lg == 0:
                            print("a")
                            lcd1.clear()
                            lcd1.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd1.move_to(0, 1)
                            lcd1.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_1 = ticks_ms()
                            text_disappear_1 = text_appear_1 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_g.value(0)
                            current_mole += 1
                            player_1_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break

                        # Player 2 hit (right green)
                        elif button_state_before_rg == 1 and button_state_rg == 0:
                            print("a")
                            lcd2.clear()
                            lcd2.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd2.move_to(0, 1)
                            lcd2.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_2 = ticks_ms()
                            text_disappear_2 = text_appear_2 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_g.value(0)
                            current_mole += 1
                            player_2_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break

                        # Store previous states for edge detection
                        button_state_before_lg = button_state_lg
                        button_state_before_rg = button_state_rg

            if which_button == 1:
                # Same logic as above but for red mole position
                if text_disappear_1 == ticks_ms():
                    lcd1.clear()
                    lcd1.putstr(f"Stig {player_1_score}")
                    if current_mole > random_num - 1:
                        break
                if text_disappear_2 == ticks_ms():
                    lcd2.clear()
                    lcd2.putstr(f"Stig {player_2_score}")
                    if current_mole > random_num - 1:
                        break
                if ticks_ms() == mole_spawn:
                    if current_mole > random_num - 1:
                        break
                    print("mole", current_mole + 1, "spawned")
                    led_r.value(1)
                    mole_spawned = ticks_ms()
                    mole_despawn = mole_spawned + 2000
                    while True:
                        button_state_lr = button_lr.value()
                        button_state_rr = button_rr.value()
                        if ticks_ms() == mole_despawn:
                            print("mole", current_mole + 1, "despawned")
                            led_r.value(0)
                            current_mole += 1
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_lr == 1 and button_state_lr == 0:
                            print("a")
                            lcd1.clear()
                            lcd1.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd1.move_to(0, 1)
                            lcd1.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_1 = ticks_ms()
                            text_disappear_1 = text_appear_1 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_r.value(0)
                            current_mole += 1
                            player_1_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_rr == 1 and button_state_rr == 0:
                            print("a")
                            lcd2.clear()
                            lcd2.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd2.move_to(0, 1)
                            lcd2.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_2 = ticks_ms()
                            text_disappear_2 = text_appear_2 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_r.value(0)
                            current_mole += 1
                            player_2_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        button_state_before_lr = button_state_lr
                        button_state_before_rr = button_state_rr

            if which_button == 2:
                # Blue mole position
                if text_disappear_1 == ticks_ms():
                    lcd1.clear()
                    lcd1.putstr(f"Stig {player_1_score}")
                    if current_mole > random_num - 1:
                        break
                if text_disappear_2 == ticks_ms():
                    lcd2.clear()
                    lcd2.putstr(f"Stig {player_2_score}")
                    if current_mole > random_num - 1:
                        break
                if ticks_ms() == mole_spawn:
                    if current_mole > random_num - 1:
                        break
                    print("mole", current_mole + 1, "spawned")
                    led_b.value(1)
                    mole_spawned = ticks_ms()
                    mole_despawn = mole_spawned + 2000
                    while True:
                        button_state_lb = button_lb.value()
                        button_state_rb = button_rb.value()
                        if ticks_ms() == mole_despawn:
                            print("mole", current_mole + 1, "despawned")
                            led_b.value(0)
                            current_mole += 1
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_lb == 1 and button_state_lb == 0:
                            print("a")
                            lcd1.clear()
                            lcd1.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd1.move_to(0, 1)
                            lcd1.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_1 = ticks_ms()
                            text_disappear_1 = text_appear_1 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_b.value(0)
                            current_mole += 1
                            player_1_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_rb == 1 and button_state_rb == 0:
                            print("a")
                            lcd2.clear()
                            lcd2.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd2.move_to(0, 1)
                            lcd2.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_2 = ticks_ms()
                            text_disappear_2 = text_appear_2 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_b.value(0)
                            current_mole += 1
                            player_2_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        button_state_before_lb = button_state_lb
                        button_state_before_rb = button_state_rb

            if which_button == 3:
                # Yellow mole position
                if text_disappear_1 == ticks_ms():
                    lcd1.clear()
                    lcd1.putstr(f"Stig {player_1_score}")
                    if current_mole > random_num - 1:
                        break
                if text_disappear_2 == ticks_ms():
                    lcd2.clear()
                    lcd2.putstr(f"Stig {player_2_score}")
                    if current_mole > random_num - 1:
                        break
                if ticks_ms() == mole_spawn:
                    if current_mole > random_num - 1:
                        break
                    print("mole", current_mole + 1, "spawned")
                    led_y.value(1)
                    mole_spawned = ticks_ms()
                    mole_despawn = mole_spawned + 2000
                    while True:
                        button_state_ly = button_ly.value()
                        button_state_ry = button_ry.value()
                        if ticks_ms() == mole_despawn:
                            print("mole", current_mole + 1, "despawned")
                            led_y.value(0)
                            current_mole += 1
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_ly == 1 and button_state_ly == 0:
                            print("a")
                            lcd1.clear()
                            lcd1.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd1.move_to(0, 1)
                            lcd1.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_1 = ticks_ms()
                            text_disappear_1 = text_appear_1 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_y.value(0)
                            current_mole += 1
                            player_1_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_ry == 1 and button_state_ry == 0:
                            print("a")
                            lcd2.clear()
                            lcd2.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd2.move_to(0, 1)
                            lcd2.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_2 = ticks_ms()
                            text_disappear_2 = text_appear_2 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_y.value(0)
                            current_mole += 1
                            player_2_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        button_state_before_ly = button_state_ly
                        button_state_before_ry = button_state_ry

            if which_button == 4:
                # White mole position
                if text_disappear_1 == ticks_ms():
                    lcd1.clear()
                    lcd1.putstr(f"Stig {player_1_score}")
                    if current_mole > random_num - 1:
                        break
                if text_disappear_2 == ticks_ms():
                    lcd2.clear()
                    lcd2.putstr(f"Stig {player_2_score}")
                    if current_mole > random_num - 1:
                        break
                if ticks_ms() == mole_spawn:
                    if current_mole > random_num - 1:
                        break
                    print("mole", current_mole + 1, "spawned")
                    led_w.value(1)
                    mole_spawned = ticks_ms()
                    mole_despawn = mole_spawned + 2000
                    while True:
                        button_state_lw = button_lw.value()
                        button_state_rw = button_rw.value()
                        if ticks_ms() == mole_despawn:
                            print("mole", current_mole + 1, "despawned")
                            led_w.value(0)
                            current_mole += 1
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_lw == 1 and button_state_lw == 0:
                            print("a")
                            lcd1.clear()
                            lcd1.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd1.move_to(0, 1)
                            lcd1.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_1 = ticks_ms()
                            text_disappear_1 = text_appear_1 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_w.value(0)
                            current_mole += 1
                            player_1_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        elif button_state_before_rw == 1 and button_state_rw == 0:
                            print("a")
                            lcd2.clear()
                            lcd2.putstr(f"{chr(0)}{chr(6)} hittir")
                            lcd2.move_to(0, 1)
                            lcd2.putstr(f"moldv{chr(7)}rpuna")
                            text_appear_2 = ticks_ms()
                            text_disappear_2 = text_appear_2 + 2000
                            print("mole", current_mole + 1, "despawned")
                            button_noise()
                            led_w.value(0)
                            current_mole += 1
                            player_2_score += 1
                            mole_despawn = ticks_ms()
                            mole_spawn = mole_despawn + randint(2500, 3500)
                            break
                        button_state_before_lw = button_state_lw
                        button_state_before_rw = button_state_rw

        # Round ended: evaluate scores and assign round win / punishments
        if player_1_score == player_2_score:
            # Players tied the round currently not possible
            lcd1.clear()
            lcd1.putstr(f"leikurinn enda{chr(1)}i")
            lcd2.clear()
            lcd2.putstr(f"{chr(0)}a{chr(1)} var")
            lcd1.move_to(0, 1)
            lcd1.putstr(f"jafntefli")  # tie message (Icelandic)
            lcd2.move_to(0, 1)
            lcd2.putstr(f"jafnteli")
            rounds_completed += 1

        elif player_1_score > player_2_score:
            # Player 1 won the round
            lcd1.clear()
            lcd1.putstr(f"{chr(0)}{chr(6)} vannst")  # you won the round
            lcd1.move_to(0, 1)
            lcd1.putstr(f"umfer{chr(1)}ina")
            lcd2.clear()
            lcd2.putstr(f"{chr(0)}{chr(6)} tapa{chr(1)}ir")  # you lost the round
            lcd2.move_to(0, 1)
            lcd2.putstr(f"umfer{chr(1)}inni")

            # Choose a punishment not yet used for player 1
            punishment_number = randint(0, 2)
            while punishment_number in player_1_punisments:
                punishment_number = randint(0, 2)
            player_1_punisments.append(punishment_number)
            punishment_list[punishment_number](lcd1)

            # Update player 1 score LEDs and wins
            p1_score_led[player_1_wins] = [50, 50, 50]
            p1_score_led.write()
            player_1_wins += 1
            rounds_completed += 1

        elif player_1_score < player_2_score:
            # Player 2 won the round
            lcd2.clear()
            lcd2.putstr(f"{chr(0)}{chr(6)} vannst")
            lcd2.move_to(0, 1)
            lcd2.putstr(f"umfer{chr(1)}ina")
            lcd1.clear()
            lcd1.putstr(f"{chr(0)}{chr(6)} tapa{chr(1)}ir")
            lcd1.move_to(0, 1)
            lcd1.putstr(f"umfer{chr(1)}inni")

            # Choose a punishment not yet used for player 2
            punishment_number = randint(0, 2)
            while punishment_number in player_2_punisments:
                punishment_number = randint(0, 2)
            player_2_punisments.append(punishment_number)
            punishment_list[punishment_number](lcd2)

            # Update player 2 score LEDs and wins
            p2_score_led[player_2_wins] = [50, 50, 50]
            p2_score_led.write()
            player_2_wins += 1
            rounds_completed += 1

    # Match finished: show final result on LCDs
    time.sleep(0.5)
    lcd1.clear()
    lcd2.clear()
    if player_1_wins == player_2_wins:
        # Players tied currently not possible
        print("t")
        lcd1.clear()
        lcd1.putstr(f"{chr(0)}a{chr(1)} var")
        lcd2.clear()
        lcd2.putstr(f"{chr(0)}a{chr(1)} var")
        lcd1.move_to(0, 1)
        lcd1.putstr(f"jafntefli")
        lcd2.move_to(0, 1)
        lcd2.putstr(f"jafnteli")
    elif player_1_wins > player_2_wins:
        # Player 1 wins the match
        print("1w")
        lcd1.clear()
        lcd1.putstr(f"{chr(0)}{chr(6)} vannst")
        lcd1.move_to(0, 1)
        lcd1.putstr(f"leikinn")
        lcd2.clear()
        lcd2.putstr(f"{chr(0)}{chr(6)} tapa{chr(1)}ir")
        lcd2.move_to(0, 1)
        lcd2.putstr(f"leikinn")
    elif player_1_wins < player_2_wins:
        # Player 2 wins the match
        print("2w")
        lcd1.clear()
        lcd2.clear()
        lcd1.putstr(f"{chr(0)}{chr(6)} tapa{chr(1)}ir")
        lcd1.move_to(0, 1)
        lcd1.putstr(f"leikinn")
        lcd2.putstr(f"{chr(0)}{chr(6)} vannst")
        lcd2.move_to(0, 1)
        lcd2.putstr(f"leikinn")
    sleep_ms(2000)