---
title: 在Springboot项目中使用MongoDB的QuickStart
date: 2024-08-11 22:38:31
permalink: 2024/08/11/20240811-在Springboot项目中使用MongoDB的QuickStart/
banner_img: /img/20240811-在Springboot项目中使用MongoDB的QuickStart.jpg
tags:
  - mongodb
  - spring-boot
  - database
categories: 数据库
---
<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注： 🖋️ 人工创作**

</div>


接下来要在SpringBoot项目中引入MongoDB，接下来做一些探索，熟悉基本的增删改查操作，了解索引的相关用法。

## 一. MongoDB有哪些相关依赖包

**MongoDB Driver**：MongoDB的Java驱动可以让Java应用与MongoDB数据库进行交互。这个驱动提供了许多直观的API，可以让你执行增删查改(CRUD)操作、索引管理、聚合等常用的数据库任务。MongoDB Java驱动以BSON的格式去处理数据，这个格式类似于JSON，但是有更丰富的数据类型。

**Spring Boot 的 MongoDB Template**：MongoTemplate是Spring框架提供的一个功能强大的工具，可以简化MongoDB操作的复杂性。与直接使用MongoDB驱动相比，该模板提供了一种更高级别的API，它会处理底层的数据读写、连接处理、事务管理等问题。许多操作如CRUD和聚合都被封装成简单的方法调用。使用Spring Data MongoDB的MongoTemplate，你可以直接操作实体对象，而不必担心底层的JSON/ BSON转换问题。

另外，要了解MongoDB Template，又需要讲到**Spring Data Repository**。这又是一大拓展点。今日目标是快速上手，接下来再考虑研究包提供的功能。

## 二. 将MongoDB Client作为Bean引入

引入上文的依赖后，就可将MongoDB Client作为Bean引入。

```java
@Bean
public MongoClient mongoClient(){
    MongoClient mongoClient = MongoClients.create("mongodb://127.0.0.1:27017");
    return mongoClient;
}
```

为使用MongoDB Template，还需定义一个Template Bean。

```java
@Bean
public MongoTemplate mongoTemplate(){
    return new MongoTemplate(mongoClient(), "store_price");
}
```

接下来，就基于MongoTemplate执行插入、删除、更新、查找操作。对数据库层的操作如建表、建立索引直接通过MongoDB语句完成。



## 三. console操作MongoDB数据库

通过Console可以快速操作DB数据库。对于本次测试，我们需要建立一个materialPriceByStore集合，再创建唯一索引。

```plain
-- 列出数据库
show dbs;

-- 创建集合
db.createCollection("materialPriceByStore");

-- 丢弃集合
db.materialPriceByStore.drop();

-- 索引操作
db.materialPriceByStore.createIndex({"affectedDate":-1, "storeCode":1}, {unique:true});
db.materialPriceByStore.createIndex({"affectedDate":-1, "storeCode":1, "materialPriceList.materialCode":1}, {unique:true});
db.materialPriceByStore.getIndexes();
db.materialPriceByStore.dropIndexes();

-- 查询语句
db.materialPriceByStore.find().sort({"affetedDate":1});
db.materialPriceByStore.find();
db.materialPriceByStore.find({"storeCode":"ST_7", "materialPriceList.materialCode":"MC_690341"}, {"materialPriceList":1});
```



## 四. MongoDB索引设计练习

### 4.1 场景一. 树状数据

以下是大概的数据结构设计。数据不更新，只插入和删除。根据affectedDate + storeCode建立唯一索引，每日插入3000条数据，之后也按日删除。每个文档里，materialCode都是不重复的list。



#### 4.1.1 数据结构设计



```java
package com.chanon.graphql.domain;

import lombok.Data;

import java.time.LocalDate;
import java.util.List;

@Data
public class MaterialPriceByStore {

    /**
     * 商店编码
     */
    private String storeCode;

    /**
     * 经营状态
     */
    private String storeStatus;

    /**
     * 商店类型
     */
    private String storeType;

    /**
     * 生效日期
     */
    private LocalDate affectedDate;

    /**
     * 商品价格编码
     */
    private List<MaterialPrice> materialPriceList;

    @Data
    public static class MaterialPrice{

        /**
         * 商品编码
         */
        private String materialCode;

        /**
         * 商品名称
         */
        private String materialName;

        /**
         * 商品价格
         */
        private Double materialPrice;

        /**
         * 商品单位
         */
        private String materialUnit;
    }
}
```



#### 4.1.2 索引设计

有两个唯一索引。这里的设计主要考虑插入和删除。

```plain
db.materialPriceByStore.createIndex({"affectedDate":-1, "storeCode":1}, {unique:true});
db.materialPriceByStore.createIndex({"affectedDate":-1, "storeCode":1, "materialPriceList.materialCode":1}, {unique:true});
```



### 4.2 保存ChatGPT的对话

数据量少，每天最多几十条。需要按分类、日期查找。数据不删除，会以Conversation形式不断追加更新。

在查询中，对话按Conversation形式呈现，不会对数组进行查询。

#### 4.2.1 数据结构设计

```java
package com.chanon.graphql.domain;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class ConversationWithChatgpt {

    private String chatGptName;

    private List<String> categories;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private List<Conversation> messages;

    @Data
    public static class Conversation{

        private Integer seqNo;

        private LocalDateTime createdAt;

        private List<Message> messages;
    }

    @Data
    public static class Message{

        private String role;

        private String content;
    }
}
```



#### 4.2.2 索引设计

不涉及唯一索引。按分类做排序索引，并按时间倒序做排序索引。这里的索引设计主要考虑查询。

```plain
db.conversationWithChatGpt.createIndex({"createdAt":-1});
db.conversationWithChatGpt.createIndex({"categories":1});
```



## 五. 对MonggoDB Template的简单实现业务操作

### 5.1 插入数据

对于有幂等键的插入，需要注意处理DuplicateKeyException。注意，这里对异常的处理是不全面的。

```java
@PostMapping("/addData")
public String addData(){
    try{
        mongoTemplate.insert(generateRandomData());
    }catch (DuplicateKeyException e){
        return "success";
    }catch (Exception e){
        throw e;
    }
    return "success";
}
```

### 5.2 查询数据

查不到时返回空值。

```java
    @PostMapping("/queryDataByStore")
    public List<MaterialPriceByStore> queryDataByStore(@RequestBody QueryDataByStoreReq req){
        Query query = new Query(Criteria.where("storeCode").is(req.getStoreCode()));
        List<MaterialPriceByStore> result = mongoTemplate.find(query, MaterialPriceByStore.class);
        return result;
    }
```



### 5.3 查询数组数据

```java
    @PostMapping("/queryDataByMaterial")
    public List<MaterialPriceByStore.MaterialPrice> queryDataByMaterial(@RequestBody QueryDataByMaterialByReq req){
        Query query = new Query(Criteria.where("storeCode").is(req.getStoreCode())
                .and("materialPriceList.materialCode").is(req.getMaterialCode()));
        query.fields().include("materialPriceList.$");
        MaterialPriceByStore result = mongoTemplate.findOne(query, MaterialPriceByStore.class);
        return result.getMaterialPriceList();
    }
```



## 六. 总结

以上的一些设计练习、常用语句，和插入删除示例足够作为任何人MongoClient的入门练习了。
