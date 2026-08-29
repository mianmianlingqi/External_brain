# External Brain

A Seed is published compressed. An Owner forks it and runs Init to expand a personal Brain onto a Target. Init confirms the first Direction. A Brain can hold several Directions. The Brain assists that Owner's learning. Other Agents reach the Brain through Skills.

## Language

**Seed**:
The compressed Git project as published. It is not yet a Brain. It holds Skills, contracts, and an empty Brain shape, and does not name a Direction.
_Avoid_: 本体, 压缩包, 模板（口语可以说模板；正式词是 Seed）

**Fork**:
An Owner's copy of the Seed, still compressed until Init.
_Avoid_: clone, 副本, 安装

**Init**:
The Skill that expands a Fork onto a Target, confirms the first Direction, records how an Agent connects to the Brain (address and secret), and gives the Owner the View link and secret. Later Directions are added by a Skill, not by Init.
_Avoid_: setup, install, 部署

**Target**:
Where Init expands both a workspace and a running Brain: the Owner's machine or a server.
_Avoid_: 环境, host, 部署目标

**Brain**:
The expanded personal service that holds one Owner's learning state. It exists only after Init and can hold several Directions.
_Avoid_: 平台, app, 系统, 外脑（服务名可以叫 Brain，工作不是「什么都存」）

**Owner**:
The person a Brain instance belongs to.
_Avoid_: 用户, 使用者, client, account

**Agent**:
An external AI that acts for an Owner and talks to that Owner's Brain.
_Avoid_: bot, assistant, plugin

**Skill**:
The contract an Agent uses to interact with a Brain.
_Avoid_: plugin, integration, API（对 Agent 而言，合同是 Skill，不是裸接口）

**Direction**:
A subject or field the Owner is learning (for example analog electronics, or Italian). Init confirms the first one. An Agent adds more later through a Skill. All Questions under a Direction are the pool a Plan or the Owner draws from. That pool is not a separate named thing.
_Avoid_: 学习方向, 主题, 目标, Exam, 题库（不要把题库做成第二种容器）

**Exam**:
An optional named assessment under a Direction. The Brain is not bound to an Exam.
_Avoid_: 测验, test, quiz（不要用 Exam 称呼 Direction）

**Point**:
A fact or procedure the Owner is learning. It belongs to exactly one Direction. The first release stores Point. A Point is Clear only when it has at least one Question or Task, every Question and Task under it has a latest right Verdict, and each has been tried at least once. An empty Point is not Clear.
_Avoid_: 知识点, topic, card, 概念

**Question**:
A prompt the Owner answers during a Drill, with a stored expected answer. It belongs to exactly one Point (and so to exactly one Direction). The Brain issues the Verdict.
_Avoid_: 习题, item, 卡片, Task

**Task**:
A learning activity with no stored expected answer (lab, oral, portfolio). It belongs to exactly one Point (and so to exactly one Direction). The Owner reports the Verdict. The first release includes Task.
_Avoid_: 作业, 开放题, project, Question

**Drill**:
One attempt at a Question or a Task that ends with a Verdict. The Owner may name the Question, or ask for one from a Direction. The Brain may also pick from the Plan.
_Avoid_: 练习, session, 学习, quiz

**Verdict**:
The judgement of a Drill: right or wrong. For a Question the Brain issues it; for a Task the Owner reports it.
_Avoid_: score, 反馈, 评价（只有对错，没有分数带）

**Graph**:
The map of Points in a Direction and the Links between those Points.
_Avoid_: 知识图谱, mind map, 网

**Link**:
A before-after tie between two Points: learn this Point before that Point. No other kind of tie. A Proposal that would make a loop is rejected.
_Avoid_: 关系, edge, 相关

**Plan**:
An ordered list of Points the Owner should learn next. The Brain writes it from Verdicts and the Graph only when the Owner asks to update it. The Owner may edit it.
_Avoid_: 课表, curriculum, 日程

**Review**:
How many Points are Clear under a Direction, how many are not, how many Misses there are, and the next Point on the Plan. The View also shows the Graph.
_Avoid_: 分析, dashboard, 报告, 评语

**Clear**:
The state of a Point that has been passed. The Plan can move past a Clear Point.
_Avoid_: mastered, done, 完成, 学会了

**Open**:
The state of a Point that has at least one Question or Task, is not Clear, and is not Blocked.
_Avoid_: in progress, 进行中

**Blocked**:
The state of a Point that has a before-Point that is not Clear.
_Avoid_: locked, 锁定

**View**:
A read-only web page for the Owner. One address lists Directions; the Owner picks one. It shows the Review numbers and the Graph with Clear, Open, and Blocked Points. The Owner does not accept Proposals, edit the Plan, or answer Questions on the View. Opening it needs the link and secret from Init.
_Avoid_: 后台, dashboard, app, 网站产品

**Miss**:
A Question or Task whose latest Verdict is wrong. Misses under a Direction are what the Owner retries as a group.
_Avoid_: 错题本, 错题集（口语可以说错题；正式词是 Miss）

**Proposal**:
A Point, Question, or Link an Agent suggests from pasted notes. It is not stored until the Owner accepts it.
_Avoid_: draft, 建议, 候选
