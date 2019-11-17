#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
import tkinter
from psychopy import visual, core, event, gui
import pandas as pd
import numpy as np
from pylink import *
import pylink
from Table_class import Table

p = np.array([0.01, 0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95, 0.99])
money = np.array([(25, 0), (50, 0), (75, 0), (100, 0), (150, 0), (200, 0), (400, 0), (800, 0),
                  (50, 25), (75, 50), (100, 50), (150, 50), (150, 100), (200, 100), (200, 150)])
# 建立存储字典result
result = {'name': 'null', 'sex': 'null', 'age': 0, 'type': 'NULL', 'p': [], '1-p': [], 'x': [], 'y': [], 'id': [],
          'RT': [], 'block': [],
          'first_upper': [], 'first_lower': [], 'upper': [], 'lower': [], 'mirror': [], 'inverse': []}
clk_data = {'rt': [], 'gamble': [], 'y': [], 'reward': [], 'p': [], 'x1': [], 'x2': [], 'flag': []}

# GUI
myDlg = gui.Dlg(title=u"实验")
myDlg.addText(u'被试信息')
myDlg.addField('name:')
myDlg.addField('sex:', choices=['male', 'female'])
myDlg.addField('age:', 21)
myDlg.addField('类别:', choices=['A', 'B'])
# A 为连续呈现；B为随机
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
window = tkinter.Tk()
w = window.winfo_screenwidth()
h = window.winfo_screenheight()
if not myDlg.OK:
    core.quit()

result['name'] = ok_data[0]
result['sex'] = ok_data[1]
result['age'] = ok_data[2]
if ok_data[3] == 'A':
    result['type'] = 'repeat'
else:
    result['type'] = 'random'

# 读取初始数据
data = pd.read_csv('data.csv')
df = data.copy()
if result['type'] == 'random':
    df = df.sample(frac=1)
    df.index = [i for i in range(len(df))]
item = [0] * len(p)
for i in range(len(p)):
    item[i] = data.loc[15*i:15*i+14].values
    np.random.shuffle(item[i])  # 打乱每个p下的项目
# 打乱总体
np.random.shuffle(item)
# 不要写[[0]*15]*11，这样赋值时会出错
trial_data = {'p': [], 'x1': [], 'x2': [], 'block': []}
for i in range(11):
    for j in range(15):
        trial_data['p'].append(item[i][j][0])
        trial_data['x1'].append(item[i][j][1])
        trial_data['x2'].append(item[i][j][2])
        trial_data['block'].append('block%s' % (i + 1))
df = pd.DataFrame(trial_data)
if result['type'] == 'repeat':
    # 插入其他概率
    # 便利满足条件的插入位置，3个其他p不出现在开头末尾且不连着，连续p值不超过5个
    sample_ind = []
    for a in [1, 2, 3]:
        for b in range(a, 4):
            for d in [3, 4, 5]:
                c = 12-a-b-d
                if b <= c <= d:
                    sample_ind.append(np.array([a, b, c, d]))
    s = []
    for j in range(11):
        a = random.choice(sample_ind)
        np.random.shuffle(a)
        for i in [1, 2, 3]:
            s.append((np.sum(a[:i])+i-1)+15*j)
    # 抽取要打乱的部位
    a = df.loc[s]
    b = a.copy()
    # 剔除插入概率与重复概率相同的结果
    while (b.p.values == a.p.values).any():
        b = b.sample(frac=1)
        b.index = a.index
        b.block = a.block
    df.loc[b.index]=b
df.to_csv('trial_data.csv')
# df = df1.loc[df1.block == ok_data[3]]

back = [0, 0, 0]
color = [1, 1, 1]
win = visual.Window(size=(w, h), fullscr=True, units='pix', color=back)

card_pos = [[0 for i in range(3)] for i in range(7)]
table = [[0 for i in range(3)] for i in range(7)]
value = [[0 for i in range(3)] for i in range(7)]
gou_pos = [[0 for i in range(3)] for i in range(7)]
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
jq_head = Table(visual.TextStim(win, height=h / 36),
                visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2),
                visual.ImageStim(win),
                [[-2 * a, 3 * b], [-2 * a, 2 * b], [-a, 2 * b], [-a, 3 * b]])
jq_head.txt.text = title_text[0]
table_jq = Table(visual.TextStim(win, text='奖券', height=h / 30),
                 visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2),
                 visual.ImageStim(win),
                 [[-2 * a, 2 * b], [-2 * a, -2 * b], [-a, -2 * b], [-a, 2 * b]])
