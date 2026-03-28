---
title: Collection类源码阅读
date: 2024-08-10 19:36:44
permalink: 2024/08/10/20240810-Collection类源码阅读/
banner_img: /img/20240810-Collection类源码阅读.jpg
tags:
  - java
  - source-code
  - collection
categories: Java
---

## 一. 前言

​    最近想要阅读一些源码，所以决定从java基础包开始读起，逐渐向外拓展。

​    Collection类作为面试大头，在日常工作中又非常常用，自然就成为了我的首选。但我在阅读时发现，选择它作为第一个阅读的源码包其实不是很合适，原因如下：

​    \1. Collection类并不是一次写就的，中间经过多次修改，每一代人修改时想法不尽相同，所以读者在阅读时就会迷惑，为什么这里用了这种概念，那里却并没有？

​    \2. 源码的阅读应该重整体轻细节，但对于一个我们熟悉又了解得不全面的包来说，很容易陷入细节无法自拔，问就是HashMap如何扩容，Hash冲突怎么办，更不容易获得全局视野。这大概是（有点）知识（又不多）的诅咒。

​    \3. Collection本身也不够整体，边界很难划分。我们常说Collection及其子类，但其实日常里会把Map类也放进这个分类，把本应是子类的Vector排除出去。这常常让人迷惑。我个人认为，utils包中承载了容器功能的类都在本次讨论范围内，至于好用不好用，建不建议使用，那是后话。

​    \4. 我个人的困惑。Collection本身的范围是有限的，但在很多常用包中使用了它，做了详尽的拓展。克制自己去了解这些东西的欲望，也很难的。

​    另外，在本次源码阅读中，除了泛泛而谈了解一下包结构 、每个Collection的扩容方式、底层结构，我也会关注Iterable接口、关注序列化与反序列化、方法抛出的异常、排序如何实现，种种问题。



## 二. 整体结构

我在此将Collection类分为两个部分，一个部分是接口，接口其实是一种分类，每个实现类都有多个不同标签，Collection的分类又相对比较错乱。另一个部分是具体实现类，如我们常讲的ArrayList、LinkedList，它们才具体实现了方法。

### 2.1 Interface Structure

![](/img/20240810-Collection类源码阅读/01.jpg)

图示为Collection类相关接口，所有的实现类都是从这几个接口衍生出来的。



### 2.2 Implement Structure

![](/img/20240810-Collection类源码阅读/02.jpg)

图中黄色标记为utils包里所有的实现类，有一些热门实现类，还有冷门实现类。另外，既然实现类都要实现通用功能，让每个实现类自己重写一次也是非常不划算的，因此Collection里多个很多抽象类来做这件事。



### 2.3 Abstract Implement Structure

![](/img/20240810-Collection类源码阅读/03.jpg)

图中所示为utils包中写的模板方法，实现了基础的方法，让后面实现类可以复用代码，减少工作量。



## 三. 从上至下分析-例子: ArrayList

我们的分析从上至下，选取一条路径。为举例方便，选择了ArrayList这个最简单最通用的实现类。



### 3.1 Iterable接口分析

从Collection接口开始，就不得不面对Iterable接口。Iterable接口标记这个类可以使用foreach语法。主要应用在collection类中。它只有两个方法。

#### 3.1.1 iterator

获取这个类的Iterator迭代器

#### 3.1.2 forEach

将待执行代码段作为参数传递进去，对这个类的每一个对象执行这段代码

#### 3.1.3 spliterator（没有研究明白）

获取一个可分割的迭代器。

### 3.2 Collection接口分析

#### 3.2.1 基础方法

如size, isEmpty, add, remove, contains，都是需要实现的基础方法

#### 3.2.2 引入Iteratable的方法

略。

#### 3.2.3 lambda表达式以后的方法

removeIf(Predicate)

当满足Predicate的时候，执行remove方法

### 3.3 AbstractCollection实现了什么

提供一个最小实现。

若需要实现一个不可变Collection，只需要继承AbstractCollection并实现iterator方法和size方法。AbstractCollection实现了get方法、contain方法、isEmpty、toArray。

若要实现一个可变Collection，需要实现add和remove。AbstractCollection还实现了addAll, removeAll、retainAll、clear。

### 3.4 List接口加了什么东西

