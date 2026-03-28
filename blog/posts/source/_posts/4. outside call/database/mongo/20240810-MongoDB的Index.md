---
title: MongoDB的Index
date: 2024-08-10 19:10:08
permalink: 2024/08/10/20240810-MongoDB的Index/
banner_img: /img/20240810-MongoDB的Index.jpg
tags:
  - mongodb
  - index
  - database
categories: 数据库
---



最近在写一个需求，需要用到mongoDB，保存的数据结构大概如下。查找的时候需要先按照日期，再按object_code查询。于是我开始研究MongoDB的索引。我们需要解决两个问题，1. MongoDB的索引是如何工作的，2. MongoDB有哪些索引分类，它们的作用范围、分层模型分别是怎样的。最后我们才能回答，MongoDB的索引能否满足我的需求。

![](/img/20240810-MongoDB的Index/01.jpg)



## 一. MongoDB的索引是如何工作的

资料：[An Introduction To Search Indexes | MongoDB](https://www.mongodb.com/resources/basics/search-index)

资料离给出了一个根据索引排序的示例图。从图里可以看出，索引是挂在数据集外的。索引相当于另写了一个数据结构来处理排序、查找的问题，跟MySQL的非主键索引类似。

另外，MongoDB索引使用B-Tree形式。

#### 1.1 MongoDB的查询优化器是如何工作的

资料：[ESR（相等、排序、范围）规则 - MongoDB 手册 v7.0](https://www.mongodb.com/zh-cn/docs/manual/tutorial/equality-sort-range-rule/)

索引有几个抽象的问题，如索引中什么是相等、如何排序、索引作用范围，这被MongoDB抽象成ESR规则。

MongoDB查询时会优先做等值匹配，然后再做排序。如搜索，就会先找出所有manufacturer = “GM"的数据，再根据model进行排序。

db.cars.find( { manufacturer: "GM" } ).sort( { model: 1 } )

在等值匹配和排序之后，MongoDB才会继续做范围限制。Regex也是范围限制。



#### 1.2 创建支持查询的索引（即不用回表的索引）

db.products.createIndex( { "category": 1, "item": 1 } )

当创建了上面这种索引，就可以支持仅查询category，或查询category和item的索引。这两个数据都在索引上了，不需要回表。



#### 1.3 对排序结果进行排序

在使用索引查询时，可以指定排序规则。如

db.myColl.createIndex( { category: 1 }, { collation: { locale: "fr" } } )

db.myColl.find( { category: "cafe" } ).collation( { locale: "fr" } )

这时查询语句与索引使用同样的排序器，因此可以使用索引。

db.myColl.find( { category: "cafe" } )

这个查询使用简单的二进制排序器，因此无法使用索引。排序规则不一样了嘛。



与文档键（包括嵌入式文档键）的匹配使用简单的二进制比较。



如果索引键有多个不同类型，排序会按照[比较/排序顺序 - MongoDB 手册 v7.0](https://www.mongodb.com/zh-cn/docs/manual/reference/bson-type-comparison-order/#std-label-bson-types-comparison-order)顺序排列。



#### 1.4 确保索引的大小可以被RAM容纳

可以使用db.collection.totalIndexSize()来确定大小



### 二. 如何测量索引的使用情况

1. 1. 使用indexStats
   2. 使用explain
   3. 使用hints



### 三. 不同的索引类型

#### 3.1 单字段索引

最基础索引，不作赘述。



#### 3.2 复合索引

从集合中每个文档的两个或多个字段收集数据并对其排序。

![](/img/20240810-MongoDB的Index/02.jpg)

单个复合索引最多可包含 32 个字段。

复合索引可以包含一个单字段索引+一个多键索引，但只能有一个多键索引。这样就能满足我的任务要求了。

#### 3.3 多键索引

多键索引收集数组中存储的数据并进行排序。这个图画得很好。

![](/img/20240810-MongoDB的Index/03.jpg)

在复合多键索引中，每个索引文档*最多*可以有一个值为数组的索引字段。具体而言：

{ _id: 1, scores_spring: [ 8, 6 ], scores_fall: [ 5, 9 ] }

无法创建索引{ scores_spring: 1, scores_fall: 1 }



应用1. 在数组字段上创建索引

[在数组字段上创建索引 - MongoDB 手册 v 7 。 0](https://www.mongodb.com/zh-cn/docs/manual/core/indexes/index-types/index-multikey/create-multikey-index-basic/#std-label-index-create-multikey-scalar)

应用2. 在数组字段的嵌入式字段上创建索引（这个符合我的问题场景）

[在数组中的嵌入式字段上创建索引 - MongoDB 手册 v 7 。 0](https://www.mongodb.com/zh-cn/docs/manual/core/indexes/index-types/index-multikey/create-multikey-index-embedded/#std-label-index-create-multikey-embedded)



### 四. 总结

​	最后发现，根据我设计的数据结构，复合多键索引可以满足我的需求。其中date + object_code为字段索引，object_item.code为复合索引。
