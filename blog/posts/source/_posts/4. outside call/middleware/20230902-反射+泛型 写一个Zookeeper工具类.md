---
title: 反射+泛型 写一个Zookeeper工具类
date: 2023-09-01 12:27:49
permalink: 2023/09/01/20230902-反射+泛型 写一个Zookeeper工具类/
banner_img: /img/230902-反射+泛型写一个Zookeeper工具类.jpg
tags:
  - java
  - zookeeper
  - reflection
  - generic
categories: 中间件
description: 用 **Java 反射与泛型** 封装一个可复用的 ZooKeeper 工具类，覆盖初始化与关闭、节点增删、监听器注册等常见操作。本文附实现要点与示例。
---
<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注： 🖋️ 人工创作**

</div>


功能简介：

1. 初始化和关闭
2. 创建和删除节点
3. 注册监听器



### 1. 初始化和关闭

功能要求

- 从配置中读取信息
- 设置权限

```java

    @PostConstruct
    public void init(){
        try{
            if(zkClient == null){
                zkClient = new ZkClient(zookeeperConfig.connectionString);
                zkClient.addAuthInfo("digest", generateAuthInfo());
                zkClient.setZkSerializer(new CustomerSerializer());
                logger.info("Connected to ZooKeeper. ");
                for(Map.Entry<String, String> entry:zookeeperConfig.pathHandlerMap.entrySet()){
                    String path = entry.getKey();
                    String handlerClass = entry.getValue();
                    registeListener(path, handlerClass);
                }
            }
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                zkClient.close();
                System.out.println("Zookeeper Client Closed.");
            }));
        } catch(Exception e){
            logger.error("Error initializing ZooKeeper client. ", e);
        }
    }

```

​    这段代码中，选择将zkClient的初始化交给Spring管理，在容器构造完成之后执行。

​    同时，监听器的注册逻辑也在这里，注册抛出的异常在注册方法里处理了。

​    代码最后利用Java的ShutdownHook机制，在JVM退出前新建线程关闭Zookeeper。不建议大量使用这样的钩子，如果大量使用，关闭程序时会创建大量新线程，可能会出现其他错误。

##### 还有别的初始化的方式吗？

​    zkClient是单例，也可以通过单例模式+static写初始化代码。但我的参数注入是通过Spring完成的，static执行早于Spring参数注入，如果这么写会报错。

​    也可通过懒加载的方式，使用的时候再初始化。但这样就无法使用监听器了。



### 2. 创建和删除节点

功能要求

- 创建和删除时先检查父节点是否存在，若不存在，抛出异常
- 跟zk连接时进行三次重试

```java
    public boolean createNode(String path, String curNode, Object data) throws InterruptedException {
        curNode = adjustmentNodePathUtil(curNode);
        String curNodePath = path + curNode;
        if(!zkClient.exists(path)){
            throw new RuntimeException("Parent node "+ path +" does not exist");
        }
        Map<String, Object> paramMap = new HashMap<String, Object>();
        paramMap.put("curNodePath", curNodePath);
        paramMap.put("data", data);
        RetryUtil.RetryResult<Object> result = RetryUtil.executeWithRetry(new RetryUtil.RetryCallback<Object, Map<String, Object>>() {
            public Object call(Map<String, Object> param) throws Exception {
                try{
                    zkClient.createPersistent(param.get("curNodePath").toString());
                }catch (Exception e){
                    throw e;
                }
                return true;
            }
        }, paramMap);
        return result.getSuccessState();
    }
```

​    创建节点时先检查父节点是否存在，若不存在则报错。这里最好写一个业务报错，方便使用者对异常进行处理，根据自己需要处理报错，比如创建父节点后重试。

​    在创建节点时进行了多次重试。由于重试是个通用代码，所以我把它写到了另一个类里，并新建了RetryResult用来封装重试结果。

```java
    public static <T,P> RetryResult<T> executeWithRetry(RetryCallback<T,P> callback, P param) throws InterruptedException {
        int retryCount = 3;
        Exception lastException = null;
        for(int i = 0; i < retryCount; i++){
            try{
                T result = callback.call(param);
                return RetryResult.success(result);
            }catch(Exception e){
                lastException = e;
                Thread.sleep(1000);
            }
        }

        return RetryResult.failure(lastException);
    }
```

​    这段代码的使用者仅需在调用时实现RetryCallback接口即可。

​    删除节点代码类似，不再重复贴出。

### 3. 注册监听器

功能要求

- 对拓展开放，只需实现接口即可实现新的监听
- 无需重复注册监听器

```java
    private void registeListener(String path, String handlerClass){
        try{
            IZkDataListener listener = (IZkDataListener)Class.forName(handlerClass).newInstance();
            String absPath = prefixNode + adjustmentNodePathUtil(path);
            zkClient.subscribeDataChanges(absPath, listener);
            listenerMap.put(path, listener);
        }catch (ClassNotFoundException | InstantiationException | IllegalAccessException e1){
            e1.printStackTrace();
        }
    }
```

   监听注册逻辑。代码通过反射找到IZkDataListener的实现类，一一生成实例并注册。监听器监听的key由ZookeeperConfig配置，可从配置文件中读取。

  如果需要新增注册器，只需新增一个类，对IZkDataListener进行实现。

```java
public class PrintListener implements IZkDataListener {
    public void handleDataChange(String s, Object o) throws Exception {
        System.out.println(o.toString());
    }

    public void handleDataDeleted(String s) throws Exception {
        System.out.println("delete: " + s);
    }
}
```

##### 为什么这里监听器只需要注册一次

Zookeeper的watcher是一次触发即失效，这里使用了ZkClient包，封装了监听器，当变更触发以后会自动重新注册。

### Others

​    Java里的Zookeeper客户端有ZkClient和Curator，这里仅使用了ZkClient，它仅对Zookeeper客户端进行了简单的封装，如失败重连，自动重注册watcher等。从网上资料看，Curator是功能更齐全的包，留待以后研究。