for m in range(5):
    for n in range(3):
        table[m][n] = Table(visual.TextStim(win, height=h / 30),
                            visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2),
                            visual.ImageStim(win, image="gou.png", size=32 * h / 720),
                            card_pos[m][n])
        if m == 0:
            table[m][n].txt.text = title_text[n + 1]
            table[m][n].txt.height = h / 36

# 确认
ok = visual.TextStim(win, text=u"确认", pos=(0, -3.5 * b), height=h / 36)
ok_shape = visual.ShapeStim(win, lineColor=[0.8, 0.8, 0.8], lineWidth=2)
ok_shape.vertices = [[-0.5 * a, -4 * b], [-0.5 * a, -3 * b], [0.5 * a, -3 * b], [0.5 * a, -4 * b]]

# 时间间隔
t_trial = {'t_fix': 0.5}
# 文本
# text_gamble_1 = visual.TextStim(win, height=64 * h / 720, pos=(int(-150 * w / 1024), 0), color=color)
# text_gamble_2 = visual.TextStim(win, height=64 * h / 720, pos=(int(150 * w / 1024), 0), color=color)
# text_p = visual.TextStim(win, height=64 * h / 720, color=color)
txt = visual.TextStim(win, height=64 * h / 720)
text_chaoshi = visual.TextStim(win, height=64 * h / 720, color=color)
# 注视点
fix = visual.ImageStim(win, image="fix.png", size=64 * h / 720)
# 指导语
pic = visual.ImageStim(win, size=(w, h))

clk_trial = core.Clock()

# 指导语
while True:
    for i in range(2):
        pic.image = 'pic/introduction_%s' % (i + 1)
        pic.draw()
        win.flip()
        event.waitKeys(keyList=['space'])
        event.clearEvents()
    txt.text = '按【空格键】进入决策实验练习'
    txt.draw()
    win.flip()
    key = event.waitKeys(keyList=['space', 'escape'])
    if 'space' in key:
        event.clearEvents()
        break
    event.clearEvents()

myMouse = event.Mouse()
myMouse.setVisible(0)
flag = 0
x1 = 0
y1 = 0
# 练习
for ii in [23, 135, 52, 83, 29]:
    inverse, mirror = np.random.randint(0, 2, 2)
    trial = df.loc[ii]
    p_v = trial['p']
    x = trial['x1']
    y = trial['x2']
    table_jq.txt.text = "%s%%，%s元\n%s%%，%s元" % (int(100 * p_v), int(x), 100 - int(100 * p_v), int(y))
    fix.draw()
    win.flip()
    core.wait(0.5)
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
            if clk_trial.getTime() > 1000:
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

