---
title: 写一个用zk监听变化的 Kafka Consumer
date: 2023-09-02 22:35:43
permalink: 2023/09/02/20230903-写一个用zk监听变化的kafkaconsumer/
banner_img: /img/230903-写一个用zk监听变化的KafkaConsumer.jpg
tags:
  - java
  - kafka
  - zookeeper
  - consumer
categories: 中间件
description: 实现一个 **Kafka Consumer Manager** 与具体 Consumer，并用 **ZooKeeper 监听变更** 动态调整订阅的 topic。本文给出完整搭建步骤与代码组织方式。
---
<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注： 🖋️ 人工创作**

</div>


功能简介：

1. 写一个kafka consumer manager类
2. 实现一个具体的kafka consumer
3. 注册zk监听器，监听zk变化修改consumer订阅的topic



### 1. 写一个kafka consumer manager类

- kafka consumer manager类，用于管理kafka consumer
- 找到每个消费者，订阅各自主题
- 将任务交给线程池处理
- 设置关闭函数

#### 1.1 kafka consumer manager类，用于管理kafka consumer

```java
    private ConcurrentMap<String, KafkaConsumer<String, KafkaConsumer>> kafkaConsumers;

    @PostConstruct
    @Order(2)
    public void init(){
        if(kafkaConsumers == null){
            kafkaConsumers = new ConcurrentHashMap<>();
            Reflections reflections = new Reflections("src.main.com.channon.util");
            Set<Class<? extends KafkaConsumer>> subTypes = reflections.getSubTypesOf(KafkaConsumer.class);
            subTypes.forEach(clazz -> {
            	KafkaConsumer consumer = clazz.getConstructor(Properties.class).newInstance(kafkaConfig.consumerConfigs());
                // 消费者订阅主题
                // 消费者拉取消息代码交给线程池
                // 设置关闭处理
            });
        }
    }
```

这里创建了一个KafkaConsumerManager类，通过反射获取所有继承了KafkaConsumer的子类，再作处理。

#### 1.2 消费者订阅各自主题

```java
    private void subscribeTopic(Class clazz, KafkaConsumer consumer){
        Set<Map.Entry<String, String>> listener = zookeeperConfig.pathHandlerMap.entrySet();
        boolean configTopic = false;
        for(Map.Entry<String, String> entry:listener){
            if(listener.equals(clazz.getName())){
                configTopic = true;
                consumer.subscribe(Collections.singleton(entry.getKey()));
            }
        }
        if(!configTopic){
            consumer.subscribe(Collections.singleton(kafkaConfig.topic));
        }
    }
```

​    从配置中读取每个消费者对应的主题，如果有单独配置就读取单独配置，如果没有就读取通用配置。这里配置获取方式各有不同，大家可以选择各自的实现方式。唯一需要注意的是， 配置获取的时间应该先于manager init代码运行的时间。

#### 1.3 将任务交给线程池处理

```java
kafkaConsumerPool.addTask(new Runnable() {
    @Override
    public void run() {
        try{
            while(true){
                synchronized (subscribeLock) {
                    ConsumerRecords records = consumer.poll(Duration.ofMillis(1000));
                }
            }
        }catch (WakeupException e){
            e.printStackTrace();
        }finally {
            consumer.close();
        }
    }
});
```

​    设置时间，每个消费者隔一段时间会从kafka里拉取消息，consumer交由线程池管理。

```java
@Component
public class KafkaConsumerPool {
    public static ExecutorService executorService;

    @Autowired
    KafkaConsumerManager kafkaConsumerManager;

    @PostConstruct
    public void start(){
        executorService = Executors.newFixedThreadPool(10);
    }

    public void addTask(Runnable task){
        executorService.submit(task);
    }

    public void close(){
        Map<String, KafkaConsumer<String, KafkaConsumer>> consumers = kafkaConsumerManager.kafkaConsumers();
        for(Map.Entry<String, KafkaConsumer<String, KafkaConsumer>> entry : consumers.entrySet()){
            entry.getValue().wakeup();
        }
        executorService.shutdown();
    }
}
```

​    上面一段是线程池的代码。需要注意的是，kafka consumer是需要一直在后台运行的，所以最好是设置一个固定线程数的线程池，线程数 = 消费者数。

​    线程池关闭的时候会获取所有的消费者，并调用wakeup()。

##### 为什么关闭消费者时调用的是wakeup()而不是close()？

​    wakeup是更轻量也更安全的方法。

​    轻量：它会将client里的wakeup设置为true，kafka在下一次poll数据时就会读取到wakeup设置，并抛出一个WakeUpException。调用线程更改完变量即可退出，无需等待kafka consumer彻底关闭。

​    安全： wakeup会在下次poll之前抛出异常，而close可能打断poll的过程，使得缓存区的该批数据丢失，这批数据可能处于未处理、处理中、已处理未提交位移的状态。

```java
// KafkaConsumer源码
	private ConsumerRecords<K, V> poll(final Timer timer, final boolean includeMetadataInTimeout) {
        acquireAndEnsureOpen();
        try {
            ......
            }

            do {
                client.maybeTriggerWakeup(); // wakeup会在这里抛出异常

                final Fetch<K, V> fetch = pollForFetches(timer);
                if (!fetch.isEmpty()) {
                    ......

                    return this.interceptors.onConsume(new ConsumerRecords<>(fetch.records()));
                }
            } while (timer.notExpired());

            return ConsumerRecords.empty();
        } finally {
            release();
            this.kafkaConsumerMetrics.recordPollEnd(timer.currentTimeMs());
        }
    }

```

#### 1.4 设置关闭函数

