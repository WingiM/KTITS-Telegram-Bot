import json

import openpyxl

wb = openpyxl.load_workbook("../workbooks/rasp1.xlsx")
sheet_names = wb.sheetnames

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
    6: '16:30-18:00'
}


def parse(start_col="C", end_col="E", sheet_number=0):
    one_sheet_lessons = {}
    start_col_ord, end_col_ord = ord(start_col), ord(end_col)
    group_number = 100
    lesson_num = 1
    sheet = wb[sheet_names[sheet_number]]
    while start_col_ord <= ord("R"):
        return_dict = {}
        temp_lessons = []
        a = 8 if sheet_number == 0 else 7
        while a <= 43:
            for i in range(a, a + 6):
                for cell_obj in sheet[f"{chr(start_col_ord)}{i}:{chr(end_col_ord)}{i}"]:
                    lesson = ""
                    for cell in cell_obj:
                        if cell.value is None:
                            break
                        lesson += f"{str(cell.value)} "
                    temp_new_line_str_1 = r"\n"
                    temp_new_line_str_2 = r".\n"
                    temp_lessons.append(
                        f"{LESSONS_DAILY[lesson_num]} - {lesson.replace('_', '').replace(temp_new_line_str_2, '-').replace(temp_new_line_str_1, '.')}")
                a += 1
                lesson_num += 1
            lesson_num = 1
        temp_var = 6
        while temp_var <= 36:
            temp = temp_lessons[temp_var - 6:temp_var]
            return_dict[temp_var // 5 - 1] = "".join(temp)
            temp_var += 6
        one_sheet_lessons[group_number] = return_dict
        group_number += 1

        start_col_ord += 3
        end_col_ord += 3

    return one_sheet_lessons


def main():
    all_lessons = {}
    for i in range(len(sheet_names)):
        all_lessons[i] = parse("C", "E", i)
    return all_lessons


if __name__ == '__main__':
    js = main()
    with open('test1.json', mode='w', encoding='utf8') as file:
        json.dump(js, file, ensure_ascii=False)
