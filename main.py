import copy


# ==========================================
# ИСХОДНЫЕ ДАННЫЕ
# ==========================================

# Список процессов: название и время выполнения
PROCESSES = [
    {"name": "P1", "burst": 5},
    {"name": "P2", "burst": 3},
    {"name": "P3", "burst": 8},
    {"name": "P4", "burst": 2},
]

# Квант времени для Round Robin
TIME_QUANTUM = 2


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def calculate_statistics(processes):
    """Среднее время ожидания и среднее время завершения."""
    count = len(processes)
    average_waiting = sum(p["waiting"] for p in processes) / count
    average_completion = sum(p["completion"] for p in processes) / count
    return average_waiting, average_completion


def print_gantt_chart(gantt, title):
    """
    Выводит диаграмму Ганта в консоль.

    gantt — список кортежей (имя процесса, время начала, время окончания).
    Ширина ячейки подбирается динамически, чтобы двузначные и трёхзначные
    моменты времени не «съезжали».
    """
    print("\n" + "=" * 60)
    print(f"ДИАГРАММА ГАНТА: {title}")
    print("=" * 60)

    if not gantt:
        print("(нет данных)")
        return

    max_time = max(end for _, _, end in gantt)
    width = max(5, len(str(max_time)) + 2)

    # Строка названий процессов
    process_row = "".join(f"|{name:^{width}}" for name, _, _ in gantt) + "|"
    print(process_row)

    # Временная шкала: 0 и все моменты завершения
    time_row = str(gantt[0][1])
    for _, _, end in gantt:
        time_row += f"{end:>{width + 1}}"
    print(time_row + "\n")


# ==========================================
# АЛГОРИТМ FIFO
# ==========================================

def fifo_scheduler(processes):
    """
    FIFO: процессы выполняются в порядке поступления,
    каждый — до полного завершения.
    """
    tasks = copy.deepcopy(processes)

    current_time = 0
    gantt = []

    for process in tasks:
        start_time = current_time
        current_time += process["burst"]

        process["completion"] = current_time
        # Все процессы поступают в момент 0
        process["waiting"] = start_time

        gantt.append((process["name"], start_time, current_time))

    return tasks, gantt


# ==========================================
# АЛГОРИТМ SJF
# ==========================================

def sjf_scheduler(processes):
    """
    SJF (невытесняющий): первым выполняется процесс
    с наименьшим временем выполнения.
    """
    tasks = copy.deepcopy(processes)

    # Сортировка по времени выполнения
    tasks.sort(key=lambda p: p["burst"])

    current_time = 0
    gantt = []

    for process in tasks:
        start_time = current_time
        current_time += process["burst"]

        process["completion"] = current_time
        process["waiting"] = start_time

        gantt.append((process["name"], start_time, current_time))

    return tasks, gantt


# ==========================================
# АЛГОРИТМ ROUND ROBIN
# ==========================================

def round_robin_scheduler(processes, quantum):
    """
    Round Robin: каждому процессу выделяется квант времени.
    Незавершённые процессы возвращаются в конец очереди.

    Важно: очередь содержит ссылки на те же словари, что и tasks,
    поэтому результаты симуляции сразу попадают в итоговый список.
    """
    tasks = copy.deepcopy(processes)
    queue = []

    for process in tasks:
        process["remaining"] = process["burst"]
        process["waiting"] = 0
        process["completion"] = 0
        queue.append(process)  # ссылка на тот же объект, а не копия

    current_time = 0
    gantt = []

    while queue:
        process = queue.pop(0)

        execution_time = min(quantum, process["remaining"])
        start_time = current_time
        current_time += execution_time
        process["remaining"] -= execution_time

        gantt.append((process["name"], start_time, current_time))

        if process["remaining"] == 0:
            process["completion"] = current_time
            # arrival = 0, поэтому waiting = completion - burst
            process["waiting"] = process["completion"] - process["burst"]
        else:
            queue.append(process)

    # tasks сохраняет исходный порядок процессов
    return tasks, gantt


# ==========================================
# ВЫВОД РЕЗУЛЬТАТОВ
# ==========================================

def print_results(name, processes, gantt):
    """Печатает таблицу результатов и диаграмму Ганта для алгоритма."""
    print("\n" + "#" * 60)
    print(f"АЛГОРИТМ: {name}")
    print("#" * 60)

    print(
        f"{'Процесс':<12}"
        f"{'Время работы':<16}"
        f"{'Ожидание':<15}"
        f"{'Завершение':<15}"
    )
    print("-" * 60)

    for process in processes:
        print(
            f"{process['name']:<12}"
            f"{process['burst']:<16}"
            f"{process['waiting']:<15}"
            f"{process['completion']:<15}"
        )

    avg_waiting, avg_completion = calculate_statistics(processes)

    print("-" * 60)
    print(f"Среднее время ожидания: {avg_waiting:.2f}")
    print(f"Среднее время завершения: {avg_completion:.2f}")

    print_gantt_chart(gantt, name)

    return avg_waiting, avg_completion


# ==========================================
# СРАВНЕНИЕ АЛГОРИТМОВ
# ==========================================

def compare_algorithms():
    """Запускает три алгоритма и сравнивает их эффективность."""
    print("\n" + "=" * 60)
    print("       ИМИТАЦИОННОЕ МОДЕЛИРОВАНИЕ ПЛАНИРОВЩИКА")
    print("=" * 60)

    print("\nИсходные процессы:")
    for process in PROCESSES:
        print(f"{process['name']} - {process['burst']} единиц времени")

    print(f"\nКвант Round Robin: {TIME_QUANTUM}")

    fifo_result, fifo_gantt = fifo_scheduler(PROCESSES)
    fifo_stats = print_results("FIFO", fifo_result, fifo_gantt)

    sjf_result, sjf_gantt = sjf_scheduler(PROCESSES)
    sjf_stats = print_results("SJF", sjf_result, sjf_gantt)

    rr_result, rr_gantt = round_robin_scheduler(PROCESSES, TIME_QUANTUM)
    rr_stats = print_results("ROUND ROBIN", rr_result, rr_gantt)

    # Итоговая сравнительная таблица
    print("\n" + "=" * 60)
    print("СРАВНЕНИЕ ЭФФЕКТИВНОСТИ АЛГОРИТМОВ")
    print("=" * 60)

    print(
        f"{'Алгоритм':<18}"
        f"{'Среднее ожидание':<22}"
        f"{'Среднее завершение':<22}"
    )
    print("-" * 60)

    results = [
        ("FIFO", fifo_stats),
        ("SJF", sjf_stats),
        ("Round Robin", rr_stats),
    ]

    for name, stats in results:
        print(f"{name:<18}{stats[0]:<22.2f}{stats[1]:<22.2f}")

    best_algorithm = min(results, key=lambda item: item[1][0])

    print("-" * 60)
    print("\nНаименьшее среднее время ожидания у алгоритма:", best_algorithm[0])


# ==========================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==========================================

if __name__ == "__main__":
    compare_algorithms()