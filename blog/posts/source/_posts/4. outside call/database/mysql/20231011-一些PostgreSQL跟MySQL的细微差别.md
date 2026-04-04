---
title: 一些PostgreSQL跟MySQL的细微差别
date: 2023-10-11 21:12:30
permalink: 2023/10/11/20231011-一些PostgreSQL跟MySQL的细微差别/
banner_img: /img/231011-数据库区别.jpg
tags:
  - postgresql
  - mysql
  - mvcc
categories: 数据库
description: 对比 **PostgreSQL 与 MySQL** 在 MVCC、锁与日常行为上的细微差别，帮助在两种引擎之间切换或联调时少踩坑。本文以笔记形式记录差异与直觉。
---
<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注： 🖋️ 人工创作**

</div>


### 一些PostgreSQL跟MySQL的细微差别

### 1. PostgreSQL和MySQL的MVCC

当同一个数据被两个事务写的时候，MySQL（Innodb）的默认实现是使用悲观锁行锁，锁住当前行，禁止其他事务读写。而PostgreSQL使用了MVCC，也就是记录了数据的版本号，当事务A写数据时，事务B仍可读到旧版本的数据。

#### 1.1. postgres mvcc 一个事务读，一个事务写

A事务读取数据，获取自己的快照

B事务读取数据

A事务修改完成，提交，更新数据版本号

#### 1.2. postgres mvcc 两个事务写

乐观锁，会等到第一个事务执行完再执行第二个数据。

A事务读取数据，获取自己的快照

B事务读取数据，获取自己的快照

A事务修改完成，提交，更新数据版本号

B事务修改完成，提交，发现自己版本号较低，重新获取快照修改

B事务修改完成，提交，更新数据版本号



#### 1.3. 怎么启用mysql的mvcc？

​	mysql5.6以上版本才支持，RR隔离级别才支持



#### 1.4. mvcc跟行锁有什么区别？

​	两个请求同时抵达数据库，每个请求是一个独立事务。A请求修改数据，B请求查询数据，A请求先到。

​	在MySQL的机制下，A事务会锁住这一行数据，B无法读取。等到A释放行锁后，B才可以读取数据。

​	在MVCC机制下，A会新增一行记录，不锁数据。B可以无阻塞地查到旧版本的数据。



### 2. PostgreSQL和MySQL的索引

​	mysql只能在整张表上建立索引，但pg可以在某些列上建立索引。

​	postgres还支持更多的索引类型。



​	mysql仅支持B树索引和hash索引，postgres还支持GiST、SP-GiST等。

​	mysql仅支持整张表建立索引，pg可以建立部分索引、表达式索引、多列索引。



​	postgres支持并发索引。

### 3. PostgreSQL和MySQL对SQL的优化

#### 3.1. 查询计划优化

​	PostgreSQL的优化器会考虑表之间的统计相关信息,调整Join顺序以减少记录数。MySQL的优化器基本按照Join语句顺序处理。

​	PostgreSQL会估算不同的索引在过滤记录数方面的效果,选用最有效的索引。MySQL的选择较简单。

#### 3.2. 统计信息

​	PostgreSQL自动收集并利用各种统计信息进行查询优化,包括列相关性、distinct值比例等。MySQL只有基础的表级统计信息。


### 4. PostgreSQL的堆表和InnoDB中的索引表

​	postgres是堆表，追加写入，主键可以不连续。innodb索引表，涉及页分裂和页合并，主键最好连续。
