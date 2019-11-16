#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
import tkinter
from psychopy import visual, core, event, gui, parallel
import pandas as pd
import numpy as np
from pylink import *
import pylink
from Table_class import Table

p = np.array([0.01, 0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95, 0.99])
money = np.array([(25, 0), (50, 0), (75, 0), (100, 0), (150, 0), (200, 0), (400, 0), (800, 0),
                  (50, 25), (75, 50), (100, 50), (150, 50), (150, 100), (200, 100), (200, 150)])
# 建立存储字典result
result = {'name': 'null', 'sex': 'null', 'age': 0, 'block': 'NULL', 'p': [], '1-p': [], 'x': [], 'y': [], 'id': [],
          'RT': [],
          'first_upper': [], 'first_lower': [], 'upper': [], 'lower': []}
clk_data = {'rt': [], 'gamble': [], 'y': [], 'reward': [], 'p': [], 'x1': [], 'x2': []}

# GUI
myDlg = gui.Dlg(title=u"实验")
myDlg.addText(u'被试信息')
myDlg.addField('name:')
myDlg.addField('sex:', choices=['male', 'female'])
myDlg.addField('age:', 21)
myDlg.addField('block:', choices=['block1', 'block2', 'block3', 'block4', 'block5'])
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
window = tkinter.Tk()
w = window.winfo_screenwidth()
h = window.winfo_screenheight()
if not myDlg.OK:
    core.quit()

result['name'] = ok_data[0]
result['sex'] = ok_data[1]
result['age'] = ok_data[2]
result['block'] = ok_data[3]

if ok_data[3] == 'block1':
    # 读取初始数据
    data = pd.read_csv('data.csv')
    data_np = data.values
    item = [0] * len(p)
    for i in range(len(p)):
        item[i] = data.loc[data['p'] == p[i]].values
        np.random.shuffle(item[i])  # 打乱每个p下的项目
    # 打乱总体
    np.random.shuffle(item)
    # 不要写[[0]*33]*5，这样赋值时会出错
    block = [[0] * 33 for _ in range(5)]
    # 每个block 33个trial 11（p）* 3(x1 x2)
    for i in range(5):
        for j in range(11):
            block[i][3 * j] = item[j][i * 3]
            block[i][3 * j + 1] = item[j][i * 3 + 1]
            block[i][3 * j + 2] = item[j][i * 3 + 2]
        np.random.shuffle(block[i])
    trial_data = {'p': [], 'x1': [], 'x2': [], 'block': []}
    for i in range(5):
        for j in range(33):
            trial_data['p'].append(block[i][j][0])
            trial_data['x1'].append(block[i][j][1])
            trial_data['x2'].append(block[i][j][2])
            trial_data['block'].append('block%s' % (i + 1))

    df1 = pd.DataFrame(trial_data)
    df1.to_csv('trial_data.csv')
    df = df1.loc[df1.block == ok_data[3]]
else:
    data = pd.read_csv('trial_data.csv')
    df = data.loc[data.block == ok_data[3]]
    df.index = [i for i in range(len(df))]

# back = cst.cielab2rgb((75, 0, 0))
back = [-0.00777115, -0.00773734, -0.00784829]
color = [-0.69293506,  0.07942268,  0.25594554]

win = visual.Window(size=(w, h), fullscr=True, units='pix', color=back)
closeGraphics()
card_pos = [[0 for i in range(3)] for i in range(5)]
table = [[0 for i in range(3)] for i in range(5)]
value = [[0 for i in range(3)] for i in range(7)]
gou_pos = [[0 for i in range(3)] for i in range(5)]
a = w / 8.
b = h / 12.

# 各表格位置
for i in range(5):
    for j in range(3):
        x1 = j * a - a
        x2 = j * a
        y1 = 3 * b - i * b
        y2 = 2 * b - i * b
        card_pos[i][j] = ([[x1, y1], [x1, y2], [x2, y2], [x2, y1]])
        gou_pos[i][j] = ([int((x1 + x2) / 2), int((y1 + y2) / 2)])

# 建立表格对象
title_text = [u"抽奖券", u"选择抽奖券", u"选择固定金额", u"固定金额"]
jq_head = Table(visual.TextStim(win, height=h/36),
                visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2),
                visual.ImageStim(win),
                [[-2 * a, 3 * b], [-2 * a, 2 * b], [-a, 2 * b], [-a, 3 * b]])
jq_head.txt.text = title_text[0]
table_jq = Table(visual.TextStim(win, text='奖券', height=h/36),
                 visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2),
                 visual.ImageStim(win),
                 [[-2 * a, 2 * b], [-2 * a, -2 * b], [-a, -2 * b], [-a, 2 * b]])
for m in range(5):
    for n in range(3):
        table[m][n] = Table(visual.TextStim(win, height=h/30),
                            visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2),
                            visual.ImageStim(win, image="gou.png", size=32 * h / 720),
                            card_pos[m][n])
        if m == 0:
            table[m][n].txt.text = title_text[n + 1]
            table[m][n].txt.height = h/36

# 确认
ok = visual.TextStim(win, text=u"确认", pos=(0, -3.5 * b), height=h / 36)
ok_shape = visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2)
ok_shape.vertices = [[-0.5 * a, -4 * b], [-0.5 * a, -3 * b], [0.5 * a, -3 * b], [0.5 * a, -4 * b]]

