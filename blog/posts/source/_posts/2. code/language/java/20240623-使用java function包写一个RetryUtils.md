---
title: 使用 java function 包写一个 RetryUtils
date: 2024-06-23 09:08:16
permalink: 2024/06/23/20240623-使用java function包写一个RetryUtils/
banner_img: /img/20240623-使用java function包写一个RetryUtils.jpg
tags:
  - java
  - function
  - retry
categories: 工程实践
---
<div style="font-size: 0.9em; color: #8a8a8a; line-height: 1.7;">

**创作透明度：** 🖋️ 人工创作（完全作者撰写） | ✨ AI润色（作者撰写，AI优化语言） | 🤖 AI辅助（作者主导，AI提供内容/结构建议） | 🛠️ AI+人工（AI生成初稿，作者修改完善） | 🧠 全AI生成（内容完全由AI生成）

**本文标注： 🖋️ 人工创作**

</div>


在项目中，我们总会遇到很多需要重复执行的代码。为了方便，将重复执行抽象成工具类，提供三种功能

1. 直接重试
2. 重试并获取结果
3. 在指定条件下重试并获取结果



使用方式可以参考测试类。不需要引入额外的依赖。



# 1. 工具类本身

```java
import java.util.function.Predicate;

public class RetryUtils {

    /**
     * retry without result
     * @param runnable a block of executable code
     * @param maxRetryCount max retry count
     * @param delayMillis sleep between each retry
     * @throws Exception throws exception when retry failed
     */
    public static void retry(ThrowableRunnable runnable, int maxRetryCount, long delayMillis) throws Exception {
        Exception exception = null;
        for (int i = 0; i < maxRetryCount; i++) {
            try {
                runnable.run();
                return;
            } catch (Exception e) {
                exception = e;
                try {
                    Thread.sleep(delayMillis);
                } catch (InterruptedException e1) {
                    throw e1;
                }
            }
        }
        throw exception;
    }

    public interface ThrowableRunnable {
        void run() throws Exception;
    }

    /**
     * Executes a given block of code with result support, allowing for retries upon failure.
     *
     * This method will repeatedly execute the provided {@code callable} until it succeeds or
     * until the maximum retry count is reached. If the maximum retry count is reached without
     * success, an exception will be thrown.
     *
     * @param callable A block of executable code that returns a result. It should implement
     *                 the logic that may need to be retried in case of failure.
     * @param maxRetryCount The maximum number of times to retry the execution of the callable.
     *
     * @param delayMillis The delay time in milliseconds to wait before retrying the callable.
     *                    This delay occurs after a failed attempt and before the next retry.
     * @param <T> The type of the result returned by the callable.
     * @return The result returned by the callable if the operation was successful within the
     *         allowed number of retries.
     * @throws Exception If the callable fails and the maximum number of retries has been
     *                   exhausted, an exception is thrown to indicate the failure.
     */
    public static <T> T retryReturn(ThrowableCallable<T> callable,
                                    int maxRetryCount, long delayMillis) throws Exception {

        Exception exception = null;

        for(int i = 0; i < maxRetryCount; i++) {

            try {
                return callable.call();
            } catch (Exception e) {
                exception = e;

                try {
                    Thread.sleep(delayMillis);
                } catch (InterruptedException ex) {
                    throw ex;
                }

            }

        }

        throw exception;
    }

    public interface ThrowableCallable<T> {
        T call() throws Exception;
    }

    /**
     * Executes a given block of code with result support, allowing for retries upon failure based on a custom condition.
     *
     * This method will repeatedly execute the provided {@code callable} until it succeeds and meets the retry condition,
     * or until the maximum retry count is reached. The retry condition is checked against the result of the callable.
     * If the maximum retry count is reached without meeting the condition, an exception will be thrown.
     *
     * @param callable A block of executable code that returns a result. It should implement
     *                 the logic that may need to be retried in case of failure or until a condition is met.
     * @param maxRetryCount The maximum number of times to retry the execution of the callable.
     * @param delayMillis The delay time in milliseconds to wait before retrying the callable.
     *                    This delay occurs after a failed attempt or when the retry condition is not met.
     * @param retryCondition A predicate that defines the condition under which the callable's result
     *                       should be considered for retry. The callable will be retried if this predicate
     *                       returns TRUE for the result.
     * @param <T> The type of the result returned by the callable.
     * @return The result returned by the callable if the operation was successful and the retry condition was met.
     * @throws Exception If the callable fails and the maximum number of retries has been exhausted,
     *                   or if the retry condition is never met, an exception is thrown to indicate the failure.
     */
    public static <T> T retryReturn(ThrowableCallable<T> callable,
                                    int maxRetryCount, long delayMillis,
                                    Predicate<T> retryCondition) throws Exception {

        for(int i = 0; i < maxRetryCount; i++) {

            try {
                T result = callable.call();

                if(retryCondition.test(result)) {
                    continue;
                }

                return result;

            } catch (Exception e) {
                // 重试
            }

        }

        throw new RuntimeException("Retry failed!");
    }

    public static <T> Predicate<BaseResult<T>> createRetryPredicate() {
        return new BaseResultPredict<T>();
    }

    public static class BaseResultPredict<T> implements Predicate<BaseResult<T>> {

        @Override
        public boolean test(BaseResult<T> baseResult) {

            // 1. 判断baseResult是否为空
            if(baseResult == null) {
                return true;
            }

            // 2. 判断状态码是否为200
            int code = baseResult.getCode();
            if(baseResult.isFail()) {
                return true;
            }

            // 所有条件通过,不需要重试
            return false;
        }

    }
}
```



