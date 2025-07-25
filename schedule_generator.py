from flask import Flask, render_template
import random
from collections import defaultdict

app = Flask(__name__)

classes = [f"{i}{l}" for i in range(5, 12) for l in ['А', 'Б']]

programme = {
    5: {
        'матем': 5, 'укр_мова': 4, 'укр_літ': 2, 'англ': 3, 'історія': 2,
        'природ': 2, 'фізра': 3, 'мистецтво': 2, 'труд': 1, 'інформатика': 1
    },
    6: {
        'матем': 5, 'укр_мова': 3, 'укр_літ': 2, 'англ': 3, 'історія': 2,
        'природ': 2, 'фізра': 3, 'мистецтво': 1, 'труд': 1, 'інформатика': 1
    },
    7: {
        'алг': 3, 'геом': 2, 'укр_мова': 2, 'укр_літ': 2, 'англ': 3, 'історія': 2,
        'біологія': 2, 'фізика': 2, 'географія': 1, 'фізра': 3,
        'мистецтво': 1, 'труд': 1, 'інформатика': 1
    },
    8: {
        'алг': 3, 'геом': 2, 'укр_мова': 2, 'укр_літ': 2, 'англ': 3,
        'іст_укр': 1, 'іст_світ': 1, 'біологія': 2, 'фізика': 2,
        'хімія': 2, 'географія': 1, 'фізра': 3, 'труд': 1, 'інформатика': 1
    },
    9: {
        'алг': 3, 'геом': 2, 'укр_мова': 2, 'укр_літ': 2, 'англ': 3,
        'іст_укр': 1, 'іст_світ': 1, 'біологія': 2, 'фізика': 2,
        'хімія': 2, 'географія': 1, 'здоров’я': 1, 'фізра': 3,
        'труд': 1, 'інформатика': 1
    },
    10: {
        'укр_мова': 2, 'укр_літ': 2, 'англ': 3, 'алг': 4, 'геом': 3,
        'іст_укр': 2, 'іст_світ': 1, 'біологія': 2, 'фізика': 2,
        'хімія': 2, 'географія': 1, 'захист_укр': 1, 'фізра': 3,
        'інформатика': 1, 'право': 1
    },
    11: {
        'укр_мова': 2, 'укр_літ': 2, 'англ': 3, 'алг': 4, 'геом': 3,
        'іст_укр': 2, 'іст_світ': 1, 'біологія': 1, 'фізика': 1,
        'хімія': 1, 'географія': 1, 'захист_укр': 1, 'фізра': 3,
        'інформатика': 1, 'право': 2
    }
}

teachers = {
    'матем': ['Ірина Петрівна', 'Галина Степанівна', 'Світлана Василівна'],
    'англ': ['Марта Василівна', 'Олег Ігорович', 'Тетяна Вікторівна'],
    'укр_мова': ['Оксана Іванівна', 'Марія Михайлівна', 'Лідія Степанівна'],
    'укр_літ': ['Оксана Іванівна', 'Марія Михайлівна', 'Лідія Степанівна'],
    'історія': ['Ірина Вікторівна', 'Ганна Іллівна'],
    'алг': ['Світлана Василівна', 'Галина Степанівна', 'Ірина Петрівна'],
    'геом': ['Світлана Василівна', 'Галина Степанівна', 'Ірина Петрівна'],
    'природ': ['Леся Віталіївна'],
    'біологія': ['Олена Степанівна'],
    'фізика': ['Інна Анатоліївна', 'Олег Олексійович', 'Марія Воломирівна'],
    'географія': ['Марина Сергіївна', 'Ігор Миколайович'],
    'інформатика': ['Тетяна Максимівна', 'Олена Юріївна'],
    'труд': ['Андрій Петрович', 'Марина Сергіївна'],
    'мистецтво': ['Катерина Олександрівна'],
    'здоров’я': ['Ірина Вікторівна'],
    'іст_укр': ['Юрій Миколайович', 'Людмила Іванівна', 'Марія Ярославівна'],
    'іст_світ': ['Ірина Вікторівна', 'Людмила Іванівна', 'Ганна Іллівна'],
    'право': ['Олег Ігорович'],
    'захист_укр': ['Петро Дмитрович'],
    'фізра': ['Олексій Андрійович', 'Юрій Олегович'],
    'хімія': ['Ірина Вікторівна', 'Галина Ігорівна', 'Максим Богданович']}

DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']
teacher_schedule = defaultdict(lambda: defaultdict(set))

def get_number_of_lessons(class_num):
    number_of_lessons = {}
    for day in DAYS:
        number_of_lessons[day] = sum(programme[class_num].values()) // 5
    for _ in range(sum(programme[class_num].values()) % 5):
        day = random.choice(DAYS)
        number_of_lessons[day] += 1
    return number_of_lessons

def generate_schedule_for_class(class_name):
    class_num = int(class_name[:-1])
    subjects = programme[class_num]

    subject_pool = []
    for subject, hours in subjects.items():
        subject_pool.extend([subject] * hours)

    repeatable_subjects = {'алг', 'геом', 'алг_геом'}
    max_attempts = 20

    for _ in range(max_attempts):
        random.shuffle(subject_pool)
        number_of_lessons = get_number_of_lessons(class_num)
        schedule = {day: [None]*number_of_lessons[day] for day in DAYS}
        local_teacher_schedule = defaultdict(lambda: defaultdict(set))
        success = True

        for subject in subject_pool:
            placed = False
            for day in DAYS:
                existing_count = sum(1 for s in schedule[day] if s is not None and s[0] == subject)

                if class_num >= 9 and subject in repeatable_subjects:
                    if existing_count >= 2:
                        continue
                else:
                    if existing_count >= 1:
                        continue

                for slot in range(number_of_lessons[day]):
                    if schedule[day][slot] is None:
                        for teacher in random.sample(teachers[subject], len(teachers[subject])):
                            if slot not in teacher_schedule[teacher][day] and slot not in local_teacher_schedule[teacher][day]:
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

        if success:
            for teacher, dayslots in local_teacher_schedule.items():
                for day, slots in dayslots.items():
                    teacher_schedule[teacher][day].update(slots)
            return schedule

    return schedule



@app.route('/')
def home():
    all_schedule = {}
    teacher_schedule.clear()  # обнуляємо перед новою генерацією
    for cl in classes:
        all_schedule[cl] = generate_schedule_for_class(cl)
    return render_template('schedule.html', all_schedule=all_schedule, days=DAYS)

if __name__ == '__main__':
    app.run(debug=True)

# all_schedule = {}
# for cl in classes:
#     all_schedule[cl] = generate_schedule_for_class(cl)
# print(all_schedule)