对迭代器(iterator)、添加(add)、删除(remove)、equals及hashCode方法提出了更进一步的要求。

Collection中的add:

```java
    // Modification Operations

    /**
     * Ensures that this collection contains the specified element (optional
     * operation).  Returns {@code true} if this collection changed as a
     * result of the call.  (Returns {@code false} if this collection does
     * not permit duplicates and already contains the specified element.)<p>
     *
     * Collections that support this operation may place limitations on what
     * elements may be added to this collection.  In particular, some
     * collections will refuse to add {@code null} elements, and others will
     * impose restrictions on the type of elements that may be added.
     * Collection classes should clearly specify in their documentation any
     * restrictions on what elements may be added.<p>
     *
     * If a collection refuses to add a particular element for any reason
     * other than that it already contains the element, it <i>must</i> throw
     * an exception (rather than returning {@code false}).  This preserves
     * the invariant that a collection always contains the specified element
     * after this call returns.
     *
     * @param e element whose presence in this collection is to be ensured
     * @return {@code true} if this collection changed as a result of the
     *         call
     * @throws UnsupportedOperationException if the {@code add} operation
     *         is not supported by this collection
     * @throws ClassCastException if the class of the specified element
     *         prevents it from being added to this collection
     * @throws NullPointerException if the specified element is null and this
     *         collection does not permit null elements
     * @throws IllegalArgumentException if some property of the element
     *         prevents it from being added to this collection
     * @throws IllegalStateException if the element cannot be added at this
     *         time due to insertion restrictions
     */
```

List中的add:

```java
    /**
     * Appends the specified element to the end of this list (optional
     * operation).
     *
     * <p>Lists that support this operation may place limitations on what
     * elements may be added to this list.  In particular, some
     * lists will refuse to add null elements, and others will impose
     * restrictions on the type of elements that may be added.  List
     * classes should clearly specify in their documentation any restrictions
     * on what elements may be added.
     *
     * @param e element to be appended to this list
     * @return {@code true} (as specified by {@link Collection#add})
     * @throws UnsupportedOperationException if the {@code add} operation
     *         is not supported by this list
     * @throws ClassCastException if the class of the specified element
     *         prevents it from being added to this list
     * @throws NullPointerException if the specified element is null and this
     *         list does not permit null elements
     * @throws IllegalArgumentException if some property of this element
     *         prevents it from being added to this list
     */
```



感觉也没有做强制限制。

### 3.5 AbstractList实现了什么——如果我要自定义一个List，我还需要实现哪些方法

在AbstractList中，未实现add和remove方法。这也许是为imutableCollection考虑。

实现get和size方法，就可以实现一个不可变List。

再实现add, remove方法，就可以实现一个可变List。



举个例子，org.apache.commons.collections有个TreeList，我们可以分析一下它实现了什么方法



1. 如果要实现不可变List，首先需要实现get和size方法。这两个是读方法

```java
    /**
     * Gets the element at the specified index.
     * 
     * @param index  the index to retrieve
     * @return the element at the specified index
     */
    public Object get(int index) {
        checkInterval(index, 0, size() - 1);
        return root.get(index).getValue();
    }

    /**
     * Gets the current size of the list.
     * 
     * @return the current size
     */
    public int size() {
        return size;
    }
```



1. 这个TreeList实际是可变List，所以还需实现add和remove

```java
    /**
     * Sets the element at the specified index.
     * 
     * @param index  the index to set
     * @param obj  the object to store at the specified index
     * @return the previous object at that index
     * @throws IndexOutOfBoundsException if the index is invalid
     */
    public Object set(int index, Object obj) {
        checkInterval(index, 0, size() - 1);
        AVLNode node = root.get(index);
        Object result = node.value;
        node.setValue(obj);
        return result;
    }

    /**
     * Removes the element at the specified index.
     * 
     * @param index  the index to remove
     * @return the previous object at that index
     */
    public Object remove(int index) {
        modCount++;
        checkInterval(index, 0, size() - 1);
        Object result = get(index);
        root = root.remove(index);
        size--;
        return result;
    }
```



1. 到以上为止，其实一个基本的List功能已经实现了。但这个TreeList比较特殊，内部有一些特殊的结构改造，因此开发者还重写了其他方法。如，对每个传入index的方法都增加测checkInterval方法