# 2. 测试代码

```java
import org.junit.Test;

import java.util.function.Predicate;

import static org.junit.Assert.*;

public class RetryUtilsTest {

    private static int counter = 0;

    @Test
    public void testRetry_success() throws Exception {
        counter = 0;
        // 成功调用次数
        int expectedCount = 1;

        RetryUtils.retry(() -> {
            counter++;
        }, 3, 100);

        assertEquals(expectedCount, counter);
    }

    @Test
    public void testRetry_retry_success() throws Exception {
        counter = 0;

        // 总调用次数
        int expectedCount = 3;

        RetryUtils.retry(() -> {
            counter++;
            if(counter < 3) {
                throw new Exception("test");
            }
        }, 3, 100);

        assertEquals(expectedCount, counter);
    }

    @Test
    public void testRetry_fail() throws Exception {
        counter = 0;

        // 总调用次数
        int expectedCount = 3;

        assertThrows(Exception.class, () -> {
            RetryUtils.retry(() -> {
                counter++;
                if (counter < 4) {
                    throw new Exception("test");
                }
            }, 3, 100);
        });
        assertEquals(expectedCount, counter);
    }

    @Test
    public void testRetryReturn_success() throws Exception {

        String result = RetryUtils.retryReturn(() -> {
            return "success";
        }, 3, 100);

        assertEquals("success", result);
    }

    @Test
    public void testRetryReturn_fail() throws Exception {
        counter = 0;

        assertThrows(Exception.class, () -> {
            RetryUtils.retryReturn(() -> {
                counter++;
                if(counter < 5) {
                    throw new RuntimeException("test");
                }
                return "success";
            }, 3, 100);
        });

        assertEquals(3, counter);

    }

    @Test
    public void testRetryReturn_withPredicate_retry_success() throws Exception {
        counter = 0;

        String result = RetryUtils.retryReturn(() -> {
            counter++;
            if(counter <= 1) {
                return "failed";
            }
            return "success";
        }, 2, 100, r->{
            if(r.equals("failed")) return true;
            return false;
        });

        assertEquals("success", result);
        assertEquals(2, counter);

    }

    @Test
    public void testRetryReturn_withPredicate_retry_fail(){
        counter = 0;

        assertThrows(Exception.class, () -> {
            String result = RetryUtils.retryReturn(() -> {
                counter++;
                if (counter <= 5) {
                    return "failed";
                }
                return "success";
            }, 3, 100, r -> {
                if (r.equals("failed")) return true;
                return false;
            });
        });

        assertEquals(3, counter);

    }

    @Test
    public void testRetryReturn_withBaseResultPredicate_success() throws Exception {
        counter = 0;
        Predicate<BaseResult<Void>> predict = RetryUtils.createRetryPredicate();
        BaseResult<Void> result = RetryUtils.retryReturn(() -> {
            counter++;
            if(counter <= 1) {
                return BaseResult.error("Error message");
            }
            return BaseResult.success();
        }, 3, 100, predict);
    }

    @Test
    public void testRetryReturn_withBaseResultPredicate_fail() throws Exception {
        counter = 0;
        Predicate<BaseResult<Void>> predict = RetryUtils.createRetryPredicate();
        assertThrows(Exception.class, () -> {
            BaseResult<Void> result = RetryUtils.retryReturn(() -> {
            counter++;
            if(counter <= 5) {
                return BaseResult.error("Error message");
            }
            return BaseResult.success();
        }, 3, 100, predict);
        });
        assertEquals(3, counter);
    }

}
```
