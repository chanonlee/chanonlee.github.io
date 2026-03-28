---
title: 关于equals和hashcode方法
date: 2024-02-05 00:59:54
permalink: 2024/02/05/关于equals和hashcode方法/
banner_img: /img/20240205-关于equals和hashcode方法.jpg
tags:
  - java
  - equals
  - hashcode
categories: Java
---

equals用于判断两个对象是否是同一个

hashcode用来快速判断对象是否相同（对象相同hashcode一定相同），还用于hashMap里的处理

### 1. Object类中的方法

#### 1.1. hashcode

调用native方法，在一定程度上返回内存地址。

```java
    public native int hashCode();
```

#### 1.2. equals方法

比较两个对象是否是同一个

```java
    public boolean equals(Object obj) {
        return (this == obj);
    }
```



### 2. String类中的方法

#### 2.1. hashcode方法

根据char数组计算出一个值

```java
    public int hashCode() {
        int h = hash;
        if (h == 0 && value.length > 0) {
            char val[] = value;

            for (int i = 0; i < value.length; i++) {
                h = 31 * h + val[i];
            }
            hash = h;
        }
        return h;
    }
```

#### 2.2. equals方法

比较两个char数组是否一致

```java
public boolean equals(Object anObject) {
if (this == anObject) {
    return true;
}
if (anObject instanceof String) {
    String anotherString = (String)anObject;
    int n = value.length;
    if (n == anotherString.value.length) {
        char v1[] = value;
        char v2[] = anotherString.value;
        int i = 0;
        while (n-- != 0) {
            if (v1[i] != v2[i])
                return false;
            i++;
        }
        return true;
    }
}
return false;
}
```

注意，Object是无法获知String类型的，所以这个方法的入参是Object，在方法内再强制转换为String类。

#### 2.3. 如果重写equals，但不重写hashcode方法？

当char数组相同时，equals就会返回true。但此时的字符串未必指向同一个块内存，hashcode值可能不相同。在使用hashmap存储时，两个同样的string字符串就可能被放入不同的桶中。



### 3. HashMap中Node的节点方法

#### 3.1. hashcode方法

对key和value的hashcode求异或

```java
    static class Node<K,V> implements Map.Entry<K,V> {
        ……
	    public final int hashCode() {
            return Objects.hashCode(key) ^ Objects.hashCode(value);
        }
        ……
    }
```

#### 3.2. equals方法

```java
    static class Node<K,V> implements Map.Entry<K,V> {
        ……
        public final boolean equals(Object o) {
            if (o == this)
                return true;
            if (o instanceof Map.Entry) {
                Map.Entry<?,?> e = (Map.Entry<?,?>)o;
                if (Objects.equals(key, e.getKey()) &&
                    Objects.equals(value, e.getValue()))
                    return true;
            }
            return false;
        }
        ……
    }
```

比较key是否equals，value是否equals。

注意，这里调用到Objects类的子类重写方法。

### 4. UUID中的方法

#### 4.1. hashcode方法

UUID是128位值，但hashcode只有32位。这里把UUID分成高64位和低64位，将高低都纳入计算。

hilo是高位异或低位。hito右移32位后截断，然后跟hilo本身异或，也就是拿它自己的左右两边异或，得到一个32位字节。

```java
    public int hashCode() {
        long hilo = mostSigBits ^ leastSigBits;
        return ((int)(hilo >> 32)) ^ (int) hilo;
    }
```



#### 4.2. equals方法

高64位与低64位相同。

```java
    public boolean equals(Object obj) {
        if ((null == obj) || (obj.getClass() != UUID.class))
            return false;
        UUID id = (UUID)obj;
        return (mostSigBits == id.mostSigBits &&
                leastSigBits == id.leastSigBits);
    }
```

#### 4.3. nameUUIDFromBytes

根据输入的字节数组生成uuid，使用md5算法，跟hashcode无关。

```java
public static UUID nameUUIDFromBytes(byte[] name) {
    MessageDigest md;
    try {
        md = MessageDigest.getInstance("MD5");
    } catch (NoSuchAlgorithmException nsae) {
        throw new InternalError("MD5 not supported", nsae);
    }
    byte[] md5Bytes = md.digest(name);
    md5Bytes[6]  &= 0x0f;  /* clear version        */
    md5Bytes[6]  |= 0x30;  /* set to version 3     */
    md5Bytes[8]  &= 0x3f;  /* clear variant        */
    md5Bytes[8]  |= 0x80;  /* set to IETF variant  */
    return new UUID(md5Bytes);
```
