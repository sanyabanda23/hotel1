import matplotlib.pyplot as plt
import calendar
import numpy as np
from matplotlib.patches import Rectangle
from datetime import datetime, date, timedelta
from app.dao.dao import BookingDAO
from app.dao.database import async_session_maker

def normalize_dates(periods):
    normalized = []
    for period in periods:
        start = period['start']
        end = period['end']

        if isinstance(start, datetime):
            start = start.date()
        if isinstance(end, datetime):
            end = end.date()

        normalized.append({
            'start': start,
            'end': end,
            'number': period['number']
        })
    return normalized

def create_calendar_plot(periods, min_date, max_date, room_id):
    if not periods:
        raise ValueError("Список периодов пуст — невозможно построить календарь")

    # Рассчитываем количество месяцев
    num_months = ((max_date.year - min_date.year) * 12 +
                 (max_date.month - min_date.month) + 1)

    # Ширина: 3 месяца в ряд, высота зависит от количества рядов
    months_per_row = 3
    rows = (num_months + months_per_row - 1) // months_per_row
    fig_width = 3  # фиксированная ширина для 3 месяцев
    fig_height = rows * 3  # 3 дюйма на ряд месяцев

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Отключаем оси
    ax.axis('off')

    # Добавляем общий заголовок для всего календаря
    fig.suptitle(f"Календарь комнаты №{room_id}",
                fontsize=20,
                fontweight='bold',
                y=0.7)  # позиция по вертикали (0.98 — близко к верхнему краю)

    # Функция для отрисовки месяца в сетке
    def draw_month_in_grid(year, month, grid_x, grid_y):
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]

        # Позиция месяца в сетке (каждый месяц занимает область 2.5x2.5)
        x_offset = grid_x * 1.1
        y_offset = (rows - 1 - grid_y) * 1.1

        # Заголовок месяца над календарём
        ax.text(x_offset + 0.3, y_offset + 0.4, f"{month_name} {year}",
                ha='center', va='center', fontsize=14, fontweight='bold')
        
        # Дни недели над календарём месяца
        for d, day_name in enumerate(['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']):
            ax.text(x_offset + d * 0.13, y_offset + 0.30, day_name,
                    ha='center', va='center', fontsize=14, fontweight='bold', color='darkblue')

        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue

                day_date = date(year, month, day)
                cell_x = x_offset + day_idx * 0.13
                cell_y = y_offset + (2.5 - week_idx) * 0.1  # инвертируем недели

                # Флаг: нашли ли период для этой даты
                found_period = False

                # Проверяем все периоды для текущей даты
                for period in periods:
                    if period['start'] <= day_date <= period['end']:
                        
                        # Оставляем дату, но делаем её более заметной
                        ax.text(
                                cell_x,
                                cell_y,
                                str(day),
                                ha='center',
                                va='center',
                                fontsize=14,
                                fontweight='bold',
                                color='darkred'
                                )
                        found_period = True
                        break

                # Если период не найден, отображаем дату обычным цветом
                if not found_period:
                    ax.text(
                cell_x,
                cell_y,
                str(day),
                ha='center',
                va='center',
                fontsize=14,
                color='black'
            )

    # Рисуем месяцы в сетке 3×N
    current = min_date
    grid_x, grid_y = 0, 0

    while current <= max_date:
        draw_month_in_grid(current.year, current.month, grid_x, grid_y)

        # Переходим к следующему месту в сетке
        grid_x += 1
        if grid_x >= 3:  # 3 месяца в ряду
            grid_x = 0
            grid_y += 1

        # Переходим к следующему месяцу
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    # Настройка отступов
    plt.subplots_adjust(
        left=0.06,
        right=0.94,
        top=0.95,
        bottom=0.10,
        hspace=0.6,
        wspace=0.4
    )

    return fig, ax

async def generate_calendar_report(room_id: int):
    """
    Генерирует календарный отчёт с отмеченными периодами из результатов find_all.
    """
    # Шаг 1: Получаем данные
    async with async_session_maker() as session:
        records = await BookingDAO(session).get_bookings_with_details(room_id)

    # Шаг 2: Извлекаем периоды
    date_periods = []
    for record in records:
        if hasattr(record[0], 'date_start') and hasattr(record[0], 'date_end') and hasattr(record[0], 'id'):
            date_periods.append({
                'start': record[0].date_start,
                'end': record[0].date_end,
                'number': record[0].id
            })

    if not date_periods:
        raise ValueError("Не найдено записей с датами для построения календаря")

    # Шаг 3: Нормализуем даты
    date_periods = normalize_dates(date_periods)

    # Шаг 4: Определяем границы
    min_date = min(p['start'] for p in date_periods) - timedelta(weeks=1)
    max_date = max(p['end'] for p in date_periods) + timedelta(weeks=1)

    # Шаг 5: Строим график
    fig, ax = create_calendar_plot(date_periods, min_date, max_date, room_id)

    # Шаг 6: Сохраняем
    output_path = f"calendar_report_{room_id}.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"Календарный отчёт успешно создан: {output_path}")
    return output_path