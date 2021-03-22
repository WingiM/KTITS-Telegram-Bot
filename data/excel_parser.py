import openpyxl

wb = openpyxl.load_workbook("rasp.xlsx")
sheet_names = wb.sheetnames


def parseLesson(startCol, endCol):
    temp_lessons = []
    return_dict = {}
    a = 8
    lesson_num = 1
    sheet = wb[sheet_names[0]]
    while a <= 41:
        for i in range(a, a + 6):
            for cellObj in sheet[f"{startCol}{i}:{endCol}{i}"]:
                lesson = ""
                for cell in cellObj:
                    if cell.value is None:
                        break
                    lesson += f"{str(cell.value)} "
                temp_lessons.append(f"{str(lesson_num)} - {lesson}")
            a += 1
            lesson_num += 1
        lesson_num = 1

    temp_var = 6
    while temp_var <= 36:
        temp = temp_lessons[temp_var - 6:temp_var]
        return_dict[temp_var // 5 - 1] = "".join(temp)
        temp_var += 6

    return return_dict


programmers_lessons = parseLesson("R", "T")
print(programmers_lessons)
