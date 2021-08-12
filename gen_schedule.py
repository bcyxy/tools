# -*- coding:utf-8 -*-
# 生成计划排期表
import datetime


def tr_sect_info(sect_info):
    """
    处理单个section信息
    """
    start_date_str = sect_info.get("start", None)
    if start_date_str is None:
        return []
    date_cursor = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    date_cursor -= datetime.timedelta(days=1)

    overtime_str_list = sect_info.get("overtime", [])
    overtime_set = set()
    for overtime_str in overtime_str_list:
        overtime = datetime.datetime.strptime(overtime_str, "%Y-%m-%d")
        overtime_set.add(overtime)

    # 有固定排期的任务
    tasks = sect_info.get("tasks", [])
    task_list = []
    for task_info in tasks:
        desc = task_info.get("desc", None)
        if desc is None:
            continue
        days = task_info.get("days", None)
        if days is None:
            continue
        date_str = task_info.get("date", None)
        if date_str is None:
            continue
        start_data = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        end_date = start_data+datetime.timedelta(days=days-1)
        task_list.append((start_data, end_date, days, "crit", desc))

    # 无固定排期的任务
    for task_info in tasks:
        desc = task_info.get("desc", None)
        if desc is None:
            continue
        days = task_info.get("days", None)
        if days is None:
            continue
        date_str = task_info.get("date", None)
        if date_str is not None:
            continue
        days2 = days
        start_data = None
        end_date = None
        while True:
            date_cursor += datetime.timedelta(days=1)

            # 判断加班
            if date_cursor not in overtime_set:
                # 在周末
                week = date_cursor.isoweekday()
                if week == 6 or week == 7:
                    continue

                # 有排期
                hasT = False
                for task in task_list:
                    if date_cursor >= task[0] and date_cursor <= task[1]:
                        hasT = True
                        break
                if hasT:
                    continue

            if start_data is None:
                start_data = date_cursor

            days2 -= 1
            if days2 == 0:
                end_date = date_cursor
                break
        task_list.append((start_data, end_date, days, "", desc))
    for overtm in overtime_set:
        task_list.append((overtm, overtm, 1, "done", "加班"))

    task_list.sort()
    return task_list


def gen_task_table(sch_dict):
    """
    生成任务表
    """
    task_table = {}
    for secttion, sect_info in sch_dict.items():
        task_list = tr_sect_info(sect_info)
        task_table[secttion] = task_list
    return task_table


md_gantt_base = '''gantt
dateFormat YYYY-MM-DD
title schedule
'''


def gen_md_gantt(task_table):
    """
    生成markdown甘特图文本
    """
    md_gantt_txt = md_gantt_base
    for section, tasks in task_table.items():
        md_gantt_txt += "section %s\n" % section
        for task_it in tasks:
            start_tm, end_tm, days, mark, desc = task_it
            task_desc = "%s(%d)" % (desc, days)
            start_dstr = start_tm.strftime("%Y-%m-%d")
            end_dstr = (end_tm+datetime.timedelta(days=1)
                        ).strftime("%Y-%m-%d")
            md_gantt_txt += "    %s: %s, %s, %s\n" % (
                task_desc, mark, start_dstr, end_dstr)
    return md_gantt_txt


def gen_md_table(task_table):
    """
    生成markdown表格
    """
    table_txt = (
        "|%-11s|%-11s|%-5s|%-5s|\n"
        "|%s|%s|%s|%s|\n"
    ) % ("start", "end", "days", "task", "-"*11, "-"*11, "-"*5, "-"*5)
    for section, tasks in task_table.items():
        for task_it in tasks:
            start_tm, end_tm, days, mark, desc = task_it
            start_dstr = start_tm.strftime("%Y-%m-%d")
            end_dstr = end_tm.strftime("%Y-%m-%d")
            table_txt += "|%-11s|%-11s|%-5d|%s|\n" % (
                start_dstr, end_dstr, days, desc)
    return table_txt


if __name__ == "__main__":
    sch_dict = {
        "项目排期": {
            "start": "2021-08-09",
            "overtime": ["2021-09-18", "2021-09-26", "2021-10-09"],
            "tasks": [
                {"date": "2021-09-19", "days": 3, "desc": "中秋节"},
                {"date": "2021-10-01", "days": 7, "desc": "国庆节"},
                {"date": "2021-09-01", "days": 7, "desc": "重要工作1"},
                {"days": 3, "desc": "工作1"},
                {"days": 10, "desc": "工作2"},
                {"days": 8, "desc": "工作3"},
                {"days": 12, "desc": "工作4"},
                {"days": 8, "desc": "工作5"},
            ]
        },
        "时间点": {
            "start": "2021-08-09",
            "tasks": [
                {"date": "2021-09-10", "days": 1, "desc": "xxx功能上线"}
            ]
        }
    }
    task_table = gen_task_table(sch_dict)
    md_gantt_txt = gen_md_gantt(task_table)
    print(md_gantt_txt)

    md_table_txt = gen_md_table(task_table)
    print(md_table_txt)