# 时间间隔
t_trial = {'t_fix': 0.5, 't_gamble': 1.5, 't_response': 1.5, 't_int': [2, 3, 4]}
# 文本
text_gamble_1 = visual.TextStim(win, height=64 * h / 720, pos=(int(-150 * w / 1024), 0), color=color)
text_gamble_2 = visual.TextStim(win, height=64 * h / 720, pos=(int(150 * w / 1024), 0), color=color)
text_p = visual.TextStim(win, height=64 * h / 720, color=color)
txt = visual.TextStim(win, height=64 * h / 720, color=color)
text_chaoshi = visual.TextStim(win, height=64 * h / 720, color=color)
# 注视点
fix = visual.ImageStim(win, image="dot2.png", size=64 * h / 720)
# 指导语
pic = visual.ImageStim(win, image="dot2.png", size=(w, h))


clk_trial = core.Clock()
if ok_data[3] == 'block1':
    myMouse = event.Mouse()
    myMouse.setVisible(0)
    flag = 0
    x1 = 0
    y1 = 0
    # 练习
    for ii in [2, 13, 5, 8, 9]:
        inverse, mirror = np.random.randint(0, 2, 2)
        trial = df.loc[ii]
        p_v = trial['p']
        x = trial['x1']
        y = trial['x2']
        core.wait(0.1)
        fix.draw()
        win.flip()
        core.wait(0.5)
        text_p.text = "%s%%" % int(100 * p_v)
        text_p.draw()
        win.flip()
        core.wait(random.randrange(20, 41, step=1) / 10.)
        win.flip()
        core.wait(0.2)
        if random.randint(0, 1):
            text_gamble_1.text = "￥%s" % int(x)
            text_gamble_2.text = "￥%s" % int(y)
        else:
            text_gamble_1.text = "￥%s" % int(y)
            text_gamble_2.text = "￥%s" % int(x)
        text_gamble_1.draw()
        text_gamble_2.draw()
        win.flip()
        core.wait(3)
        win.flip()
        core.wait(0.2)
        too_long = 0
        for flag in range(2):
            myMouse.setVisible(1)
            if too_long == 1:
                too_long = 0
                myMouse.setVisible(0)
                break
            col = [0] * 2
            col[0] = [x - k * (x - y) / 5 for k in range(6)]
            if flag == 1:
                col[1] = [x1 - k * (x1 - y1) / 5 for k in range(6)]
            col_p = col[flag]
            state = 'running'
            value = [[0 for i in range(3)] for i in range(7)]
            clk_trial.reset()
            while True:
                if clk_trial.getTime() > 12:
                    if flag == 0:
                        too_long = 1
                    text_chaoshi.text = '超时！'
                    text_chaoshi.draw()
                    win.flip()
                    core.wait(0.3)
                    break
                if state == 'running':
                    value[1][1] = 1
                    value[6][0] = 1
                    for i in range(1, 5):
                        for j in range(2):
                            table[i][j].t(mirror, inverse)
                            if value[i + 1][j] == 1:
                                table[i][j].dui.draw()
                            if myMouse.isPressedIn(table[i][j].shape) and value[i + 1][j] == 0:
                                value[i + 1] = [0] * 3
                                value[i + 1][j] = 1
                                table[i][j].dui.draw()
                            table[i][j].shape.draw()
                        table[i][2].t(mirror, inverse)
                        table[i][2].shape.draw()
                        table[i][2].txt.text = u"%s元" % int(col_p[i])
                        table[i][2].txt.draw()
                    for j in range(3):
                        table[0][j].t(mirror)
                        table[0][j].shape.draw()
                        table[0][j].txt.draw()
                    jq_head.t(mirror)
                    table_jq.t(mirror)
                    jq_head.shape.draw()
                    table_jq.shape.draw()
                    jq_head.txt.draw()
                    table_jq.txt.draw()
                    key = event.getKeys(["escape"])
                    if "escape" in key:
                        state = "exit"
                    check = [0] * (7 - 1)
                    now = [0] * (7 - 1)
                    point = 0
                    for i in range(1, 7):
                        point += value[i][0] + value[i][1]
                        if value[i][1] == 1:
                            now[i - 1] = 1
                    j = 0
                    while j <= 5:
                        if value[j + 1][1] == 1:
                            check[j] = 1
                        else:
                            break
                        j += 1
                    if check == now and point == 6:
                        if ok_shape.contains(myMouse):
                            ok_shape.fillColor = [-1, -1, -1]
                            ok_shape.opacity = 0.3
                        else:
                            ok_shape.fillColor = [0, 0, 0]
                            ok_shape.opacity = 1
                        ok_shape.draw()
                        ok.draw()
                    win.flip()
                    # 获得被试所选转折点
                    if check == now and myMouse.isPressedIn(ok_shape):
                        print(col_p)
                        print(check)
                        change = sum(check)
                        x1 = col_p[change - 1]
                        y1 = col_p[change]
                        # 标记为第二轮
                        state = "quit"
                # 进入下一层
                if state == "quit":
                    win.flip()
                    break
                # 强行终止
                if state == "exit":
                    win.flip()
                    win.close()
                    core.quit()
            win.flip()
            if flag == 1:
                myMouse.setVisible(0)
            core.wait(0.5)
        # trial结束
        core.wait(random.randrange(20, 41, step=1) / 10. - 0.5)

win.close()
core.quit()
