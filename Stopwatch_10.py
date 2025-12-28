


"""PROD. BY DIXIT"""



import time
import os
import sys
import msvcrt


class CompactStopwatch:
    def __init__(self):
        self.running = False
        self.start_time = 0
        self.elapsed = 0.0
        self.laps = []

        # ИЗМЕНЕНО: Точный размер окна под интерфейс (37x25 для правильного отображения)
        self.width = 37  # 37 символов для учета вертикальных границ
        self.height = 25  # 25 строк для полного отображения

        # Для защиты от сворачивания
        self.last_valid_screen = time.time()
        self.screen_corrupted = False

        # Оптимизация и тайминги
        self.performance_counter = time.perf_counter
        self.last_counter = 0
        self.last_update = 0
        self.update_interval = 0.1  # 10 обновлений в секунду

        # НОВОЕ: Быстрый режим
        self.fast_mode = False
        self.fast_mode_interval = 0.01  # 100 обновлений в секунду

        # НОВОЕ: Цвета интерфейса
        self.color_index = 0
        self.colors = {
            "Белый": "\033[37m",
            "Оранжевый": "\033[38;5;214m",  # Яркий оранжевый
            "Желтый": "\033[33m",
            "Зеленый": "\033[32m",
            "Голубой": "\033[36m",
            "Синий": "\033[34m",
            "Фиолетовый": "\033[35m"
        }
        self.current_color = "\033[37m"
        self.color_names = list(self.colors.keys())

        # Windows настройки
        if os.name == 'nt':
            os.system('chcp 65001 > nul')
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass  # Если не удалось настроить консоль, продолжаем

    def clear_screen(self):
        os.system('cls')

    def check_screen_corruption(self):
        """Проверяет, не было ли окно свёрнуто/развёрнуто"""
        current_time = time.time()
        if current_time - self.last_valid_screen > 2.0 and self.running:
            self.screen_corrupted = True

    def repair_screen(self):
        """Восстанавливает экран после сворачивания"""
        self.clear_screen()
        self.draw_complete_border()
        self.update_time()
        self.update_status()
        self.update_laps()
        self.screen_corrupted = False
        self.last_valid_screen = time.time()

    def draw_complete_border(self):
        sys.stdout.write("\033[0;0H")

        # Используем текущий цвет для всей отрисовки
        sys.stdout.write(self.current_color)

        print("╔═══════════════════════════════╗")  # 37 символов
        print("║     СЕКУНДОМЕР v10.0          ║")
        print("╠═══════════════════════════════╣")
        print("║                               ║")
        print("║        Время:                 ║")
        print("║                               ║")
        print("╠═══════════════════════════════╣")
        print("║        Статус:                ║")  # Строка 8
        print("║                               ║")  # Строка 9 - здесь будет статус
        print("╠═══════════════════════════════╣")
        print("║       Управление:             ║")
        print("║                               ║")
        print("║                               ║")
        print("║                               ║")  # НОВАЯ строка для дополнительных опций
        print("╠═══════════════════════════════╣")
        print("║     Последние круги:          ║")

        for _ in range(5):
            print("║                               ║")

        print("╚═══════════════════════════════╝")

        # Управление (с текущим цветом)
        sys.stdout.write("\033[11;6H")
        print("[S] Старт/Стоп")

        sys.stdout.write("\033[12;6H")
        print("[L] Круг")

        sys.stdout.write("\033[13;6H")  # НОВАЯ строка
        print("[F] Быстрый режим")

        sys.stdout.write("\033[11;22H")
        print("[R] Сброс")

        sys.stdout.write("\033[12;22H")
        print("[Q] Выход")

        sys.stdout.write("\033[13;22H")  # НОВАЯ строка
        print("[C] Цвет")

    def update_time(self):
        # Время должно рассчитываться на основе текущего времени, а не накапливать ошибки
        if self.running:
            # Только если запущено, обновляем elapsed
            current_counter = self.performance_counter()
            self.elapsed = current_counter - self.start_time

        hours = int(self.elapsed // 3600)
        minutes = int((self.elapsed % 3600) // 60)
        seconds = int(self.elapsed % 60)
        centiseconds = int((self.elapsed * 100) % 100)

        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

        sys.stdout.write(self.current_color)
        sys.stdout.write("\033[6;13H")
        sys.stdout.write(" " * 13)
        sys.stdout.write("\033[6;13H")
        sys.stdout.write(time_str)

        # ИСПРАВЛЕНО: Убираем лишнюю правую границу - она уже есть от оригинальной отрисовки
        sys.stdout.flush()

    def update_status(self):
        sys.stdout.write(self.current_color)
        sys.stdout.write("\033[9;2H")
        sys.stdout.write(" " * 34)  # Очищаем всю строку внутри границ

        sys.stdout.write("\033[9;13H")  # Возвращаемся к позиции статуса

        if self.running:
            status = "> ЗАПУЩЕН"
            if self.fast_mode:
                status += " (БЫСТР)"
        else:
            status = "|| ОСТАНОВЛЕН"
            if self.fast_mode:
                status += " (БЫСТР)"

        sys.stdout.write(status)

        # ИСПРАВЛЕНО: Убираем лишнюю правую границу - она уже есть от оригинальной отрисовки
        sys.stdout.flush()

    def format_time_difference(self, diff):
        diff_hours = int(diff // 3600)
        diff_minutes = int((diff % 3600) // 60)
        diff_seconds = int(diff % 60)
        diff_centiseconds = int((diff * 100) % 100)

        if diff_hours > 0:
            return f" +{diff_hours:02d}:{diff_minutes:02d}:{diff_seconds:02d}.{diff_centiseconds:02d}"
        elif diff_minutes > 0:
            return f" +{diff_minutes:02d}:{diff_seconds:02d}.{diff_centiseconds:02d}"
        else:
            return f" +{diff_seconds:02d}.{diff_centiseconds:02d}"

    def update_laps(self):
        for i in range(5):
            sys.stdout.write(self.current_color)
            sys.stdout.write(f"\033[{17 + i};4H")
            sys.stdout.write(" " * 29)

        if not self.laps:
            sys.stdout.flush()
            return

        display_laps = self.laps[-5:]
        num_laps = len(display_laps)

        for i in range(num_laps):
            row = 17 + (4 - i)
            lap_idx = len(self.laps) - num_laps + i

            lap_time = self.laps[lap_idx]
            hours = int(lap_time // 3600)
            minutes = int((lap_time % 3600) // 60)
            seconds = int(lap_time % 60)
            centiseconds = int((lap_time * 100) % 100)

            lap_num = f"{lap_idx + 1:2d}"
            if lap_idx == len(self.laps) - 1:
                lap_num = f">{lap_num}"
            else:
                lap_num = f" {lap_num}"

            lap_str = f"{lap_num}: {hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

            if lap_idx > 0:
                prev_lap_time = self.laps[lap_idx - 1]
                diff = lap_time - prev_lap_time
                diff_str = self.format_time_difference(diff)

                if len(lap_str) + len(diff_str) <= 29:
                    lap_str = lap_str + diff_str

            sys.stdout.write(self.current_color)
            sys.stdout.write(f"\033[{row};4H")
            sys.stdout.write(lap_str.ljust(29))

        sys.stdout.flush()

    def show_message(self, message, duration=1.5):
        sys.stdout.write(self.current_color)
        sys.stdout.write(f"\033[{self.height - 2};4H")
        sys.stdout.write(" " * 33)
        sys.stdout.write(f"\033[{self.height - 2};4H")
        sys.stdout.write(message)
        sys.stdout.flush()

        self.message_time = time.time()
        self.message_text = message

    def clear_old_message(self):
        if hasattr(self, 'message_time'):
            if time.time() - self.message_time > 1.5:
                sys.stdout.write(f"\033[{self.height - 2};4H")
                sys.stdout.write(" " * 33)
                sys.stdout.flush()
                delattr(self, 'message_time')
                delattr(self, 'message_text')

    def get_key(self):
        if not msvcrt.kbhit():
            return None

        key = msvcrt.getch()

        # Упрощенная обработка клавиш
        if key in [b's', b'S']:
            return 'start_stop'
        elif key in [b'l', b'L']:
            return 'lap'
        elif key in [b'r', b'R']:
            return 'reset'
        elif key in [b'q', b'Q']:
            return 'quit'
        elif key in [b'f', b'F']:
            return 'fast_toggle'
        elif key in [b'c', b'C']:
            return 'color_change'

        return None

    def toggle_fast_mode(self):
        """Переключает быстрый режим"""
        self.fast_mode = not self.fast_mode

        # НЕ влияем на точность времени! Только на частоту обновления экрана
        if self.fast_mode:
            self.show_message(f"Быстрый режим: {1 / self.fast_mode_interval:.0f} FPS")
        else:
            self.show_message(f"Нормальный режим: {1 / self.update_interval:.0f} FPS")

        self.update_status()

    def change_color(self):
        """Меняет цвет интерфейса"""
        self.color_index = (self.color_index + 1) % len(self.color_names)
        color_name = self.color_names[self.color_index]
        self.current_color = self.colors[color_name]

        # Перерисовываем весь интерфейс с новым цветом
        self.clear_screen()
        self.draw_complete_border()
        self.update_time()
        self.update_status()
        self.update_laps()
        self.show_message(f"Цвет: {color_name}")

    def process_action(self, action):
        if action == 'start_stop':
            if not self.running:
                self.running = True
                self.start_time = self.performance_counter() - self.elapsed
                self.last_counter = self.performance_counter()
                self.show_message("Старт!")
            else:
                self.running = False
                self.show_message("Стоп!")
            self.update_status()
            return True

        elif action == 'lap':
            if self.running:
                self.laps.append(self.elapsed)
                self.update_laps()
                self.show_message(f"Круг {len(self.laps)} записан!")
            else:
                self.show_message("Сначала запустите секундомер!")
            return True

        elif action == 'reset':
            self.running = False
            self.elapsed = 0.0
            self.start_time = 0
            self.laps = []
            self.update_time()
            self.update_status()
            self.update_laps()
            self.show_message("Сброшено!")
            return True

        elif action == 'fast_toggle':
            self.toggle_fast_mode()
            return True

        elif action == 'color_change':
            self.change_color()
            return True

        elif action == 'quit':
            return 'quit'

        return False

    def run(self):
        # ИЗМЕНЕНО: Точная установка размера окна
        if os.name == 'nt':
            os.system(f'mode con: cols={self.width} lines={self.height}')

        self.clear_screen()
        self.draw_complete_border()
        self.update_time()
        self.update_status()
        self.update_laps()

        # self.show_message("Готов к работе. [F] - быстрый режим, [C] - цвет")

        last_counter = self.performance_counter()
        #Сдесь Был Иван Бычков И Алекс Гаврилов. Пусть это послание сделает нашу сверх державу айти гигантом!!! Вперед за качественным продуктом
        try:
            while True:
                current_counter = self.performance_counter()

                if self.running:
                    self.check_screen_corruption()

                if self.screen_corrupted:
                    self.repair_screen()

                # Определяем интервал обновления в зависимости от режима
                current_interval = self.fast_mode_interval if self.fast_mode else self.update_interval

                # Обновляем экран с нужной частотой
                if current_counter - self.last_update >= current_interval:
                    self.update_time()
                    self.last_update = current_counter
                    self.last_valid_screen = current_counter

                last_counter = current_counter

                # Обработка ввода
                try:
                    action = self.get_key()
                    if action:
                        result = self.process_action(action)
                        if result == 'quit':
                            break
                        self.last_valid_screen = time.time()
                except:
                    pass

                self.clear_old_message()

                # Рассчитываем время сна для экономии ресурсов
                # ИСПРАВЛЕНО: время сна как в условии
                if self.fast_mode:
                    time_to_sleep = 0.01  # Быстрый режим
                else:
                    time_to_sleep = 0.1  # Обычный режим

                time.sleep(time_to_sleep)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            try:
                self.clear_screen()
                print(f"Ошибка: {e}")
                print("Пытаюсь восстановить...")
                time.sleep(2)
                self.repair_screen()
                self.running = False
                self.update_status()
            except:
                pass
        finally:
            # Сбрасываем цвет перед выходом
            sys.stdout.write("\033[0m")
            self.clear_screen()
            print("Секундомер завершил работу.")


def main():
    stopwatch = CompactStopwatch()
    stopwatch.run()


if __name__ == "__main__":
    main()