在zookeeper util中，我们将关闭函数写在Runtime预留的callback函数里，但这里使用了线程池，所以在线程池中处理关闭即可。

```java
    public void close(){
        Map<String, KafkaConsumer<String, KafkaConsumer>> consumers = kafkaConsumerManager.kafkaConsumers();
        for(Map.Entry<String, KafkaConsumer<String, KafkaConsumer>> entry : consumers.entrySet()){
            entry.getValue().wakeup();
        }
        executorService.shutdown();
    }
```

### 2. 实现一个具体的Kafka Consumer

​    子类继承KafkaConsumer即可。对于我们需要的操作，可以通过重写poll函数来实现

```java
    @Override
    public ConsumerRecords<String, Object> poll(Duration timeout) {

        // call KafkaConsumer.poll() to get messages
        ConsumerRecords<String, Object> records = super.poll(timeout);

        // iterate records, print each message
        for (ConsumerRecord<String, Object> record : records) {
            System.out.printf("Consumed by %s, topic = %s, partition = %d, offset = %d, key = %s, value = %s \n",
                    this.getClass().getName(), record.topic(), record.partition(), record.offset(), record.key(), record.value());
        }

        // return records to user
        return records;
    }
```

​    上文先调用父类的poll函数拉取消息，然后执行我们期望的操作——打印信息，最后返回。

​    之前提到的close可能随时打断这里的任何操作，如执行完了super.poll，但还没有处理，就关闭了。这就会造成数据丢失。

### 3. 注册zk监听器，监听zk变化修改consumer订阅的topic

- 不建议的操作
- zk监听器实现
- 并发问题    

#### 3.1 不建议的操作

我在几次尝试中发现，实时修改kafka consumer订阅的topic是一个非常不好的操作。

1. kafka重平衡消费者导致信息丢失。consumer修改topic对于kafka是个消费者下线再上线的过程，这就回到了经典的kafka重平衡导致数据丢失问题。
2. kakfa consumer不是并发安全的实现。实时修改kafka consumer会遇到非常难处理的并发冲突，如果需要绝对安全又需要加锁，这会拖慢consumer的执行。

   另外，kafka consumer检查到并发冲突后会抛出异常ConcurrentModificationException，需要妥善处理。

​    我在查找网上方案的时候发现大家有两种实现方法，一种是检测到topic变更，直接close消费者再新建，另一种就是加锁。我选择了加锁实现。

#### 3.2 zk监听器实现

​    我们把kafka的topic配置到zookeeper上，写了一个zk listener，当zk node数据变更时就调用kafka consumer变更topic。

```java
public class KafkaPrintTopicListener implements IZkDataListener {

    @Override
    public void handleDataChange(String dataPath, Object data){
        KafkaConsumerManager manager= ApplicationContextUtil.getBean(KafkaConsumerManager.class);
        KafkaConsumer consumer = manager.kafkaConsumers().get(PrintConsumer.class.getName());
        synchronized (subscribeLock){
            consumer.unsubscribe();
            consumer.subscribe(Collections.singleton(data.toString()));
        }
    }

    @Override
    public void handleDataDeleted(String dataPath) throws Exception {

    }
}
```

​     需要注意的是，这个类作为pojo类，需要使用到bean类KafkaConsumerManager，这涉及bean注入的问题。我在这里选择的实现是，创建一个ApplicationContextUtil，使得程序可以在任意地方通过这个Util获取Bean。

```java

public class ApplicationContextUtil {


    private static ApplicationContext context;

    private ApplicationContextUtil() {}

    public static void setApplicationContext(ApplicationContext context) {
        ApplicationContextUtil.context = context;
    }

    public static ApplicationContext getApplicationContext() {
        return context;
    }

    public static <T> T getBean(Class<T> beanClass) {
        return context.getBean(beanClass);
    }

}
```

#### 3.3 并发问题

​    KafkaConsumerManager、KafkaPrintTopicListener和线程池都会对consumer进行更改，而consumer本身是线程不安全的，这里的访问会报错。我的解决方案是，在consumer类中创建一个Object类作为锁对象，对三个地方都加锁。

​    但是这不是一个优良的实现。如果在修改topic时，线程池的poll操作被阻塞，它就没法完成“定时拉取”的任务了。

​    另外，解决这个并发冲突的过程也是很有意思的过程。

```text
如果给两个调用共享变量的地方分别加锁,还是存在并发冲突的可能,原因可能有:
1. 两个地方加的锁对象不一样,需要使用同一对象锁才能起到互斥的效果。  
  check: 打印输出或日志检查,在加锁的地方打印出锁对象的引用,确认是否是同一个对象。引用地址相同，所以是同一个对象。
2. 加锁的范围不够,需要扩大锁的范围,直到包含所有访问共享变量的语句。
  check: 扩大到不能再大了……还是不行
3. 存在死锁情况,一个线程获取锁A等待锁B,另一个线程获取锁B等待锁A,导致互相等待。
  check: 应该不是
4. 有其它线程没有加锁也访问了该共享变量。
  check: 把其中一处代码注释掉再执行，不报错，所以这条排除。后来发现，是一个线程两处调用，另一个线程一处diao'yong
5. 共享变量没有用volatile关键字修饰,导致缓存同步问题。
  check: 没有共享变量，仅访问同一实例
6. 异常情况下,锁没有被正常释放.
  check: synchronized不需要手动释放
7. subscribe后有其它可以修改订阅的方法未加锁,如unsubscribe。
  check: 给所有subscribe和unsubscribe都加了锁，还是不行。后来发现poll方法也需要加锁。
```