```java
    /**
     * Checks whether the index is valid.
     * 
     * @param index  the index to check
     * @param startIndex  the first allowed index
     * @param endIndex  the last allowed index
     * @throws IndexOutOfBoundsException if the index is invalid
     */
    private void checkInterval(int index, int startIndex, int endIndex) {
        if (index < startIndex || index > endIndex) {
            throw new IndexOutOfBoundsException("Invalid index:" + index + ", size=" + size());
        }
    }
```



### 3.6 ArrayList内部结构

ArrayList就成为了我们最优先选择的例子。

ArrayList底层是一个数组。Collection的所有类，都需要一个底层实现来存放参数，所以我们先来关注这个实现。

```java
    /**
     * The array buffer into which the elements of the ArrayList are stored.
     * The capacity of the ArrayList is the length of this array buffer. Any
     * empty ArrayList with elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA
     * will be expanded to DEFAULT_CAPACITY when the first element is added.
     */
    transient Object[] elementData; // non-private to simplify nested class access
```



#### 3.6.1 数组的初始化

这个数组的初始化有三个方法，要么使用默认参数指定初始大小，要么使用传入的参数指定大小。

```java
    /**
     * Constructs an empty list with the specified initial capacity.
     *
     * @param  initialCapacity  the initial capacity of the list
     * @throws IllegalArgumentException if the specified initial capacity
     *         is negative
     */
    public ArrayList(int initialCapacity) {
        if (initialCapacity > 0) {
            this.elementData = new Object[initialCapacity];
        } else if (initialCapacity == 0) {
            this.elementData = EMPTY_ELEMENTDATA;
        } else {
            throw new IllegalArgumentException("Illegal Capacity: "+
                                               initialCapacity);
        }
    }

    /**
     * Constructs an empty list with an initial capacity of ten.
     */
    public ArrayList() {
        this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
    }

    /**
     * Constructs a list containing the elements of the specified
     * collection, in the order they are returned by the collection's
     * iterator.
     *
     * @param c the collection whose elements are to be placed into this list
     * @throws NullPointerException if the specified collection is null
     */
    public ArrayList(Collection<? extends E> c) {
        Object[] a = c.toArray();
        if ((size = a.length) != 0) {
            if (c.getClass() == ArrayList.class) {
                elementData = a;
            } else {
                elementData = Arrays.copyOf(a, size, Object[].class);
            }
        } else {
            // replace with empty array.
            elementData = EMPTY_ELEMENTDATA;
        }
    }
```



#### 3.6.2 方法的扩容

该方法提供了一个grow方法来进行扩容，对于add每次容量增加1

```java
    /**
     * This helper method split out from add(E) to keep method
     * bytecode size under 35 (the -XX:MaxInlineSize default value),
     * which helps when add(E) is called in a C1-compiled loop.
     */
    private void add(E e, Object[] elementData, int s) {
        if (s == elementData.length)
            elementData = grow();
        elementData[s] = e;
        size = s + 1;
    }

    /**
     * Appends the specified element to the end of this list.
     *
     * @param e element to be appended to this list
     * @return {@code true} (as specified by {@link Collection#add})
     */
    public boolean add(E e) {
        modCount++;
        add(e, elementData, size);
        return true;
    }
```

对于addAll，添加多少就分配多少

