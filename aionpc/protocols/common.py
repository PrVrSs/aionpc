import math


def checksum(buffer: bytes) -> int:
    sum_ = 0
    count_to = (len(buffer) / 2) * 2
    count = 0

    while count < count_to:
        this_val = buffer[count + 1] * 256 + buffer[count]
        sum_ += this_val
        sum_ &= 0xffffffff
        count += 2

    if count_to < len(buffer):
        sum_ += buffer[len(buffer) - 1]
        sum_ &= 0xffffffff

    sum_ = (sum_ >> 16) + (sum_ & 0xffff)
    sum_ += sum_ >> 16
    answer = ~sum_
    answer &= 0xffff

    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def mdev(iterator):
    return math.sqrt(
        sum(i * i for i in iterator) / len(iterator)
        -
        pow(sum(iterator) / len(iterator), 2)
    )
