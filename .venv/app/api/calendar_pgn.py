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
        
        # Приводим к типу date, если это datetime
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

def create_calendar_plot(periods, min_date, max_date):
    # Создаём фигуру
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_title(f"Календарь периодов: {min_date.strftime('%B %Y')} — {max_date.strftime('%B %Y')}",
                 fontsize=16, pad=20)
    
    # Настраиваем оси
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 6)  # Максимум 6 недель в месяце
    ax.set_xticks(np.arange(0.5, 7.5))
    ax.set_yticks(np.arange(0.5, 6.5))
    ax.set_xticklabels(['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'])
    ax.grid(True, alpha=0.3)
    
    # Отключаем стандартные метки осей
    ax.tick_params(left=False, bottom=False)
    
    # Функция для отрисовки месяца
    def draw_month(year, month, offset_y):
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        ax.text(3.5, offset_y + 5.8, f"{month_name} {year}",
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                day_date = date(year, month, day)
                cell_center_x = day_idx + 0.5
                cell_center_y = offset_y - week_idx + 0.5
                
                # Проверяем, принадлежит ли дата какому‑либо периоду
                for period in periods:
                    if period['start'] <= day_date <= period['end']:
                        # Рисуем прямоугольник для периода
                        rect = Rectangle((day_idx, offset_y - week_idx), 1, 1,
                                      facecolor='lightblue', edgecolor='blue', alpha=0.7)
                        ax.add_patch(rect)
                        
                        # Добавляем номер периода
                        ax.text(cell_center_x, cell_center_y, str(period['number']),
                               ha='center', va='center', fontsize=8, fontweight='bold',
                               color='darkblue')
                        break
                else:
                    # Обычный день
                    ax.text(cell_center_x, cell_center_y, str(day),
                           ha='center', va='center', fontsize=9)
    
    # Рисуем месяцы в диапазоне
    current = min_date
    offset_y = 5  # Начальная позиция по Y
    while current <= max_date:
        draw_month(current.year, current.month, offset_y)
        offset_y -= 6  # Сдвигаем на 6 строк вниз для следующего месяца
        # Переходим к следующему месяцу
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    
    plt.tight_layout()
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
    fig, ax = create_calendar_plot(date_periods, min_date, max_date)
    
    # Шаг 6: Сохраняем
    output_path = f"calendar_report_{room_id}.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"Календарный отчёт успешно создан: {output_path}")
    return output_path

generate_calendar_report(room_id=1)