```java
    /**
     * Appends all of the elements in the specified collection to the end of
     * this list, in the order that they are returned by the
     * specified collection's Iterator.  The behavior of this operation is
     * undefined if the specified collection is modified while the operation
     * is in progress.  (This implies that the behavior of this call is
     * undefined if the specified collection is this list, and this
     * list is nonempty.)
     *
     * @param c collection containing elements to be added to this list
     * @return {@code true} if this list changed as a result of the call
     * @throws NullPointerException if the specified collection is null
     */
    public boolean addAll(Collection<? extends E> c) {
        Object[] a = c.toArray();
        modCount++;
        int numNew = a.length;
        if (numNew == 0)
            return false;
        Object[] elementData;
        final int s;
        if (numNew > (elementData = this.elementData).length - (s = size))
            elementData = grow(s + numNew);
        System.arraycopy(a, 0, elementData, s, numNew);
        size = s + numNew;
        return true;
    }

    /**
     * Inserts all of the elements in the specified collection into this
     * list, starting at the specified position.  Shifts the element
     * currently at that position (if any) and any subsequent elements to
     * the right (increases their indices).  The new elements will appear
     * in the list in the order that they are returned by the
     * specified collection's iterator.
     *
     * @param index index at which to insert the first element from the
     *              specified collection
     * @param c collection containing elements to be added to this list
     * @return {@code true} if this list changed as a result of the call
     * @throws IndexOutOfBoundsException {@inheritDoc}
     * @throws NullPointerException if the specified collection is null
     */
    public boolean addAll(int index, Collection<? extends E> c) {
        rangeCheckForAdd(index);

        Object[] a = c.toArray();
        modCount++;
        int numNew = a.length;
        if (numNew == 0)
            return false;
        Object[] elementData;
        final int s;
        if (numNew > (elementData = this.elementData).length - (s = size))
            elementData = grow(s + numNew);

        int numMoved = s - index;
        if (numMoved > 0)
            System.arraycopy(elementData, index,
                             elementData, index + numNew,
                             numMoved);
        System.arraycopy(a, 0, elementData, index, numNew);
        size = s + numNew;
        return true;
    }
```

接下来看看grow方法，它会新建Array，再将数据插入进去。所以对性能消耗是很大的。

```java
    /**
     * Increases the capacity to ensure that it can hold at least the
     * number of elements specified by the minimum capacity argument.
     *
     * @param minCapacity the desired minimum capacity
     * @throws OutOfMemoryError if minCapacity is less than zero
     */
    private Object[] grow(int minCapacity) {
        return elementData = Arrays.copyOf(elementData,
                                           newCapacity(minCapacity));
    }

    private Object[] grow() {
        return grow(size + 1);
    }
```

可以写个单测了解一下它们的插入时间

```java
    @Test
    public void velocityTest(){
        ArrayList<Integer> list1 = new ArrayList<>();

        Long startTime1 = System.currentTimeMillis();
        for(int i = 0; i < 60000; i++){
            list1.add(i);
        }
        Long endTime1 = System.currentTimeMillis();

        ArrayList<Integer> list2 = new ArrayList<>(60000);

        Long startTime2 = System.currentTimeMillis();
        for(int i = 0; i < 60000; i++){
            list2.add(i);
        }
        Long endTime2 = System.currentTimeMillis();

        System.out.println("list1插入耗时 " + (endTime1 - startTime1) + " 毫秒");
        System.out.println("list2插入耗时 " + (endTime2 - startTime2) + " 毫秒");
    }
```

输出：

```java
list1插入耗时 6 毫秒
list2插入耗时 3 毫秒

Process finished with exit code 0
```



#### 3.6.3 方法的移除，但并不收缩容量

快速收缩，复制数组，并将最后一个值设为null。并不改变底层数组的大小

```java
/**
 * Private remove method that skips bounds checking and does not
 * return the value removed.
 */
private void fastRemove(Object[] es, int i) {
    modCount++;
    final int newSize;
    if ((newSize = size - 1) > i)
        System.arraycopy(es, i + 1, es, i, newSize - i);
    es[size = newSize] = null;
}
```



### 3.7 ArrayList之外的拓展

如果你想写一个新的东西，会顺序增长，那就可以使用ArrayList来处理。每次新增或修改都拷贝一个新的数组过去，不用对内部数据进行处理。

另外，查询时，也可以根据时间ArrayList来做random access，使用二分查找。



## 四. 一些特征类

### 4.1 ArrayDeque为代表的Deque

#### 4.1.1. Deque为何需要transient?

ArrayDeque中使用transient关键字的主要原因有以下几点:



1.  ArrayDeque内部使用数组来存储元素,数组长度是动态变化的。如果直接序列化数组可能会产生问题。 
2.  使用transient修饰数组成员,可以避免数组本身被序列化,而只序列化数组中的元素。 
3.  反序列化时,会重新创建动态数组,长度根据元素数量自动调整。这样可以保证恢复到最新的状态。 
4.  不使用transient的话,反序列化得到的数组可能因为长度修改而无法放得下元素,或者因为空间浪费。 
5.  另外,ArrayDeque内部还有一些指针成员标记位置,如head和tail。如果这些指针也被序列化,无法正确反映最新状态。 
6.  用transient可以避免这些指针指向被序列化后的无效对象位置。 



