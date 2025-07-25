"""
Module for generating a school schedule
"""

import random
from collections import defaultdict
import json
from flask import Flask, render_template

app = Flask(__name__)

classes = [f"{i}{l}" for i in range(5, 12) for l in ['А', 'Б']]

LESSON_HOURS = [
    "08:30–09:15",
    "09:25–10:10",
    "10:20–11:05",
    "11:15–12:00",
    "12:10–12:55",
    "13:05–13:50",
    "14:00–14:45"
]

with open('programme.json', 'r', encoding='utf-8') as progr_file:
    progr = json.load(progr_file)
    programme = {}
    for cls in progr:
        programme[int(cls)] = progr[cls]

with open('teachers.json', 'r', encoding='utf-8') as teachers_file:
    teachers = json.load(teachers_file)

DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']
teacher_schedule = defaultdict(lambda: defaultdict(set))


def get_number_of_lessons(class_num):
    """
    Calculates the number of lessons per day for a given class.

    Args:
        class_num (int): The numeric part of the class name (e.g., 5, 6, 7, etc.).

    Returns:
        dict: A dictionary where keys are weekdays ('Пн', 'Вт', ...) and values are
              the number of lessons scheduled for that day.

    Description:
        The total number of weekly lessons (based on the class's curriculum) is evenly distributed
        across the 5 weekdays. If the number of lessons doesn't divide evenly, the remaining lessons
        are randomly assigned to the days.
    """
    number_of_lessons = {}
    for day in DAYS:
        number_of_lessons[day] = sum(programme[class_num].values()) // 5
    for _ in range(sum(programme[class_num].values()) % 5):
        day = random.choice(DAYS)
        number_of_lessons[day] += 1
    return number_of_lessons


def generate_schedule_for_class(class_name):
    """
    Generates a weekly timetable for a specific class.

    Args:
        class_name (str): The full name of the class (e.g., '7А', '9Б').

    Returns:
        dict or None: A dictionary representing the class's schedule with weekdays as keys
                      and lists of (subject, teacher) tuples as values. Returns None if a valid
                      schedule could not be generated after multiple attempts.

    Description:
        - Distributes subjects according to their weekly hour requirements.
        - Ensures subjects are not repeated too often (e.g., most only once per day, some twice).
        - Prevents placing certain subjects in the last lesson slot of the day.
        - Avoids teacher conflicts by checking if a teacher is already assigned during a time slot.
        - Attempts to generate a valid schedule up to 100 times before failing.
    """
    class_num = int(class_name[:-1])
    subjects = programme[class_num]

    subject_pool = []
    for subject, hours in subjects.items():
        subject_pool.extend([subject] * hours)

    repeatable_subjects = {'алгебра', 'геометрія'}
    forbidden_last_slot_subjects = {'алгебра', 'геометрія'}
    max_attempts = 100

    for _ in range(max_attempts):
        random.shuffle(subject_pool)
        number_of_lessons = get_number_of_lessons(class_num)
        schedule = {day: [None] * number_of_lessons[day] for day in DAYS}
        local_teacher_schedule = defaultdict(lambda: defaultdict(set))
        success = True

        for subject in subject_pool:
            placed = False
            for day in DAYS:
                day_lessons = number_of_lessons[day]
                existing_count = sum(1 for s in schedule[day] if s is not None and s[0] == subject)

                if class_num >= 9 and subject in repeatable_subjects:
                    if existing_count >= 2:
                        continue
                else:
                    if existing_count >= 1:
                        continue

                for slot in range(day_lessons):
                    if subject in forbidden_last_slot_subjects and slot == day_lessons - 1:
                        continue
                    if schedule[day][slot] is None:
                        for teacher in random.sample(teachers[subject], len(teachers[subject])):
                            if slot not in teacher_schedule[teacher][day] and \
                                (slot not in local_teacher_schedule[teacher][day]):
                                schedule[day][slot] = (subject, teacher)
                                local_teacher_schedule[teacher][day].add(slot)
                                placed = True
                                break
                    if placed:
                        break
                if placed:
                    break

            if not placed:
                success = False
                break

        if success and all(None not in schedule[day] for day in DAYS):
            for teacher, dayslots in local_teacher_schedule.items():
                for day, slots in dayslots.items():
                    teacher_schedule[teacher][day].update(slots)
            return schedule

    return None


@app.route('/')
def home():
    """
    Flask route for the homepage that generates and displays schedules for all classes.

    Returns:
        str: Rendered HTML template 'schedule.html' containing the complete schedule for all classes

    Description:
        - Clears the teacher schedule to start fresh.
        - Iterates over all classes and attempts to generate a schedule for each.
        - If any class fails to generate a schedule, the whole process restarts.
        - If successful, renders the schedule along with weekdays and lesson time slots.
    """
    while True:
        all_schedule = {}
        teacher_schedule.clear()
        success = True

        for cl in classes:
            schedule = generate_schedule_for_class(cl)
            if schedule is None:
                success = False
                break
            all_schedule[cl] = schedule

        if success:
            return render_template('schedule.html', all_schedule=all_schedule,\
                                    days=DAYS, lesson_hours = LESSON_HOURS)


if __name__ == '__main__':
    app.run(debug=True)