# 开始屏
txt.text = '按【空格键】开始实验'
txt.draw()
win.flip()
event.waitKeys(keyList=['space'])
event.clearEvents()
myMouse = event.Mouse()
myMouse.setVisible(0)
core.wait(0.5)
# 开始
flag = 0
x1 = 0
y1 = 0
clk = core.Clock()
clk2 = core.Clock()
for ii in range(len(df)):
    inverse, mirror = np.random.randint(0, 2, 2)
    core.wait(0.1)
    myMouse.setVisible(0)
    tr = ii
    # 每个trial包含先后两次
    result['id'].append(tr)
    trial = df.loc[tr]
    p_v = trial['p']
    x = trial['x1']
    y = trial['x2']
    table_jq.txt.text = "%s%%，%s元\n%s%%，%s元" % (int(100 * p_v), int(x), 100 - int(100 * p_v), int(y))
    result['p'].append(p_v)
    result['1-p'].append(1 - p_v)
    result['x'].append(x)
    result['y'].append(y)
    result['mirror'].append(mirror)
    result['inverse'].append(inverse)
    result['block'].append(trial['block'])
    # 注视点
    fix.draw()
    win.flip()
    core.wait(0.5)
    too_long = 0
    # 选择
    for flag in range(2):
        myMouse.setVisible(1)
        if too_long == 1:
            result['upper'].append(-1)
            result['lower'].append(-1)
            too_long = 0
            myMouse.setVisible(0)
            break
        # 建立确定金额阵列
        col = [0] * 2
        col[0] = [x - k * (x - y) / 5 for k in range(6)]
        if flag == 1:
            col[1] = [x1 - k * (x1 - y1) / 5 for k in range(6)]
        col_p = col[flag]
        state = 'running'
        value = [[0 for i in range(3)] for i in range(7)]
        clk.reset()
        clk2.reset()
        clk_trial.reset()
        while True:
            # 取消时间限制（将超时设为1000s）
            if clk_trial.getTime() > 1000:
                if flag == 0:
                    result['first_upper'].append(-1)
                    result['first_lower'].append(-1)
                    too_long = 1
                else:
                    result['upper'].append(-1)
                    result['lower'].append(-1)
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
                            clk_data['rt'].append(clk2.getTime())
                            clk_data['gamble'].append(i)
                            clk_data['reward'].append(col_p[i])
                            clk_data['y'].append(j)
                            clk_data['p'].append(p_v)
                            clk_data['x1'].append(x)
                            clk_data['x2'].append(y)
                            clk_data['flag'].append(flag)
                            clk2.reset()
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
                    rt = clk.getTime()
                    clk_data['rt'].append(clk2.getTime())
                    clk_data['gamble'].append(-1)
                    clk_data['reward'].append(-1)
                    clk_data['y'].append(-1)
                    clk_data['p'].append(p_v)
                    clk_data['x1'].append(x)
                    clk_data['x2'].append(y)
                    clk_data['flag'].append(flag)
                    change = sum(check)
                    x1 = col_p[change - 1]
                    y1 = col_p[change]
                    if flag == 0:
                        result['first_upper'].append(x1)
                        result['first_lower'].append(y1)
                    else:
                        result['upper'].append(x1)
                        result['lower'].append(y1)
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
        myMouse.setVisible(0)
        result['RT'].append(rt)
        if flag == 1:
            myMouse.setVisible(0)
        core.wait(0.5)
    # trial结束
    # 本次trial结束
    core.wait(2)
    if ((tr+1)%15 == 0 )&tr:
        # 休息 10s强制
        txt.text = "请休息，按【空格键】继续"
        txt.draw()
        win.flip()
        core.wait(8)
        key = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in key:
            break
        elif 'space' in key:
            pass
    # core.wait(random.randrange(20, 41, step=1) / 10. - 0.5)

# 休息 10s强制
txt.text = "本试次结束，请呼叫主试"
txt.draw()
win.flip()
core.wait(3)

with open("exp_data\\%s_%s.csv" % (result['name'], result['type']), 'a') as exp_data:
    exp_data.write(
        'id' + ',' + 'name' + ',' + 'age' + ',' + 'sex' + ',' + 'p' + ',' + '1-p' + ',' + 'x1' + ',' + 'x2' + ',' + 'RT'
        + ',' + 'first_upper' + ',' + 'first_lower' + ',' + 'upper' + ',' + 'lower' + ',' + 'block' + ',' + 'mirror' +
        ',' + 'inverse' + ',' + 'type' + '\n')
    for i in range(len(result['id'])):
        exp_data.write(str(result['id'][i]) + ',' + result['name'] + ',' + str(result['age']) + ',' + result['sex']
                       + ',' + str(result['p'][i]) + ',' + str(result['1-p'][i]) + ',' + str(result['x'][i]) + ',' +
                       str(result['y'][i]) + ',' + str(result['RT'][i]) + ',' + str(result['first_upper'][i]) + ',' +
                       str(result['first_lower'][i]) + ',' + str(result['upper'][i]) + ',' + str(result['lower'][i]) +
                       ',' + result['block'][i] + ',' + str(result['mirror'][i]) + ',' + str(result['inverse'][i]) +
                       ',' + result['type'] + '\n'
                       )

with open("exp_data\\RT%s_%s.csv" % (result['name'] + time.strftime("%H-%M-%S"), result['type']), 'a') as exp_data:
    exp_data.write(
        'name' + ',' + 'age' + ',' + 'sex' + ',' + 'p' + ',' + 'x1' + ',' + 'x2' + ',' + 'RT' + ',' +
        'gamble' + ',' + 'y' + ',' + 'reward' + ',' + 'flag' + '\n')
    for i in range(len(clk_data['p'])):
        exp_data.write(result['name'] + ',' + str(result['age']) + ',' + result['sex']
                       + ',' + str(clk_data['p'][i]) + ',' + str(clk_data['x1'][i]) + ',' + str(clk_data['x2'][i]) + ','
                       + str(clk_data['rt'][i]) + ',' + str(clk_data['gamble'][i]) + ',' + str(clk_data['y'][i]) + ',' +
                       str(clk_data['reward'][i]) + ',' + str(clk_data['flag'][i]) + '\n'
                       )

# 实验结束
win.close()
core.quit()