总之,ArrayDeque作为一个长度动态变化的结构,直接序列化底层数组有一定问题。使用transient可以排除结构性信息,只序列化有效元素,更高效地实现序列化与反序列化。



#### 4.1.2. 头插和尾插

ArrayDeque在使用AddFirst, AddLast的时候，会使用dec方法循环递减head索引,以求得正确的队头位置



#### 4.1.3. Remove

计算前移和后移哪个更划算，然后移动

```java
/**
     * Removes the element at the specified position in the elements array.
     * This can result in forward or backwards motion of array elements.
     * We optimize for least element motion.
     *
     * <p>This method is called delete rather than remove to emphasize
     * that its semantics differ from those of {@link List#remove(int)}.
     *
     * @return true if elements near tail moved backwards
     */
boolean delete(int i) {
final Object[] es = elements;
final int capacity = es.length;
final int h, t;
// number of elements before to-be-deleted elt
final int front = sub(i, h = head, capacity);
// number of elements after to-be-deleted elt
final int back = sub(t = tail, i, capacity) - 1;
if (front < back) {
    // move front elements forwards
    if (h <= i) {
        System.arraycopy(es, h, es, h + 1, front);
    } else { // Wrap around
        System.arraycopy(es, 0, es, 1, i);
        es[0] = es[capacity - 1];
        System.arraycopy(es, h, es, h + 1, front - (i + 1));
    }
    es[h] = null;
    head = inc(h, capacity);
    return false;
} else {
    // move back elements backwards
    tail = dec(t, capacity);
    if (i <= tail) {
        System.arraycopy(es, i + 1, es, i, back);
    } else { // Wrap around
        System.arraycopy(es, i + 1, es, i, capacity - (i + 1));
        es[capacity - 1] = es[0];
        System.arraycopy(es, 1, es, 0, t - 1);
    }
    es[tail] = null;
    return true;
}
}
```



### 4.2 LinkedList

linkedList在常规方法外，没有底层数据，因此在处理很多操作时需要先判定位置是否越界。判定方法就是这两个。

```java
    /**
     * Tells if the argument is the index of an existing element.
     */
    private boolean isElementIndex(int index) {
        return index >= 0 && index < size;
    }

    /**
     * Tells if the argument is the index of a valid position for an
     * iterator or an add operation.
     */
    private boolean isPositionIndex(int index) {
        return index >= 0 && index <= size;
    }

    /**
     * Constructs an IndexOutOfBoundsException detail message.
     * Of the many possible refactorings of the error handling code,
     * this "outlining" performs best with both server and client VMs.
     */
    private String outOfBoundsMsg(int index) {
        return "Index: "+index+", Size: "+size;
    }
```



链表提供了序列化和反序列化方法，只需要序列化其中的元素和元素的顺序，而不需要序列化每个节点的next和prev字段。不过我没找到在哪里用的……

```java
    /**
     * Saves the state of this {@code LinkedList} instance to a stream
     * (that is, serializes it).
     *
     * @serialData The size of the list (the number of elements it
     *             contains) is emitted (int), followed by all of its
     *             elements (each an Object) in the proper order.
     */
    private void writeObject(java.io.ObjectOutputStream s)
        throws java.io.IOException {
        // Write out any hidden serialization magic
        s.defaultWriteObject();

        // Write out size
        s.writeInt(size);

        // Write out all elements in the proper order.
        for (Node<E> x = first; x != null; x = x.next)
            s.writeObject(x.item);
    }

    /**
     * Reconstitutes this {@code LinkedList} instance from a stream
     * (that is, deserializes it).
     */
    @SuppressWarnings("unchecked")
    private void readObject(java.io.ObjectInputStream s)
        throws java.io.IOException, ClassNotFoundException {
        // Read in any hidden serialization magic
        s.defaultReadObject();

        // Read in size
        int size = s.readInt();

        // Read in all elements in the proper order.
        for (int i = 0; i < size; i++)
            linkLast((E)s.readObject());
    }
```



### 4.3 PriorityQueue

PriorityQueue在各个系统中的实现方法各不相同，但它们的特点是固定的。有序，方便取出。如果你想的数据是抽牌，随时抽出一张新的数字，就可以按PriorityQueue，它的排序很快。



### 4.4 虽然不在Collection包里，但Map也是重要的组成部份
