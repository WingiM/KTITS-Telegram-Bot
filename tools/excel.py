import openpyxl

LESSONS_DAILY = {
    1: '8:00-9:30',
    2: '9:40-11:10',
    3: '11:50-13:20',
    4: '13:20-15:10',
    5: '15:20-16:50',
    6: '17:00-18:30',
    7: '18:40-20:10',
}

LESSONS_SATURDAY = {
    1: '8:00-9:30',
    2: '9:40-11:10',
    3: '11:30-13:00',
    4: '13:10-14:40',
    5: '14:50-16:20',
    6: '16:30-18:00',
    7: '18:00-19:30'
}


def groups_parse(cells, pair, weekday):
    for cell_obj in cells:
        if weekday == 5:
            string = '•' + LESSONS_SATURDAY[pair] + ' - '
        else:
            string = '•' + LESSONS_DAILY[pair] + ' - '
        string += ' - '.join([str(cell.value).replace('\n', '|').replace(' /', '/') for cell in cell_obj])
        string = string.replace(' - None', '')
    return string


def parse_teachers(cells, pair, weekday, group):
    t_pairs = {}
    teachers = cells[0][2].value
    if not teachers:
        return {}
    c = 0
    for teacher_pairs in teachers.split('\n'):
        pairs = cells[0][1].value.split('\n')
        for teacher in (teacher_pairs.split('/') if '/' in teacher_pairs else teacher_pairs.split('\\')):
            t_pairs[teacher.strip()] = t_pairs.get(teacher, {})
            t_pairs[teacher.strip()][weekday] = []
            if len(pairs) == len(teachers.split('\n')) > 1:
                t_pairs[teacher.strip()][weekday].append(
                    '•' + (LESSONS_DAILY[pair] if weekday != 5 else LESSONS_SATURDAY[pair]) + ' - Группа ' + str(
                        group) + ' - Аудитория ' + '/'.join(str(cells[0][0].value).split('\n')) + ' - ' + pairs[
                        c].strip() + (' - До пересменки' if c == 0 else ' - После пересменки'))
            else:
                t_pairs[teacher.strip()][weekday].append(
                    '•' + (LESSONS_DAILY[pair] if weekday != 5 else LESSONS_SATURDAY[pair]) + ' - Группа ' + str(
                        group) + ' - Аудитория ' + '/'.join(str(cells[0][0].value).split('\n')) + ' - ' + pairs[
                        0].strip())
        c += 1
    return t_pairs


def parse_groups(workbook, workbook_number):
    sheet_names = workbook.sheetnames
    groups = {}
    teachers = {}
    for sheet_number in range(len(sheet_names)):  # Цикл по листам
        start_col, end_col = ord('C'), ord('E')
        sheet = workbook[sheet_names[sheet_number]]
        for group_number in sheet_names[sheet_number].split(','):  # Цикл про группам
            # print('\n\n' + group_number + '\n\n')
            groups[group_number] = {}
            if workbook_number in (1, 2):
                start_row = 8 if sheet_number == 0 else 7
            else:
                start_row = 7
            for weekday in range(6):  # 6 дней недели
                pair = 1
                groups[group_number][weekday] = ''
                for rows in range(start_row, start_row + (7 if workbook_number == 4 else 6)):  # Берем по 6 пар
                    cells = sheet[f'{chr(start_col)}{rows}:{chr(end_col)}{rows}']
                    groups[group_number][weekday] += groups_parse(cells, pair, weekday) + '\n\n'
                    t_pairs = parse_teachers(cells, pair, weekday, group_number)
                    for name in t_pairs:
                        teachers[name] = teachers.get(name, {})
                        teachers[name][weekday] = teachers[name].get(weekday, [])
                        for p in t_pairs[name][weekday]:
                            teachers[name][weekday].append(p + '\n')
                        # if name == 'Петрова А.Р.':
                        #     print(teachers['Петрова А.Р.'])
                    pair += 1
                start_row += 6
            start_col = end_col + 1
            end_col = start_col + 2
    return groups, teachers


def main():
    groups = {}
    teachers = {}
    for i in range(1, 5):
        workbook = openpyxl.load_workbook(f'workbooks/rasp{i}.xlsx')
        group_dict, teacher_dict = parse_groups(workbook, i)
        groups.update(group_dict)
        for teacher in teacher_dict:
            for weekday in teacher_dict[teacher]:
                teachers[teacher] = teachers.get(teacher, {})
                teachers[teacher][weekday] = teachers[teacher].get(weekday, []) + teacher_dict[teacher][weekday]
    return groups, teachers
