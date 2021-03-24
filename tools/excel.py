import json

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


def parse_groups(workbook, workbook_number) -> dict:
    sheet_names = workbook.sheetnames
    groups = {}
    for sheet_number in range(len(sheet_names)):  # Цикл по листам
        start_col, end_col = ord('C'), ord('E')
        sheet = workbook[sheet_names[sheet_number]]
        for group_number in sheet_names[sheet_number].split(','):  # Цикл про группам
            # print('\n\n' + group_number + '\n\n')
            groups[group_number] = {}
            if workbook_number in (1, 2):
                start_row = 9 if sheet_number == 1 else 8
            else:
                start_row = 8
            for weekday in range(6):  # 6 дней недели
                pair = 1
                groups[group_number][weekday] = ''
                for rows in range(start_row, start_row + (7 if workbook_number == 4 else 6)):  # Берем по 6 пар
                    cells = sheet[f'{chr(start_col)}{rows}:{chr(end_col)}{rows}']
                    for cell_obj in cells:
                        if weekday == 5:
                            string = LESSONS_SATURDAY[pair] + ' - '
                        else:
                            string = LESSONS_DAILY[pair] + ' - '
                        string += ' - '.join([str(cell.value).replace('\n', '|').replace(' /', '/') for cell in cell_obj])
                        string = string.replace(' - None', '')
                        groups[group_number][weekday] += string + '\n'
                        # print(string)
                    pair += 1
                # print()
                start_row += 6
            start_col = end_col + 1
            end_col = start_col + 2
    return groups


def main():
    groups = {}
    for i in range(1, 5):
        workbook = openpyxl.load_workbook(f'../workbooks/rasp{i}.xlsx')
        groups.update(parse_groups(workbook, i))
    with open('test1.json', mode='w', encoding='utf8') as file:
        json.dump(groups, file, ensure_ascii=False)


if __name__ == '__main__':
    main()
