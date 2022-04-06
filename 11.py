x = int(input("请输入："))


def fib(n):
    n1 = 1
    n2 = 1
    for i in range(3, n+1):
        t = n1+n2
        n1 = n2
        n2 = t
    return t


print(fib(x))
