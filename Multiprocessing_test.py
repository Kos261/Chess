import threading
import time

def foo():
    while True:
        print('dupa')
        time.sleep(1)

def user_input():
    while True:
        user_text = input("Wpisz coś: ")
        print(f"Wpisałeś: {user_text}")

if __name__ == '__main__':
    # Tworzenie wątków
    thread_foo = threading.Thread(target=foo)
    thread_user_input = threading.Thread(target=user_input)

    # Uruchamianie wątków
    thread_foo.start()
    thread_user_input.start()

    # Oczekiwanie na zakończenie wątków (choć w praktyce te wątki będą działały w nieskończoność)
    thread_foo.join()
    thread_user_input.join()
